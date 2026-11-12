"""Workspace safety checks for AI-proposed edits."""
from pathlib import Path

DENIED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next"}
DENIED_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
DENIED_EXTENSIONS = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}
MAX_FILE_BYTES = 100_000


def safe_path(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    root = root.resolve()
    rel = Path(relative)
    if not relative or rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Only relative paths inside the workspace are allowed")
    if any(part in DENIED_PARTS for part in rel.parts):
        raise ValueError("Path contains a protected directory")
    if rel.name in DENIED_NAMES or rel.suffix in DENIED_EXTENSIONS or rel.name.startswith(".env."):
        raise ValueError("Potential secret or binary data path is protected")
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Path escapes workspace (possibly via symlink)")
    if must_exist and not path.is_file():
        raise ValueError("File does not exist")
    return path


def read_text(root: Path, relative: str) -> str:
    path = safe_path(root, relative, must_exist=True)
    if path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("File too large for the local context window")
    return path.read_text(encoding="utf-8")
