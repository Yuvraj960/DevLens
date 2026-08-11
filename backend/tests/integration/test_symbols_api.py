import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, Symbol


@pytest.mark.asyncio
async def test_get_symbols_api(client: AsyncClient, db_session: AsyncSession):
    # Setup test Repo and File
    repo = Repo(name="test_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="src/user.ts",
        language="typescript",
        size_bytes=100,
        loc=10,
        content_hash="hash123",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="UserService",
        kind="class",
        signature="class UserService",
        start_line=1,
        end_line=10,
        is_exported=True,
    )
    db_session.add(symbol)
    await db_session.commit()

    # Query Symbols API
    resp = await client.get(f"/api/v1/repos/{repo.id}/symbols?q=UserService")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "UserService"
    assert data[0]["kind"] == "class"
    assert data[0]["file_path"] == "src/user.ts"


@pytest.mark.asyncio
async def test_hybrid_search_api(client: AsyncClient, db_session: AsyncSession):
    repo = Repo(name="test_repo_search", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="src/auth.ts",
        language="typescript",
        size_bytes=120,
        loc=15,
        content_hash="hash456",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="validateJwtToken",
        kind="function",
        signature="function validateJwtToken(token: string)",
        start_line=1,
        end_line=15,
        is_exported=True,
    )
    db_session.add(symbol)
    await db_session.commit()

    resp = await client.post(
        f"/api/v1/repos/{repo.id}/search/hybrid",
        json={"query": "validateJwtToken", "limit": 10},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "validateJwtToken"
    assert data[0]["matched_by"] == "symbol_exact"
