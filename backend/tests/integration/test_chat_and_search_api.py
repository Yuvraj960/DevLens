import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, Symbol


@pytest.mark.asyncio
async def test_chat_and_smart_search_apis(client: AsyncClient, db_session: AsyncSession):
    repo = Repo(name="test_chat_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="src/auth.ts",
        language="typescript",
        size_bytes=200,
        loc=30,
        content_hash="hchat123",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="verifyToken",
        kind="function",
        signature="function verifyToken(t: string)",
        start_line=5,
        end_line=25,
        is_exported=True,
    )
    db_session.add(symbol)
    await db_session.commit()

    # Test POST /chat
    res_chat = await client.post(
        f"/api/v1/repos/{repo.id}/chat",
        json={"message": "Where is verifyToken defined?"},
    )
    assert res_chat.status_code == 200
    data_chat = res_chat.json()
    assert "conversation_id" in data_chat
    assert "citations" in data_chat
    assert len(data_chat["citations"]) >= 1

    # Test POST /search/smart
    res_search = await client.post(
        f"/api/v1/repos/{repo.id}/search/smart",
        json={"query": "kind:function name:verifyToken*"},
    )
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert data_search["total"] == 1
    assert data_search["results"][0]["symbol"]["name"] == "verifyToken"
