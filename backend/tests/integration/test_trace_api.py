import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, Symbol


@pytest.mark.asyncio
async def test_trace_apis(client: AsyncClient, db_session: AsyncSession):
    repo = Repo(name="test_trace_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="app/api/v1/orders.py",
        language="python",
        size_bytes=200,
        loc=40,
        content_hash="htrace99",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="create_order",
        kind="function",
        start_line=10,
        end_line=30,
    )
    db_session.add(symbol)
    await db_session.commit()

    # GET /trace/entry-points
    res_eps = await client.get(f"/api/v1/repos/{repo.id}/trace/entry-points")
    assert res_eps.status_code == 200
    assert len(res_eps.json()) >= 1

    # POST /trace/flow
    res_flow = await client.post(
        f"/api/v1/repos/{repo.id}/trace/flow",
        json={"entry_point_symbol": "create_order"},
    )
    assert res_flow.status_code == 200
    data = res_flow.json()
    assert "nodes" in data
    assert "edges" in data
    assert "entry_points" in data
