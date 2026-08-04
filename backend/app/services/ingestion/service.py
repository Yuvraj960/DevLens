import hashlib
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

from app.schemas.repo import FileTreeNode

# Ignored directory & file patterns
IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".idea",
    ".vscode",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".turbo",
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf", ".zip", ".tar", ".gz",
    ".7z", ".exe", ".dll", ".so", ".dylib", ".pyc", ".pyo", ".pyd", ".db", ".sqlite",
    ".bin", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4", ".mov", ".avi",
}

LANGUAGE_MAP = {
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".php": "php",
    ".rb": "ruby",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".html": "html",
    ".css": "css",
    ".sql": "sql",
}


class IngestionService:
    @staticmethod
    def is_binary(file_path: Path) -> bool:
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            return True
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(8000)
                return b"\x00" in chunk
        except Exception:
            return True

    @staticmethod
    def calculate_file_metrics(file_path: Path) -> tuple[int, int, str]:
        """Returns (size_bytes, line_of_code, sha256_hash)"""
        size_bytes = file_path.stat().st_size
        sha256 = hashlib.sha256()
        loc = 0

        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    sha256.update(chunk)

            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                loc = sum(1 for _ in f)
        except Exception:
            pass

        return size_bytes, loc, sha256.hexdigest()

    @staticmethod
    def detect_language(file_path: Path) -> str:
        return LANGUAGE_MAP.get(file_path.suffix.lower(), "text")

    @classmethod
    def walk_repository(cls, root_dir: Path) -> list[dict[str, Any]]:
        manifest: list[dict[str, Any]] = []

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Prune ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS and not d.startswith(".")]

            for filename in filenames:
                file_path = Path(dirpath) / filename
                rel_path = file_path.relative_to(root_dir).as_posix()

                if cls.is_binary(file_path):
                    continue

                size_bytes, loc, content_hash = cls.calculate_file_metrics(file_path)
                language = cls.detect_language(file_path)

                manifest.append({
                    "path": rel_path,
                    "language": language,
                    "size_bytes": size_bytes,
                    "loc": loc,
                    "content_hash": content_hash,
                })

        return manifest

    @classmethod
    def build_file_tree(cls, file_records: list[dict[str, Any]]) -> list[FileTreeNode]:
        root_nodes: dict[str, Any] = {}

        for rec in file_records:
            parts = rec["path"].split("/")
            current = root_nodes

            for i, part in enumerate(parts):
                is_file = (i == len(parts) - 1)
                full_path = "/".join(parts[:i + 1])

                if part not in current:
                    current[part] = {
                        "name": part,
                        "path": full_path,
                        "is_directory": not is_file,
                        "size_bytes": rec["size_bytes"] if is_file else 0,
                        "children": {} if not is_file else None,
                    }
                elif not is_file:
                    pass

                if not is_file:
                    current = current[part]["children"]

        def convert_dict_to_list(node_dict: dict[str, Any]) -> list[FileTreeNode]:
            nodes: list[FileTreeNode] = []
            for item in sorted(node_dict.values(), key=lambda x: (not x["is_directory"], x["name"])):
                children_list = convert_dict_to_list(item["children"]) if item["is_directory"] else []
                nodes.append(
                    FileTreeNode(
                        name=item["name"],
                        path=item["path"],
                        is_directory=item["is_directory"],
                        size_bytes=item["size_bytes"],
                        children=children_list,
                    )
                )
            return nodes

        return convert_dict_to_list(root_nodes)
