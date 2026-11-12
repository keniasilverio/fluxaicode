"""Optimistic concurrency checks for applying AI code edits."""
import hashlib
from pathlib import Path

from .agent import apply
from .safety import read_text, safe_path


def _file_digest(root: Path, relative: str) -> str | None:
    path = safe_path(root, relative)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError("Proposal cannot overwrite a directory")
    content = read_text(root, relative)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def snapshot_files(root: Path, proposal: dict) -> dict[str, str | None]:
    """Capture original contents as hashes before displaying a proposal."""
    return {item["path"]: _file_digest(root, item["path"]) for item in proposal["files"]}


def apply_if_unchanged(root: Path, proposal: dict, original: dict[str, str | None] | None) -> None:
    """Reject a proposal if files changed since it was reviewed."""
    if original is None:
        raise ValueError("Missing review snapshot. Regenerate the proposal.")
    current = snapshot_files(root, proposal)
    if current != original:
        raise ValueError("Workspace files changed since preview. Regenerate the proposal.")
    apply(root, proposal)
