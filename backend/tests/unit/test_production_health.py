import pytest
from app.models import File, Repo, Symbol
from app.services.discovery import ApiExtractor, AuthExtractor, DbExtractor, TraceExtractor
from app.services.gamechanger import ArchDiff, CodeReviewer, DependencyGraphBuilder, OnboardingGenerator, RefactorEngine, TimelineGenerator
from app.services.trace import TraceEngine


@pytest.mark.asyncio
async def test_full_production_system_health(db_session):
    # Create test repository
    repo = Repo(name="prod_health_repo", source_type="folder")
    db_session.add(repo)
    await db_session.flush()

    file_obj = File(
        repo_id=repo.id,
        path="backend/app/main.py",
        language="python",
        size_bytes=300,
        loc=50,
        content_hash="hprodhealth99",
    )
    db_session.add(file_obj)
    await db_session.flush()

    symbol = Symbol(
        file_id=file_obj.id,
        name="root_health_check",
        kind="function",
        start_line=1,
        end_line=20,
        is_exported=True,
    )
    db_session.add(symbol)
    await db_session.commit()

    # 1. API Discovery Engine
    endpoints = await ApiExtractor.extract_endpoints(db_session, repo.id, [file_obj])
    assert len(endpoints) >= 1

    # 2. Database Schema Visualizer
    db_schema = await DbExtractor.extract_database_schema(db_session, repo.id, [file_obj])
    assert "tables" in db_schema

    # 3. Auth Engine
    auth_flow = AuthExtractor.extract_auth_flow([file_obj])
    assert "steps" in auth_flow

    # 4. Flagship Execution Trace Engine
    trace_data = await TraceEngine.generate_trace(db_session, repo.id)
    assert len(trace_data["nodes"]) >= 1

    # 5. Multi-Agent AI Code Review
    findings = await CodeReviewer.review_repository(db_session, repo.id, [file_obj])
    assert len(findings) >= 1

    # 6. AST Refactoring Engine
    suggestions = await RefactorEngine.generate_suggestions(db_session, repo.id, [file_obj])
    assert len(suggestions) >= 1

    # 7. Commit Timeline Narrator
    timeline = TimelineGenerator.generate_timeline([file_obj])
    assert len(timeline) >= 6

    # 8. Architecture Diff
    diff = ArchDiff.compare_branches([file_obj])
    assert "added_endpoints" in diff

    # 9. Onboarding Generator
    onboarding = OnboardingGenerator.generate_onboarding_path([file_obj])
    assert len(onboarding) >= 4

    # 10. Dependency Graph Builder
    graph = await DependencyGraphBuilder.build_graph(db_session, repo.id, [file_obj])
    assert "nodes" in graph
