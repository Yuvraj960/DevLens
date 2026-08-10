import pytest
from app.models import File, Symbol
from app.services.trace.engine import TraceEngine
from app.services.trace.entry_resolver import EntryResolver
from app.services.trace.path_traverser import PathTraverser


@pytest.mark.asyncio
async def test_trace_engine(db_session):
    f1 = File(path="app/api/v1/repos.py", language="python", size_bytes=200, loc=30, content_hash="htr1")
    f2 = File(path="app/services/ingestion.py", language="python", size_bytes=300, loc=50, content_hash="htr2")
    db_session.add_all([f1, f2])
    await db_session.flush()

    s1 = Symbol(file_id=f1.id, name="ingest_repository", kind="function", start_line=10, end_line=30)
    s2 = Symbol(file_id=f2.id, name="process_clone", kind="function", start_line=5, end_line=25)
    db_session.add_all([s1, s2])
    await db_session.commit()

    entry_points = await EntryResolver.resolve_entry_points(db_session, "test_repo_id", [f1, f2])
    assert len(entry_points) >= 1

    nodes, edges = await PathTraverser.traverse_flow(db_session, "test_repo_id", [f1, f2])
    assert len(nodes) >= 1
    assert len(edges) == len(nodes) - 1

    trace_data = await TraceEngine.generate_trace(db_session, f1.repo_id)
    assert "nodes" in trace_data
    assert "edges" in trace_data
    assert "entry_points" in trace_data
