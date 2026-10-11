from pathlib import Path

import pytest
from typer.testing import CliRunner

from codedown import config
from codedown.cli import app


@pytest.fixture(autouse=True)
def isolated_config(monkeypatch, tmp_path):
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path / "user")
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "user" / "config.toml")
    monkeypatch.chdir(tmp_path)


def test_toml_round_trip_with_escaping():
    values = {"header": 'Quote " / slash \\ / newline\n / café', "toc": True, "margin": "12mm"}
    config.save_config(values)
    assert config.load_config() == values


@pytest.mark.parametrize("values", [{"unknown": "x"}, {"page_size": "bad"},
                                      {"overwrite": "false"}, {"font": 3},
                                      {"page_size": ["A4"]}, {"margin": 20},
                                      {"default_theme": "missing"}])
def test_invalid_values_are_not_saved(values):
    with pytest.raises(ValueError):
        config.save_config(values)
    assert not config.CONFIG_FILE.exists()


def test_project_user_cli_precedence_and_explicit_false(tmp_path, monkeypatch):
    from codedown.converter import ConverterEngine
    config.save_config({"default_theme": "dark", "margin": "10mm", "toc": True})
    (tmp_path / "codedown.toml").write_text('default_theme = "print"\nmargin = "15mm"\npage_numbers = true\n', encoding="utf-8")
    folder = tmp_path / "nested"
    folder.mkdir()
    source = folder / "notes.md"
    source.write_text("# Notes", encoding="utf-8")
    captured = {}
    def fake(self, output_pdf_path, style="dark"):
        captured["options"] = self.options
        captured["style"] = style
    monkeypatch.setattr(ConverterEngine, "convert_to_pdf", fake)
    result = CliRunner().invoke(app, [str(source), "--margin", "25mm", "--no-toc"])
    assert result.exit_code == 0, result.output
    assert captured["style"] == "print"
    assert captured["options"].margin == "25mm"
    assert captured["options"].page_numbers is True
    assert captured["options"].toc is False
    assert config.load_config()["margin"] == "10mm"


def test_no_overwrite_and_explicit_override(tmp_path, monkeypatch):
    from codedown.converter import ConverterEngine
    source = tmp_path / "notes.md"
    source.write_text("# Notes", encoding="utf-8")
    output = source.with_suffix(".pdf")
    output.write_bytes(b"old PDF")
    config.save_config({"overwrite": False})
    result = CliRunner().invoke(app, [str(source)])
    assert result.exit_code == 1 and "--overwrite" in result.output
    assert output.read_bytes() == b"old PDF"
    monkeypatch.setattr(ConverterEngine, "convert_to_pdf", lambda self, path, style: Path(path).write_bytes(b"new PDF"))
    result = CliRunner().invoke(app, [str(source), "--overwrite"])
    assert result.exit_code == 0, result.output
    assert output.read_bytes() == b"new PDF"


def test_malformed_config_has_path_and_no_traceback(tmp_path):
    config.CONFIG_DIR.mkdir()
    config.CONFIG_FILE.write_text('default_theme = "unterminated', encoding="utf-8")
    source = tmp_path / "notes.md"
    source.write_text("# Notes", encoding="utf-8")
    result = CliRunner().invoke(app, [str(source)])
    assert result.exit_code == 1
    assert "Cannot read configuration" in result.output
    assert "Traceback" not in result.output
    assert not source.with_suffix(".pdf").exists()


def test_invalid_utf8(tmp_path):
    source = tmp_path / "notes.md"
    source.write_bytes(b"\xff")
    result = CliRunner().invoke(app, [str(source)])
    assert result.exit_code == 1
    assert "UTF-8" in result.output


@pytest.mark.parametrize("error", [PermissionError("permission denied"), ImportError("weasyprint missing"), OSError("libpango missing")])
def test_render_failures_are_friendly(tmp_path, monkeypatch, error):
    from codedown.converter import ConverterEngine
    source = tmp_path / "notes.md"
    source.write_text("# Notes", encoding="utf-8")
    def fail(*args, **kwargs):
        raise error
    monkeypatch.setattr(ConverterEngine, "convert_to_pdf", fail)
    result = CliRunner().invoke(app, [str(source)])
    assert result.exit_code == 1
    assert str(error) in result.output
    assert "Traceback" not in result.output


def test_config_set_validates_and_preserves_previous_values():
    runner = CliRunner()
    assert runner.invoke(app, ["config", "set", "page_size", "Letter"]).exit_code == 0
    assert runner.invoke(app, ["config", "set", "toc", "true"]).exit_code == 0
    assert config.load_config() == {"page_size": "Letter", "toc": True}
    assert runner.invoke(app, ["config", "set", "toc", "yes"]).exit_code == 1
    assert runner.invoke(app, ["config", "set-theme", "missing"]).exit_code == 1
    assert config.load_config() == {"page_size": "Letter", "toc": True}
