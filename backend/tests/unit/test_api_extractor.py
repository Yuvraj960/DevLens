import pytest
from app.models import File, Symbol
from app.services.discovery.api_extractor import ApiExtractor


@pytest.mark.asyncio
async def test_api_extractor(db_session):
    repo_file = File(path="app/api/v1/repos.py", language="python", size_bytes=200, loc=30, content_hash="he1")
    db_session.add(repo_file)
    await db_session.flush()

    sym = Symbol(
        file_id=repo_file.id,
        name="get_all_repos",
        kind="function",
        signature="@router.get('/repos')",
        start_line=10,
        end_line=25,
    )
    db_session.add(sym)
    await db_session.commit()

    endpoints = await ApiExtractor.extract_endpoints(db_session, "test_repo_id", [repo_file])

    assert len(endpoints) >= 1
    ep = next(e for e in endpoints if e["controller"]["name"] == "get_all_repos")
    assert ep["method"] == "GET"
    assert "/api/v1/" in ep["path"]
