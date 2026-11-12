"""Generate a proposed edit, preview the diff, and apply only on approval."""
import difflib
import json
import re
from pathlib import Path
from .model import ask_ollama
from .safety import MAX_FILE_BYTES, read_text, safe_path, DENIED_PARTS

MAX_CONTEXT_CHARS = 26000
MAX_PROPOSAL_BYTES = 100_000


def files_in_workspace(root: Path, limit: int = 70) -> list[str]:
    paths = []
    for candidate in sorted(root.rglob("*")):
        if len(paths) >= limit:
            break
        if not candidate.is_file() or candidate.is_symlink():
            continue
        relative = candidate.relative_to(root).as_posix()
        try:
            safe_path(root, relative, must_exist=True)
        except ValueError:
            continue
        if candidate.stat().st_size <= MAX_FILE_BYTES and not any(p in DENIED_PARTS for p in candidate.parts):
            paths.append(relative)
    return paths


def parse_proposal(reply: str) -> dict:
    cleaned = reply.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Model did not return valid JSON. No files changed.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        raise ValueError("Proposal must contain a files list")
    if not 1 <= len(data["files"]) <= 8:
        raise ValueError("A proposal must change between 1 and 8 files")
    seen = set()
    for entry in data["files"]:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not isinstance(entry.get("content"), str):
            raise ValueError("Each file must have path and complete content strings")
        if entry["path"] in seen or len(entry["content"].encode()) > MAX_PROPOSAL_BYTES:
            raise ValueError("Duplicate path or oversized proposed file")
        seen.add(entry["path"])
    return data


def propose(root: Path, task: str, selected_files: list[str], model: str) -> dict:
    snippets = []
    for name in selected_files:
        content = read_text(root, name)
        snippets.append(f"--- FILE: {name} ---\n{content}\n--- END ---")
    context = "\n".join(snippets)
    if len(context) > MAX_CONTEXT_CHARS:
        raise ValueError("Too much context; select fewer/smaller files")
    prompt = f'''You are Flux, an expert coding assistant. Work only within a software workspace.
Task: {task}
Available file list: {json.dumps(files_in_workspace(root), ensure_ascii=False)}
You may change up to 8 files. Use existing file paths or new relative paths.
Output ONLY a valid JSON object of the form:
{{"summary":"what changed", "files":[{{"path":"relative/path.py","content":"COMPLETE replacement file contents"}}]}}
Never include secrets, credentials, terminal commands to execute, or markdown code fences.
If task cannot be done from context, explain that in summary and still provide the best self-contained file proposal.
Selected source files:\n{context}'''
    return parse_proposal(ask_ollama(prompt, model=model))


def preview(root: Path, proposal: dict) -> str:
    changes = []
    for file in proposal["files"]:
        path = safe_path(root, file["path"])
        if path.exists() and not path.is_file():
            raise ValueError("Cannot replace a directory")
        original = read_text(root, file["path"]) if path.exists() else ""
        changes.extend(difflib.unified_diff(original.splitlines(keepends=True), file["content"].splitlines(keepends=True),
                         fromfile=f"a/{file['path']}", tofile=f"b/{file['path']}"))
    return "".join(changes) or "No differences."


def apply(root: Path, proposal: dict) -> None:
    # Preflight ALL paths before touching any file.
    targets = []
    for item in proposal["files"]:
        path = safe_path(root, item["path"])
        if path.exists() and not path.is_file():
            raise ValueError("Cannot replace a directory")
        targets.append((path, item["content"]))
    for path, content in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
