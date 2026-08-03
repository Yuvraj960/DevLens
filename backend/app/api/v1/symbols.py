import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File, Import, Repo, Symbol
from app.services.search.hybrid_search import HybridSearchService

router = APIRouter(prefix="/repos/{repo_id}", tags=["Symbols & Search"])


class SymbolResponse(BaseModel):
    id: uuid.UUID
    name: str
    kind: str
    file_path: str
    start_line: int
    end_line: int
    signature: str | None = None
    docstring: str | None = None
    is_exported: bool
    is_async: bool


class SymbolReferenceResponse(BaseModel):
    symbol_name: str
    references: list[dict[str, Any]]


class HybridSearchRequest(BaseModel):
    query: str
    kind: str | None = None
    limit: int = 20


class HybridSearchResultResponse(BaseModel):
    symbol_id: str | None
    name: str
    kind: str
    file_path: str
    start_line: int
    end_line: int
    signature: str | None
    score: float
    matched_by: str


@router.get(
    "/symbols",
    response_model=list[SymbolResponse],
    summary="Fuzzy symbol search",
    description="Finds code symbols (functions, classes, interfaces) matching search query.",
)
async def get_symbols(
    repo_id: uuid.UUID,
    q: str | None = Query(default=None, description="Fuzzy name search query"),
    kind: str | None = Query(default=None, description="Symbol kind filter (function, class, etc.)"),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[SymbolResponse]:
    # Check repo
    repo = (await db.execute(select(Repo).where(Repo.id == repo_id))).scalar_one_or_none()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")

    stmt = (
        select(Symbol, File)
        .join(File, Symbol.file_id == File.id)
        .where(File.repo_id == repo_id)
    )

    if kind:
        stmt = stmt.where(Symbol.kind == kind)

    if q:
        stmt = stmt.where(Symbol.name.ilike(f"%{q}%"))

    stmt = stmt.order_by(Symbol.name.asc()).limit(limit)
    rows = (await db.execute(stmt)).all()

    return [
        SymbolResponse(
            id=sym.id,
            name=sym.name,
            kind=sym.kind,
            file_path=file_obj.path,
            start_line=sym.start_line,
            end_line=sym.end_line,
            signature=sym.signature,
            docstring=sym.docstring,
            is_exported=sym.is_exported,
            is_async=sym.is_async,
        )
        for sym, file_obj in rows
    ]


@router.get(
    "/symbols/{symbol_id}/references",
    response_model=SymbolReferenceResponse,
    summary="Find symbol references",
    description="Returns usages and cross-file imports referencing a target symbol.",
)
async def get_symbol_references(
    repo_id: uuid.UUID,
    symbol_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SymbolReferenceResponse:
    # Fetch target symbol
    sym_stmt = select(Symbol, File).join(File, Symbol.file_id == File.id).where(Symbol.id == symbol_id)
    target = (await db.execute(sym_stmt)).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol_id} not found")

    target_sym, target_file = target

    # Find imports referencing symbol name
    imp_stmt = (
        select(Import, File)
        .join(File, Import.file_id == File.id)
        .where(File.repo_id == repo_id, Import.imported_symbol == target_sym.name)
    )
    imp_rows = (await db.execute(imp_stmt)).all()

    references = [
        {
            "file_path": file_obj.path,
            "imported_from": imp.source,
            "is_external": imp.is_external,
        }
        for imp, file_obj in imp_rows
    ]

    return SymbolReferenceResponse(
        symbol_name=target_sym.name,
        references=references,
    )


@router.post(
    "/search/hybrid",
    response_model=list[HybridSearchResultResponse],
    summary="Hybrid code search",
    description="Combines vector similarity, BM25 text search, and PostgreSQL symbol matching.",
)
async def hybrid_search_symbols(
    repo_id: uuid.UUID,
    req: HybridSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> list[HybridSearchResultResponse]:
    results = await HybridSearchService.search(
        session=db,
        repo_id=repo_id,
        query=req.query,
        kind_filter=req.kind,
        limit=req.limit,
    )

    return [
        HybridSearchResultResponse(
            symbol_id=r.symbol_id,
            name=r.name,
            kind=r.kind,
            file_path=r.file_path,
            start_line=r.start_line,
            end_line=r.end_line,
            signature=r.signature,
            score=r.score,
            matched_by=r.matched_by,
        )
        for r in results
    ]
