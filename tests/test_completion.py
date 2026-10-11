import os
import subprocess
import sys
import shlex

import pytest


def complete(tmp_path, words, shell="bash"):
    env = {**os.environ, "_CODE_DOWN_COMPLETE": f"complete_{shell}",
           "_TYPER_COMPLETE_FISH_ACTION": "get-args", "COMP_WORDS": words, "COMP_CWORD": str(len(shlex.split(words)) - 1),
           "_TYPER_COMPLETE_ARGS": words.replace('""', '')}
    result = subprocess.run([sys.executable, "-m", "codedown"], cwd=tmp_path,
                            env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_root_completion_and_no_side_effects(tmp_path, shell):
    (tmp_path / "notes.md").write_text("# Notes", encoding="utf-8")
    (tmp_path / "my notes.md").write_text("# Notes", encoding="utf-8")
    (tmp_path / "other.txt").write_text("text", encoding="utf-8")
    (tmp_path / "folder").mkdir()
    output = complete(tmp_path, 'code-down ""', shell)
    assert "convert" in output and "notes.md" in output and "my notes.md" in output
    assert "folder/" in output and "other.txt" not in output
    assert not list(tmp_path.glob("*.pdf"))


@pytest.mark.parametrize("words, expected", [
    ("code-down no", "notes.md"),
    ("code-down convert no", "notes.md"),
    ("code-down notes.md --st", "--style"),
    ("code-down --st", "--style"),
    ("code-down notes.md --style da", "dark"),
    ("code-down -s da", "dark"),
    ("code-down config set-theme li", "light"),
    ("code-down notes.md --output fo", "folder/"),
    ("code-down notes.md fo", "folder/"),
])
def test_context_completion(tmp_path, words, expected):
    (tmp_path / "notes.md").write_text("# Notes", encoding="utf-8")
    (tmp_path / "folder").mkdir()
    assert expected in complete(tmp_path, words)
    assert not list(tmp_path.glob("*.pdf"))


@pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
def test_completion_script(shell, monkeypatch):
    monkeypatch.setenv("_TYPER_COMPLETE_TEST_DISABLE_SHELL_DETECTION", "1")
    from typer.testing import CliRunner
    from codedown.cli import app
    result = CliRunner().invoke(app, ["--show-completion", shell])
    assert result.exit_code == 0, result.output
    assert "code-down" in result.output
