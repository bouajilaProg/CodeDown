import base64
from io import BytesIO
import json
import re
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest
from pypdf import PdfReader
from typer.testing import CliRunner

from codedown.preview import create_preview_server
from codedown.converter import RenderOptions
from codedown.themes import get_all_themes


@pytest.fixture
def preview(tmp_path):
    source = tmp_path / "notes.md"
    source.write_text("# Preview\n\n```python\nprint('hello')\n```", encoding="utf-8")
    (tmp_path / "image.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    server = create_preview_server(source, options=RenderOptions(title="Preview export", page_size="Letter"))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}", source
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_render_and_source_reload(preview):
    url, source = preview
    with urlopen(url) as response:
        page = response.read().decode()
    config = json.loads(re.search(r'<script id="config" type="application/json">(.*?)</script>', page)[1])
    body = json.dumps(dict(markdown="# Browser edit\n\n```python\nprint(42)\n```", theme="nord")).encode()
    request = Request(url + "/api/render", data=body, headers={"X-Preview-Token": config["token"]})
    with urlopen(request) as response:
        data = json.load(response)
    assert "Browser edit" in data["html"] and 'class="highlight"' in data["html"]
    assert '<base href="/assets/">' in data["html"]
    assert "#2e3440" in data["css"]
    assert "Browser edit" not in source.read_text()
    source.write_text("# External edit")
    with urlopen(url + "/api/document") as response:
        assert json.load(response)["markdown"] == "# External edit"
    with urlopen(url + "/assets/image.svg") as response:
        assert response.headers["Content-Type"] == "image/svg+xml"


@pytest.mark.parametrize("endpoint", ["render", "download"])
def test_preview_rejects_traversal_and_unauthorized_render(preview, tmp_path, endpoint):
    url, source = preview
    outside = tmp_path.parent / "outside-preview.txt"
    outside.write_text("private")
    (tmp_path / "link.txt").symlink_to(outside)
    for route in ("/assets/../outside-preview.txt", "/assets/%2e%2e/outside-preview.txt", "/assets/link.txt"):
        with pytest.raises(HTTPError) as error:
            urlopen(url + route)
        assert error.value.code == 404
    with pytest.raises(HTTPError) as error:
        urlopen(Request(url + "/api/" + endpoint, data=b'{}'))
    assert error.value.code == 403


def test_download_pdf_uses_browser_edits_theme_options_and_local_images(preview, monkeypatch):
    import weasyprint
    url, source = preview
    original = source.read_bytes()
    existing_pdf = source.with_suffix(".pdf")
    existing_pdf.write_bytes(b"existing output")
    (source.parent / "pixel.png").write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aS1sAAAAASUVORK5CYII="))
    with urlopen(url) as response:
        config = json.loads(re.search(r'<script id="config" type="application/json">(.*?)</script>', response.read().decode())[1])
    html_class = weasyprint.HTML
    rendered = {}

    def capture_html(**kwargs):
        rendered.update(kwargs)
        return html_class(**kwargs)

    monkeypatch.setattr(weasyprint, "HTML", capture_html)
    markdown = "# Unsaved résumé\n\n![Local image](pixel.png)\n\n```python\nprint(42)\n```"
    request = Request(url + "/api/download", data=json.dumps(dict(markdown=markdown, theme="nord")).encode(),
                      headers={"X-Preview-Token": config["token"]})
    with urlopen(request) as response:
        assert response.headers["Content-Type"] == "application/pdf"
        pdf = PdfReader(BytesIO(response.read()))
    assert "Unsaved résumé" in pdf.pages[0].extract_text()
    assert "42" in pdf.pages[0].extract_text()
    assert pdf.metadata.title == "Preview export"
    assert float(pdf.pages[0].mediabox.width) == pytest.approx(612)
    assert list(pdf.pages[0].images)
    assert "#2e3440" in rendered["string"]
    assert "copy-code" not in rendered["string"]
    assert source.read_bytes() == original
    assert existing_pdf.read_bytes() == b"existing output"


def test_download_reports_export_errors(preview, monkeypatch):
    import weasyprint
    url, _ = preview
    with urlopen(url) as response:
        config = json.loads(re.search(r'<script id="config" type="application/json">(.*?)</script>', response.read().decode())[1])

    def fail_export(self):
        raise RuntimeError("Renderer unavailable")

    monkeypatch.setattr(weasyprint.HTML, "write_pdf", fail_export)
    request = Request(url + "/api/download", data=b'{"markdown":"# Export"}',
                      headers={"X-Preview-Token": config["token"]})
    with pytest.raises(HTTPError) as error:
        urlopen(request)
    assert error.value.code == 500
    assert "Renderer unavailable" in json.load(error.value)["error"]


@pytest.mark.parametrize("args", [["preview", "--no-open"], ["--preview"], ["convert", "--preview"]])
def test_preview_cli(args, tmp_path, monkeypatch):
    from codedown.cli import app
    import codedown.config as config
    import codedown.preview as preview_module
    monkeypatch.setattr(config, "CONFIG_FILE", tmp_path / "config.toml")
    source = tmp_path / "notes.md"
    source.write_text("# Notes")
    calls = []
    monkeypatch.setattr(preview_module, "run_preview", lambda *arguments: calls.append(arguments))
    result = CliRunner().invoke(app, [*args, str(source), "-s", "github"])
    assert result.exit_code == 0, result.output
    assert calls[0][0] == source and calls[0][1] == "github"
    assert not source.with_suffix(".pdf").exists()


def test_all_theme_styles_are_valid():
    themes = get_all_themes()
    assert {"dracula", "nord", "solarized", "github", "gruvbox"} <= {theme.name for theme in themes}
    for theme in themes:
        css = theme.get_css()
        assert "--theme-bg:" in css and ".highlight" in css
