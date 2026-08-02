import asyncio
import json
import logging
import os
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
import httpx
import redis
from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import File, Job, Repo, RepoAnalysis
from app.services.analysis import ArchitectureGenerator, FolderAnalyzer, StackDetector
from app.services.ingestion.service import IngestionService
from app.services.parsing.indexer import SymbolIndexer
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def publish_job_update(job_id: str, stage: str, progress: float, message: str, status: str = "IN_PROGRESS"):
    r = None
    try:
        r = redis.Redis.from_url(settings.REDIS_URL)
        payload = json.dumps({
            "job_id": job_id,
            "stage": stage,
            "progress": progress,
            "message": message,
            "status": status,
        })
        r.publish(f"job_channel:{job_id}", payload)
    except Exception:
        logger.warning("Failed to publish job update for %s", job_id, exc_info=True)
    finally:
        if r:
            try:
                r.close()
            except Exception:
                pass


async def _download_github_zip(github_url: str, dest_dir: Path) -> bool:
    """Fallback method to download GitHub repository as a ZIP archive over HTTP."""
    clean_url = github_url.rstrip("/").replace(".git", "")
    parts = clean_url.split("/")
    if len(parts) < 2:
        return False
    
    owner, repo_name = parts[-2], parts[-1]
    branches = ["main", "master", "dev"]
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
        for branch in branches:
            zip_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"
            try:
                resp = await client.get(zip_url)
                if resp.status_code == 200:
                    zip_path = dest_dir / f"{repo_name}.zip"
                    zip_path.write_bytes(resp.content)
                    
                    extract_dir = dest_dir / "zip_extracted"
                    extract_dir.mkdir(exist_ok=True)
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(extract_dir)
                    
                    # If extracted into a subfolder, copy its contents
                    subdirs = [d for d in extract_dir.iterdir() if d.is_dir()]
                    target_source = subdirs[0] if subdirs else extract_dir
                    
                    for item in target_source.iterdir():
                        dest_item = dest_dir / item.name
                        if item.is_dir():
                            shutil.copytree(item, dest_item, dirs_exist_ok=True)
                        else:
                            shutil.copy2(item, dest_item)
                    return True
            except Exception as ex:
                logger.warning(f"Failed to fetch GitHub zip for branch {branch}: {ex}")
    return False


async def _process_ingest_repo(job_id_str: str, source_type: str, source_input: str):
    job_uuid = uuid.UUID(job_id_str)
    async with AsyncSessionLocal() as session:
        stmt = select(Job).where(Job.id == job_uuid)
        result = await session.execute(stmt)
        job = result.scalar_one_or_none()
        if not job:
            return

        repo_id = job.repo_id

        try:
            # Stage 1: Cloning / Preparing Source
            job.status = "CLONING"
            job.stage = "Fetching repository source"
            job.progress = 15.0
            job.message = f"Retrieving codebase via {source_type}..."
            await session.commit()
            publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

            temp_dir = tempfile.mkdtemp(prefix="devlens_ingest_")
            work_dir = Path(temp_dir)

            try:
                if source_type == "github":
                    clone_success = False
                    try:
                        proc = await asyncio.create_subprocess_exec(
                            "git", "clone", "--depth", "1", source_input, str(work_dir),
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE,
                        )
                        _, stderr_data = await proc.communicate()
                        if proc.returncode == 0:
                            clone_success = True
                    except Exception as ex:
                        logger.warning(f"git clone failed: {ex}, attempting HTTP ZIP fallback...")

                    if not clone_success:
                        # Fallback to direct HTTP ZIP download
                        zip_success = await _download_github_zip(source_input, work_dir)
                        if not zip_success:
                            raise RuntimeError(f"Could not clone or download GitHub repository: {source_input}")

                elif source_type == "zip":
                    zip_path = Path(source_input)
                    if not zip_path.exists():
                        raise RuntimeError(f"ZIP file not found: {source_input}")
                    if not zipfile.is_zipfile(zip_path):
                        raise RuntimeError(f"Invalid ZIP archive: {source_input}")
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        zf.extractall(work_dir)

                elif source_type == "folder":
                    target_path = Path(source_input).resolve()
                    if not target_path.exists():
                        raise RuntimeError(f"Local folder path not found: {source_input}")
                    work_dir = target_path

                # Resolve nested single subfolder if present
                sub_items = [i for i in work_dir.iterdir() if i.is_dir() and not i.name.startswith(".")]
                if len(sub_items) == 1 and not any(i.is_file() for i in work_dir.iterdir()):
                    work_dir = sub_items[0]

                # Stage 2: File Walking & Indexing
                job.status = "WALKING"
                job.stage = "Analyzing file tree and computing hashes"
                job.progress = 50.0
                job.message = "Traversing files, filtering binaries, computing LOC and content hashes..."
                await session.commit()
                publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

                manifest = IngestionService.walk_repository(work_dir)
                if not manifest:
                    raise RuntimeError(f"No source code files found in repository path: {work_dir}")

                # Clear previous file records for re-ingest
                del_stmt = select(File).where(File.repo_id == repo_id)
                existing_files = (await session.execute(del_stmt)).scalars().all()
                for ef in existing_files:
                    await session.delete(ef)

                # Insert new files
                file_models = [
                    File(
                        repo_id=repo_id,
                        path=m["path"],
                        language=m["language"],
                        size_bytes=m["size_bytes"],
                        loc=m["loc"],
                        content_hash=m["content_hash"],
                    )
                    for m in manifest
                ]
                session.add_all(file_models)
                await session.flush()

                # Stage 3: AST Parsing & Symbol Indexing
                job.status = "PARSING"
                job.stage = "Parsing AST symbols & import graph"
                job.progress = 75.0
                job.message = f"Running AST parsers across {len(file_models)} files..."
                await session.commit()
                publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

                total_symbols = 0
                for f_model in file_models:
                    file_path = work_dir / f_model.path
                    if file_path.exists():
                        try:
                            content = file_path.read_text(encoding="utf-8", errors="ignore")
                            count = await SymbolIndexer.index_file(session, f_model, content)
                            total_symbols += count
                        except Exception:
                            pass


                # Stage 4: Vector Embedding → Qdrant (90-second hard cap)
                job.status = "EMBEDDING"
                job.stage = "Embedding code chunks with nomic-embed-text"
                job.progress = 83.0
                job.message = f"Building semantic vector index for {total_symbols} symbols..."
                await session.commit()
                publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

                try:
                    import time as _time
                    from sqlalchemy import select as _sel
                    from app.models import Symbol as _Symbol
                    from app.services.search.vector_indexer import VectorIndexer

                    EMBED_MAX_SECONDS = 90  # hard cap — never block ingest for more than 90s
                    MAX_FILES_TO_EMBED = 60  # embed most important files only

                    # Sort by LOC descending — embed the most significant files first
                    files_to_embed = sorted(file_models, key=lambda f: f.loc, reverse=True)[:MAX_FILES_TO_EMBED]

                    total_chunks_upserted = 0
                    embed_start = _time.monotonic()

                    for f_model in files_to_embed:
                        # Hard time cap: stop embedding if we've used too much time
                        elapsed = _time.monotonic() - embed_start
                        if elapsed >= EMBED_MAX_SECONDS:
                            logger.info(
                                "Embedding time cap (%.0fs) reached after %d chunks — skipping remaining files",
                                EMBED_MAX_SECONDS, total_chunks_upserted,
                            )
                            break

                        file_path_abs = work_dir / f_model.path
                        if not file_path_abs.exists():
                            continue
                        try:
                            content = file_path_abs.read_text(encoding="utf-8", errors="ignore")
                            # Fetch symbols for this file
                            sym_stmt = _sel(_Symbol).where(_Symbol.file_id == f_model.id)
                            file_syms = (await session.execute(sym_stmt)).scalars().all()
                            # Chunk by AST symbols
                            chunks = VectorIndexer.chunk_file_by_symbols(
                                repo_id=str(repo_id),
                                file_path=f_model.path,
                                language=f_model.language,
                                content=content,
                                symbols=file_syms,
                            )
                            # Batch embed + upsert (all chunks in one Ollama call per file)
                            n_upserted = await asyncio.wait_for(
                                VectorIndexer.upsert_chunks(chunks, batch_size=30),
                                timeout=40.0,  # max 40s per file
                            )
                            total_chunks_upserted += n_upserted
                        except asyncio.TimeoutError:
                            logger.debug("Embedding timeout for %s — skipping", f_model.path)
                        except Exception as _emb_ex:
                            logger.debug("Embedding skip for %s: %s", f_model.path, _emb_ex)

                    elapsed_total = _time.monotonic() - embed_start
                    job.message = (
                        f"Indexed {total_symbols} symbols and embedded "
                        f"{total_chunks_upserted} code chunks into Qdrant "
                        f"({elapsed_total:.1f}s)."
                    )
                    await session.commit()
                    publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

                except Exception as emb_error:
                    logger.warning("Vector embedding stage failed (non-fatal): %s", emb_error)


                # Stage 5: AI Analysis & Architecture Generation
                job.status = "ANALYZING"
                job.stage = "Generating AI Summary & Architecture Diagram"
                job.progress = 95.0
                job.message = "Running stack detector, architecture generator, and folder analyzer..."
                await session.commit()
                publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

                try:
                    summary_data = await StackDetector.analyze_stack(session, repo_id, file_models)
                    arch_data = await ArchitectureGenerator.generate_diagram(session, repo_id, file_models)
                    folders_data = await FolderAnalyzer.analyze_folders(session, repo_id, file_models)

                    # Persist analysis
                    del_an = select(RepoAnalysis).where(RepoAnalysis.repo_id == repo_id)
                    ex_ans = (await session.execute(del_an)).scalars().all()
                    for ea in ex_ans:
                        await session.delete(ea)

                    analysis_record = RepoAnalysis(
                        repo_id=repo_id,
                        summary_json=summary_data,
                        architecture_json=arch_data,
                        folders_json=folders_data,
                    )
                    session.add(analysis_record)
                    await session.flush()
                except Exception as ex:
                    logger.error("Analysis stage failed for repo %s: %s", repo_id, ex, exc_info=True)

                # Update Repo status
                repo_stmt = select(Repo).where(Repo.id == repo_id)
                repo = (await session.execute(repo_stmt)).scalar_one_or_none()
                if repo:
                    repo.status = "ready"

                # Mark Job Complete
                job.status = "COMPLETE"
                job.stage = "Ingestion Complete"
                job.progress = 100.0
                job.message = f"Successfully analyzed {len(file_models)} files and generated repository intelligence."
                await session.commit()

                publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)

            finally:
                if temp_dir and os.path.exists(temp_dir) and source_type == "github":
                    shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            logger.error("Ingestion failed for job %s: %s", job_id_str, e, exc_info=True)
            job.status = "FAILED"
            job.stage = "Failed"
            job.progress = 0.0
            job.message = f"Ingestion error: {str(e)}"
            job.error = str(e)
            
            # Set repo status to error
            repo_stmt = select(Repo).where(Repo.id == repo_id)
            repo = (await session.execute(repo_stmt)).scalar_one_or_none()
            if repo:
                repo.status = "error"
                
            await session.commit()
            publish_job_update(job_id_str, job.stage, job.progress, job.message, job.status)


@celery_app.task(name="ingest.repo")
def ingest_repo_task(job_id: str, source_type: str, source_input: str):
    asyncio.run(_process_ingest_repo(job_id, source_type, source_input))
