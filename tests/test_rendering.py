import base64

from pypdf import PdfReader
import pytest

from codedown.converter import ConverterEngine, RenderOptions


def test_real_pdf_images_unicode_tables_and_metadata(tmp_path, caplog):
    source = tmp_path / "document.md"
    (tmp_path / "pixel.png").write_bytes(base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aS1sAAAAASUVORK5CYII="))
    markdown = "# Résumé\n\n![Image](pixel.png)\n\n| Name | Value |\n|---|---|\n| café | 42 |\n\n```python\nprint('hello')\n```"
    options = RenderOptions(page_size="Letter", title="Guide & Notes", author="A. Writer", toc=True)
    output = tmp_path / "document.pdf"
    ConverterEngine(markdown, source, options).convert_to_pdf(str(output), "print")
    pdf = PdfReader(output)
    assert pdf.metadata.title == "Guide & Notes"
    assert pdf.metadata.author == "A. Writer"
    assert float(pdf.pages[0].mediabox.width) == pytest.approx(612)
    text = "\n".join(page.extract_text() for page in pdf.pages)
    assert "Contents" in text and "café" in text and "hello" in text
    assert any(list(page.images) for page in pdf.pages)
    assert "Failed to load image" not in caplog.text


def test_multipage_code_headers_and_numbers(tmp_path):
    markdown = "# Code\n\n```text\n" + "\n".join(f"line {i:03d}" for i in range(150)) + "\n```"
    output = tmp_path / "long.pdf"
    ConverterEngine(markdown, options=RenderOptions(page_numbers=True, header="My header", footer="My footer")).convert_to_pdf(str(output), "print")
    pdf = PdfReader(output)
    assert len(pdf.pages) > 1
    assert "line 149" in pdf.pages[-1].extract_text()
    for index, page in enumerate(pdf.pages, 1):
        text = page.extract_text()
        assert "My header" in text and "My footer" in text
        assert f"Page {index} of {len(pdf.pages)}" in text


@pytest.mark.parametrize("kwargs", [{"margin": "bad; color:red"}, {"page_size": "unknown"}, {"toc": "yes"}])
def test_invalid_render_settings(kwargs):
    with pytest.raises(ValueError):
        RenderOptions(**kwargs)


def test_metadata_is_escaped():
    from codedown.themes import get_theme_by_name
    html = ConverterEngine("# Hello", options=RenderOptions(title="<script>", author='" onclick="x')).apply_theme("<p>Hello</p>", get_theme_by_name("print"))
    assert "&lt;script&gt;" in html
    assert 'content="&quot; onclick=&quot;x"' in html
