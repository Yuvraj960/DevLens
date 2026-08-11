import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, Symbol


@pytest.mark.asyncio
async def test_gamechanger_apis(client: AsyncClient, db_session: AsyncSession):
    repo = Repo(name="test_gc_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="app/api/v1/auth.py",
        language="python",
        size_bytes=200,
        loc=40,
        content_hash="hgcapi123",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="verify_jwt",
        kind="function",
        start_line=10,
        end_line=30,
    )
    db_session.add(symbol)
    await db_session.commit()

    # POST /code-review
    res_review = await client.post(f"/api/v1/repos/{repo.id}/code-review", json={"scope": "all"})
    assert res_review.status_code == 200
    assert len(res_review.json()) >= 1

    # POST /refactor
    res_refactor = await client.post(f"/api/v1/repos/{repo.id}/refactor")
    assert res_refactor.status_code == 200
    assert len(res_refactor.json()) >= 1

    # GET /timeline
    res_tl = await client.get(f"/api/v1/repos/{repo.id}/timeline")
    assert res_tl.status_code == 200
    assert len(res_tl.json()) >= 1

    # POST /diff
    res_diff = await client.post(f"/api/v1/repos/{repo.id}/diff", json={"base_branch": "main", "head_branch": "feature/v2"})
    assert res_diff.status_code == 200
    assert "added_endpoints" in res_diff.json()

    # GET /onboarding
    res_onboarding = await client.get(f"/api/v1/repos/{repo.id}/onboarding")
    assert res_onboarding.status_code == 200
    assert len(res_onboarding.json()) >= 1

    # GET /dependency-graph
    res_graph = await client.get(f"/api/v1/repos/{repo.id}/dependency-graph")
    assert res_graph.status_code == 200
    assert "nodes" in res_graph.json()
