"""Explicit boundaries shared by validation and GitHub release packaging."""
from pathlib import Path

TOP_FILES = {"README.md", "README.zh-CN.md", "LICENSE", "THIRD_PARTY.md", "CHANGELOG.md",
             "CONTRIBUTING.md", "AGENTS.md", ".gitignore", "requirements-dev.txt"}
TOP_DIRS = {"plugins", "scripts", "tests", "examples", "docs", ".agents", ".github", ".claude-plugin"}
EXCLUDED_PARTS = {".git", ".local", "dist", "__pycache__", ".venv", ".obsidian"}


def source_files(root):
    root = Path(root)
    result = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if relative.parts[0] not in TOP_DIRS and str(relative) not in TOP_FILES:
            continue
        if path.is_symlink():
            raise ValueError("Release cannot contain symlinks: " + str(relative))
        if not path.is_file() or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.name in {".DS_Store", ".env"} or path.name.startswith(".env.") or path.suffix in {".pem", ".key"}:
            raise ValueError("Unexpected private file in release: " + str(relative))
        result.append(path)
    return result
