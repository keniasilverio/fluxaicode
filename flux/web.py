"""Streamlit browser interface for Flux Code AI.

Start with: streamlit run flux/web.py
Configure FLUX_WORKSPACE to a trusted local project folder before startup.
"""
import hashlib
import os
from pathlib import Path

import streamlit as st

from flux.agent import files_in_workspace, parse_proposal, preview, propose
from flux.model import LocalModelError
from flux.review import apply_if_unchanged, snapshot_files

st.set_page_config(page_title="Flux Code AI", page_icon="💠", layout="wide")

st.markdown("""
<style>
.block-container {max-width: 1120px; padding-top: 2.1rem;}
h1 {letter-spacing: -0.04em;}
div[data-testid="stChatMessage"] {border-radius: 14px;}
</style>
""", unsafe_allow_html=True)

st.title("💠 Flux Code AI")
st.caption("Your independent coding assistant · Python & app development · Approval-first changes")

configured = os.environ.get("FLUX_WORKSPACE", "")
workspace = Path(configured).expanduser().resolve() if configured else None
if workspace is None or not workspace.is_dir():
    st.error("Set FLUX_WORKSPACE to an existing, trusted project folder before starting Flux.")
    st.code('FLUX_WORKSPACE=/path/to/project streamlit run flux/web.py', language="bash")
    st.stop()

if "workspace_key" not in st.session_state or st.session_state.workspace_key != str(workspace):
    st.session_state.workspace_key = str(workspace)
    st.session_state.proposal = None
    st.session_state.snapshot = None
    st.session_state.history = []

with st.sidebar:
    st.subheader("Workspace")
    st.code(str(workspace))
    st.info("The workspace stays on the machine running Flux. If using Codespaces, this means the cloud workspace.")
    model = st.text_input("Ollama model", value="qwen2.5-coder:7b")
    st.caption("The model must be installed and Ollama must be running on this same machine.")
    st.divider()
    available = files_in_workspace(workspace)
    selected = st.multiselect("Files to include as context", available, default=available[:min(2, len(available))])
    st.caption("Select relevant source files. Avoid confidential material on shared or cloud machines.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.proposal = None
        st.session_state.snapshot = None
        st.rerun()

for item in st.session_state.history:
    with st.chat_message(item["role"]):
        st.markdown(item["text"])

task = st.chat_input("Ex.: Flux, crie uma função Python para analisar receitas mensais...")
if task:
    st.session_state.proposal = None
    st.session_state.snapshot = None
    st.session_state.history.append({"role": "user", "text": task})
    if not selected:
        st.session_state.history.append({"role": "assistant", "text": "Selecione pelo menos um arquivo no menu lateral."})
    else:
        with st.spinner("Flux is analyzing the selected files..."):
            try:
                proposal = propose(workspace, task, selected, model)
                diff = preview(workspace, proposal)
                originals = snapshot_files(workspace, proposal)
                st.session_state.proposal = proposal
                st.session_state.snapshot = originals
                summary = proposal.get("summary") or "Proposed code changes ready for review."
                st.session_state.history.append({"role": "assistant", "text": str(summary)})
            except (ValueError, OSError, LocalModelError) as exc:
                st.session_state.history.append({"role": "assistant", "text": f"Could not create a proposal: {exc}"})
    st.rerun()

proposal = st.session_state.proposal
if proposal:
    st.divider()
    st.subheader("Review proposed changes")
    st.warning("AI-generated code may be incorrect. Review every change. Flux will not execute or commit it.")
    st.write(proposal.get("summary", ""))
    try:
        diff = preview(workspace, proposal)
        st.code(diff, language="diff")
        with st.form("approval_form", clear_on_submit=True):
            approval = st.checkbox("I reviewed the changes and authorize writing these files")
            submitted = st.form_submit_button("Apply changes to workspace", type="primary", disabled=not bool(diff.strip()) or diff == "No differences.")
        if submitted:
            if not approval:
                st.error("Approval is required before writing any files.")
            else:
                try:
                    apply_if_unchanged(workspace, proposal, st.session_state.snapshot)
                    st.success("Changes saved to the workspace. Run tests and inspect Git diff before committing.")
                    st.session_state.proposal = None
                    st.session_state.snapshot = None
                except (ValueError, OSError) as exc:
                    st.error(f"Nothing was applied: {exc}")
    except (ValueError, OSError) as exc:
        st.error(f"Cannot display or apply proposal: {exc}")
