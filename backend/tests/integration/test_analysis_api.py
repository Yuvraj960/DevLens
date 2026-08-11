import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import File, Repo, RepoAnalysis


@pytest.mark.asyncio
async def test_analysis_summary_and_architecture_apis(client: AsyncClient, db_session: AsyncSession):
    repo = Repo(name="test_analysis_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="app/main.py",
        language="python",
        size_bytes=100,
        loc=25,
        content_hash="h123",
    )
    db_session.add(file_obj)
    await db_session.flush()

    analysis = RepoAnalysis(
        repo_id=repo.id,
        summary_json={
            "overview": "FastAPI python application.",
            "stack": {"primary": "Python / FastAPI", "framework": "FastAPI", "language": "Python"},
            "metrics": {"total_files": 1, "total_loc": 25, "languages": {"python": 1}, "complexity_score": 1, "estimated_onboarding_minutes": 15},
            "key_modules": [],
            "entry_points": [],
            "risks": [],
        },
        architecture_json={"nodes": [], "edges": [], "layers": ["api"]},
        folders_json=[{"path": "app", "purpose": "App directory", "key_files": [], "patterns": [], "complexity": 1.0, "test_coverage": 0.5}],
    )
    db_session.add(analysis)
    await db_session.commit()

    # GET /summary
    res_sum = await client.get(f"/api/v1/repos/{repo.id}/summary")
    assert res_sum.status_code == 200
    assert res_sum.json()["overview"] == "FastAPI python application."

    # GET /architecture
    res_arch = await client.get(f"/api/v1/repos/{repo.id}/architecture")
    assert res_arch.status_code == 200
    assert "nodes" in res_arch.json()

    # GET /folders
    res_fold = await client.get(f"/api/v1/repos/{repo.id}/folders")
    assert res_fold.status_code == 200
    assert len(res_fold.json()) == 1
    assert res_fold.json()[0]["path"] == "app"
