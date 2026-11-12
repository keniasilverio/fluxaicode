"""User-facing CLI. Always preview and ask before editing."""
import argparse
from pathlib import Path
from .agent import apply, files_in_workspace, preview, propose
from .model import LocalModelError


def main() -> None:
    parser = argparse.ArgumentParser(description="Flux Code AI — local, approval-first coding agent")
    parser.add_argument("--workspace", required=True, help="Local folder containing source code")
    parser.add_argument("--model", default="qwen2.5-coder:7b", help="Previously downloaded Ollama model")
    parser.add_argument("--task", help="Coding request in Portuguese or English")
    parser.add_argument("--files", nargs="*", help="Files to provide as context")
    args = parser.parse_args()
    root = Path(args.workspace).expanduser().resolve()
    if not root.is_dir():
        parser.error("Workspace must be an existing directory")
    task = args.task or input("Flux, what should I code? ").strip()
    files = args.files if args.files is not None else []
    if not files:
        print("Available source files:")
        print("\n".join(files_in_workspace(root)[:40]))
        files = [p.strip() for p in input("Context files (comma-separated relative paths): ").split(",") if p.strip()]
    if not files:
        parser.error("Select at least one context file")
    try:
        proposal = propose(root, task, files, args.model)
        print("\nFlux summary:", proposal.get("summary", ""))
        print("\nPROPOSED DIFF (nothing changed yet):\n", preview(root, proposal))
        answer = input("Apply these changes? Type YES exactly: ")
        if answer == "YES":
            apply(root, proposal)
            print("Changes applied locally. Review and run your tests before committing.")
        else:
            print("No files changed.")
    except (ValueError, OSError, LocalModelError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
