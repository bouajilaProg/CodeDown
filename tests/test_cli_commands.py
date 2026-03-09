import sys
import types
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def isolate_config(monkeypatch, tmp_path):
    import codedown.config as config

    cfg_dir = tmp_path / "cfg"
    monkeypatch.setattr(config, "CONFIG_DIR", cfg_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_dir / "config.toml")


@pytest.fixture()
def fake_inquirerpy(monkeypatch):
    class _Prompt:
        def __init__(self, value):
            self._value = value

        def execute(self):
            return self._value

    class _Inquirer:
        def __init__(self):
            self._next = "dark"

        def select(self, *args, **kwargs):
            return _Prompt(self._next)

    mod = types.ModuleType("InquirerPy")
    mod.inquirer = _Inquirer()
    monkeypatch.setitem(sys.modules, "InquirerPy", mod)
    return mod


@pytest.fixture()
def fake_pdf(monkeypatch):
    import codedown.converter as converter

    def _fake_convert_to_pdf(self, output_pdf_path: str, style: str = "dark"):
        out = Path(output_pdf_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"fake-pdf style={style}\n", encoding="utf-8")

    monkeypatch.setattr(
        converter.ConverterEngine, "convert_to_pdf", _fake_convert_to_pdf
    )


def test_help_short_flag(runner):
    from codedown.cli import app

    result = runner.invoke(app, ["-h"])
    assert result.exit_code == 0
    assert "convert" in result.output


def test_version_flag(runner, monkeypatch):
    from codedown import cli

    monkeypatch.setattr(cli, "_get_package_version", lambda: "2.0.0")
    result = runner.invoke(cli.app, ["-v"])
    assert result.exit_code == 0
    assert result.output.strip() == "2.0.0"


def test_themes_command_outputs_selected(runner, fake_inquirerpy, isolate_config):
    from codedown.cli import app
    from codedown.config import load_config

    result = runner.invoke(app, ["themes"])
    assert result.exit_code == 0
    assert "Default theme set" in result.output
    assert load_config().get("default_theme") == "dark"


def test_config_help(runner):
    from codedown.cli import app

    result = runner.invoke(app, ["config", "-h"])
    assert result.exit_code == 0
    assert "set-theme" in result.output


def test_config_set_theme_non_interactive(runner, isolate_config):
    from codedown.cli import app

    result = runner.invoke(app, ["config", "set-theme", "dark"])
    assert result.exit_code == 0
    assert "Default theme set" in result.output


def test_convert_positional_output_dir(runner, tmp_path, fake_pdf, isolate_config):
    from codedown.cli import app

    md = tmp_path / "note.md"
    md.write_text("# Hi\n", encoding="utf-8")

    out_dir = tmp_path / "temp"
    result = runner.invoke(app, ["convert", str(md), str(out_dir)])
    assert result.exit_code == 0

    expected_pdf = out_dir / "note.pdf"
    assert expected_pdf.exists()


def test_watch_invokes_watcher(runner, tmp_path, isolate_config, monkeypatch):
    from codedown.cli import app

    md = tmp_path / "note.md"
    md.write_text("# Hi\n", encoding="utf-8")

    called = {}

    def _fake_watch_and_convert(input_file, output_file, style):
        called["input"] = Path(input_file)
        called["output"] = Path(output_file)
        called["style"] = style

    import codedown.watcher as watcher

    monkeypatch.setattr(watcher, "watch_and_convert", _fake_watch_and_convert)

    result = runner.invoke(app, ["convert", "-w", str(md)])
    assert result.exit_code == 0
    assert called["input"].name == "note.md"
    assert called["output"].name == "note.pdf"


def test_update_command_calls_updater(runner, monkeypatch):
    from codedown.cli import app

    import codedown.updater as updater

    called = {"ok": False}

    def _fake_run_update():
        called["ok"] = True

    monkeypatch.setattr(updater, "run_update", _fake_run_update)
    result = runner.invoke(app, ["update"])
    assert result.exit_code == 0
    assert called["ok"] is True


def test_convert_positional_output_file(runner, tmp_path, fake_pdf, isolate_config):
    from codedown.cli import app

    md = tmp_path / "note.md"
    md.write_text("# Hi\n", encoding="utf-8")

    out_file = tmp_path / "out.pdf"
    result = runner.invoke(app, ["convert", str(md), str(out_file)])
    assert result.exit_code == 0

    assert out_file.exists()
