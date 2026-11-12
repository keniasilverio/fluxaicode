# Flux Code AI — MVP 0.1

Flux is a local-first coding assistant for Python scripts and app development.

**Current status:** initial Python prototype. It can ask a local Ollama model for a proposed code edit, show a diff, and apply changes only after explicit approval. It is not yet a fully autonomous Codex replacement.

## Features
- Read selected files from an existing project
- Ask a programming question in Portuguese or English
- Ask a local Ollama coding model to propose up to eight file changes
- Preview all proposed changes before they are written
- Block common secrets and paths outside the workspace
- Run 4 local safety tests and GitHub Actions CI

## Installation, when you choose to run offline

The GitHub repository stores the code; **GitHub itself does not supply offline model inference**. Running locally later requires Python 3.10+, Ollama, and a downloaded coding model appropriate for your hardware.

In a terminal inside the project:

```powershell
python -m pip install -e .
ollama pull qwen2.5-coder:7b
flux --workspace "C:\\path\\to\\project" --task "Improve CSV validation" --files main.py
```

Once the model is downloaded, this local workflow can operate offline.

## Development tests

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

## Limitations and safeguards

This first version does not provide a hosted chat interface, cloud execution, Github pull request automation, or automatic test execution on generated projects. Generated code should be reviewed and tested in a separate Git branch. Never place API keys, company-confidential models, or private data in prompts sent to a cloud model without authorization.

The CLI intentionally asks for **YES** before writing files. No automatic pushing to Github or execution of generated code is performed.

## Roadmap

1. Add a browser-based interface and a configurable model backend.
2. Add Git branch creation and tests inside an isolated workspace.
3. Connect Lilo and CFO AI repositories for approved changes.
4. Support offline local model execution after hardware verification.
