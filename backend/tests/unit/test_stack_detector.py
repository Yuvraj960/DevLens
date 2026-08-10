import pytest
from app.models import File
from app.services.analysis.stack_detector import StackDetector


@pytest.mark.asyncio
async def test_stack_detector_fingerprinting(db_session):
    files = [
        File(path="src/app/page.tsx", language="typescript", size_bytes=200, loc=20, content_hash="h1"),
        File(path="src/api/router.ts", language="typescript", size_bytes=300, loc=40, content_hash="h2"),
        File(path="pyproject.toml", language="toml", size_bytes=150, loc=15, content_hash="h3"),
    ]

    summary = await StackDetector.analyze_stack(db_session, "test_repo_id", files)

    assert "overview" in summary
    assert "metrics text" not in summary
    assert summary["metrics"]["total_files"] == 3
    assert summary["metrics"]["total_loc"] == 75
    assert summary["metrics"]["complexity_score"] >= 1
    assert len(summary["entry_points"]) >= 1
