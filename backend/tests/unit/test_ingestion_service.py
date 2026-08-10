import tempfile
from pathlib import Path
from app.services.ingestion.service import IngestionService


def test_binary_detection():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"PNGFakeBinaryData")
        file_path = Path(f.name)

    assert IngestionService.is_binary(file_path) is True


def test_walk_repository_filters_binary_and_ignored():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Valid source file
        (root / "src").mkdir()
        code_file = root / "src" / "index.ts"
        code_file.write_text("console.log('hello world');\nconst x = 10;\n", encoding="utf-8")

        # Ignored node_modules file
        (root / "node_modules").mkdir()
        ignored_file = root / "node_modules" / "package.json"
        ignored_file.write_text("{}", encoding="utf-8")

        manifest = IngestionService.walk_repository(root)

        assert len(manifest) == 1
        assert manifest[0]["path"] == "src/index.ts"
        assert manifest[0]["language"] == "typescript"
        assert manifest[0]["loc"] == 2


def test_file_tree_generation():
    file_records = [
        {"path": "src/index.ts", "language": "typescript", "size_bytes": 100, "loc": 5, "content_hash": "a1"},
        {"path": "src/utils/math.ts", "language": "typescript", "size_bytes": 50, "loc": 3, "content_hash": "a2"},
        {"path": "README.md", "language": "markdown", "size_bytes": 20, "loc": 1, "content_hash": "a3"},
    ]

    tree = IngestionService.build_file_tree(file_records)
    assert len(tree) == 2  # src/ and README.md
    assert tree[0].name == "src"
    assert tree[0].is_directory is True
    assert len(tree[0].children) == 2  # index.ts and utils/
