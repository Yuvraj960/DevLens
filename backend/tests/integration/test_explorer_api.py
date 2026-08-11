import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, Symbol


@pytest.mark.asyncio
async def test_explorer_apis(client: AsyncClient, db_session: AsyncSession):
    repo = Repo(name="test_explorer_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="app/api/v1/users.py",
        language="python",
        size_bytes=200,
        loc=40,
        content_hash="hexp123",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="get_users",
        kind="function",
        signature="@router.get('/users')",
        start_line=10,
        end_line=30,
        is_exported=True,
    )
    db_session.add(symbol)
    await db_session.commit()

    # GET /endpoints
    res_ep = await client.get(f"/api/v1/repos/{repo.id}/endpoints")
    assert res_ep.status_code == 200
    assert len(res_ep.json()) >= 1

    # GET /database
    res_db = await client.get(f"/api/v1/repos/{repo.id}/database")
    assert res_db.status_code == 200
    assert "tables" in res_db.json()

    # GET /auth-flow
    res_auth = await client.get(f"/api/v1/repos/{repo.id}/auth-flow")
    assert res_auth.status_code == 200
    assert "steps" in res_auth.json()

    # GET /trace
    res_tr = await client.get(f"/api/v1/repos/{repo.id}/trace")
    assert res_tr.status_code == 200
    assert len(res_tr.json()) >= 1
