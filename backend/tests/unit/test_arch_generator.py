import pytest
from app.models import File
from app.services.analysis.arch_generator import ArchitectureGenerator


@pytest.mark.asyncio
async def test_arch_generator_layers(db_session):
    files = [
        File(path="src/components/Button.tsx", language="typescript", size_bytes=100, loc=20, content_hash="h1"),
        File(path="src/api/routes.ts", language="typescript", size_bytes=200, loc=50, content_hash="h2"),
        File(path="src/models/user.ts", language="typescript", size_bytes=150, loc=30, content_hash="h3"),
    ]

    diagram = await ArchitectureGenerator.generate_diagram(db_session, "test_repo_id", files)

    assert "nodes" in diagram
    assert "layers" in diagram
    assert len(diagram["nodes"]) >= 1

    # Check classification
    assert ArchitectureGenerator.classify_layer("src/components/Button.tsx") == "presentation"
    assert ArchitectureGenerator.classify_layer("src/api/routes.ts") == "api"
    assert ArchitectureGenerator.classify_layer("src/models/user.ts") == "data_access"
