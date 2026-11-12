import pytest
from flux.agent import apply, parse_proposal, preview
from flux.safety import safe_path


def test_path_traversal_blocked(tmp_path):
    for name in ["../outside.txt", "/tmp/outside", ".env", "nested/.git/config", "keys/private.pem"]:
        with pytest.raises(ValueError):
            safe_path(tmp_path, name)


def test_symlink_escape_blocked(tmp_path):
    target = tmp_path.parent / "external"
    target.mkdir(exist_ok=True)
    (tmp_path / "linked").symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError):
        safe_path(tmp_path, "linked/file.py")


def test_preview_and_apply(tmp_path):
    (tmp_path / "main.py").write_text("print('old')\n")
    p = parse_proposal('{"summary":"update","files":[{"path":"main.py","content":"print(123)\\n"}]}')
    diff = preview(tmp_path, p)
    assert "+print(123)" in diff
    assert (tmp_path / "main.py").read_text() == "print('old')\n"
    apply(tmp_path, p)
    assert (tmp_path / "main.py").read_text() == "print(123)\n"


def test_reject_invalid_proposal():
    with pytest.raises(ValueError):
        parse_proposal('{"files":[] }')
