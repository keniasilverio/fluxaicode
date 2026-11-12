# 💠 Flux Code AI — prototype v0.2

**Status:** A working Python codebase and a browser chat UI have been committed to a draft pull request. The AI model connection still requires a running Ollama instance; it is not yet a hosted, ready-to-use AI service.

Flux aims to help write Python data-analysis scripts, maintain apps, and suggest source-code changes with human approval.

## Browser interface (GitHub Codespaces — no installation on your Windows PC)

1. Open the repository in GitHub and select **Code → Codespaces → Create codespace on feature/flux-mvp**.
2. Inside the Codespaces terminal, run:

```bash
python -m pip install -e '.[test]'
export FLUX_WORKSPACE="$PWD"
streamlit run flux/web.py --server.address 127.0.0.1 --server.port 8501
```

3. Open port **8501** through Codespaces' **Ports** tab (keep visibility **Private**).

The page should display Flux Code AI, file selection and a chat prompt. **Code generation will not work until Ollama and a compatible coding model are running on that same Codespace**. Models may exceed Codespaces memory and computation quotas. Codespaces uses cloud compute, so do not upload confidential work models without permission.

For initial UI inspection, no model is required; requests will show an explicit connection error until a model is available.

## Offline Windows setup (later)

Install Python 3.10+, Git and Ollama on your Windows computer, download a model once while online, and then:

```powershell
ollama pull qwen2.5-coder:7b
python -m pip install -e .
$env:FLUX_WORKSPACE = "C:\\path\\to\\your\\project"
streamlit run flux/web.py
```

Open the local Streamlit URL on that computer. After setup and download, model generation can run offline without per-token API charges. The computer's RAM/GPU determine usable model size and speed.

## What the UI can do

- Choose a **workspace** using the `FLUX_WORKSPACE` environment variable.
- Select files from that workspace as context.
- Type coding tasks in Portuguese or English.
- Ask Ollama for a JSON proposal of file edits.
- Review the complete diff and a summary.
- Explicitly approve before writing files.
- Reject stale proposals if workspace files changed since review.
- Run local project tests separately (Flux does not automatically execute generated code).

**Never make a cloud workspace public, upload credentials, or point it at employer-confidential data without approval.** Do not use the development server on an untrusted network.

## Testing

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

GitHub Actions also runs tests when the branch is pushed.

## Roadmap

- Validate end-to-end generation using a running Ollama model.
- Optional configurable inference backend for lightweight cloud testing.
- Safer Git branching, sandboxed test execution and human-reviewed pull requests.
- Controlled connection to Lilo and CFO AI.
- Better support for large repositories and project-wide changes.
