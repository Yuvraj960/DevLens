import pytest
from app.models import File, Symbol
from app.services.gamechanger.arch_diff import ArchDiff
from app.services.gamechanger.code_reviewer import CodeReviewer
from app.services.gamechanger.dependency_graph_builder import DependencyGraphBuilder
from app.services.gamechanger.onboarding_generator import OnboardingGenerator
from app.services.gamechanger.refactor_engine import RefactorEngine
from app.services.gamechanger.timeline_generator import TimelineGenerator


@pytest.mark.asyncio
async def test_gamechanger_services(db_session):
    file_obj = File(path="app/core/engine.py", language="python", size_bytes=250, loc=40, content_hash="hgc1")
    db_session.add(file_obj)
    await db_session.flush()

    sym = Symbol(file_id=file_obj.id, name="core_engine_task", kind="function", start_line=10, end_line=30)
    db_session.add(sym)
    await db_session.commit()

    # Code Reviewer
    findings = await CodeReviewer.review_repository(db_session, "test_repo", [file_obj])
    assert len(findings) >= 1

    # Refactor Engine
    suggestions = await RefactorEngine.generate_suggestions(db_session, "test_repo", [file_obj])
    assert len(suggestions) >= 1

    # Timeline Generator
    timeline = TimelineGenerator.generate_timeline([file_obj])
    assert len(timeline) >= 6

    # Arch Diff
    diff = ArchDiff.compare_branches([file_obj])
    assert "added_endpoints" in diff

    # Onboarding Generator
    steps = OnboardingGenerator.generate_onboarding_path([file_obj])
    assert len(steps) >= 4

    # Dependency Graph Builder
    graph = await DependencyGraphBuilder.build_graph(db_session, "test_repo", [file_obj])
    assert "nodes" in graph
    assert "edges" in graph
