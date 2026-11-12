import pytest

from flux.review import apply_if_unchanged, snapshot_files


def test_snapshot_prevents_overwriting_changed_file(tmp_path):
    path = tmp_path / "main.py"
    path.write_text("a = 1\n", encoding="utf-8")
    proposal = {"files": [{"path": "main.py", "content": "a = 2\n"}]}
    before = snapshot_files(tmp_path, proposal)
    path.write_text("a = 99\n", encoding="utf-8")
    with pytest.raises(ValueError, match="changed"):
        apply_if_unchanged(tmp_path, proposal, before)
    assert path.read_text(encoding="utf-8") == "a = 99\n"


def test_approved_snapshot_can_apply(tmp_path):
    path = tmp_path / "main.py"
    path.write_text("print(1)\n", encoding="utf-8")
    proposal = {"files": [{"path": "main.py", "content": "print(2)\n"}]}
    before = snapshot_files(tmp_path, proposal)
    apply_if_unchanged(tmp_path, proposal, before)
    assert path.read_text(encoding="utf-8") == "print(2)\n"


def test_invalid_protected_path_rejected(tmp_path):
    proposal = {"files": [{"path": ".env", "content": "TOKEN=secret"}]}
    with pytest.raises(ValueError):
        snapshot_files(tmp_path, proposal)
