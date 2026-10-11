from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import re
from typing import Optional

from codedown.themes import Theme, get_theme_by_name


@dataclass
class RenderOptions:
    page_size: str = "A4"
    margin: str = "20mm"
    font: str = "sans-serif"
    code_font: str = "monospace"
    wrap_code: bool = True
    page_numbers: bool = False
    header: str = ""
    footer: str = ""
    toc: bool = False
    title: str = ""
    author: str = ""

    def __post_init__(self):
        if self.page_size not in {"A4", "A5", "Letter", "Legal"}:
            raise ValueError("page_size must be A4, A5, Letter, or Legal")
        if not re.fullmatch(r"(?:\d+(?:\.\d+)?)(?:mm|cm|in|pt|px)", self.margin):
            raise ValueError("margin must be a nonnegative length such as 20mm")
        for name in ("font", "code_font", "header", "footer", "title", "author"):
            if not isinstance(getattr(self, name), str):
                raise ValueError(f"{name} must be a string")
        for name in ("wrap_code", "page_numbers", "toc"):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be true or false")

    def get_css(self) -> str:
        quote = lambda value: json.dumps(value, ensure_ascii=False)
        font = self.font if self.font in {"sans-serif", "serif", "monospace"} else quote(self.font)
        code_font = self.code_font if self.code_font in {"sans-serif", "serif", "monospace"} else quote(self.code_font)
        page_content = '"Page " counter(page) " of " counter(pages)' if self.page_numbers else '""'
        return f"""
        @page {{ size: {self.page_size}; margin: {self.margin};
          @top-center {{ content: {quote(self.header)}; }}
          @bottom-left {{ content: {quote(self.footer)}; }}
          @bottom-right {{ content: {page_content}; }}
        }}
        html, body {{ font-family: {font}; padding: 0; }}
        pre, code {{ font-family: {code_font}; }}
        pre {{ white-space: {'pre-wrap' if self.wrap_code else 'pre'};
               overflow-wrap: {'anywhere' if self.wrap_code else 'normal'};
               word-wrap: {'break-word' if self.wrap_code else 'normal'};
               break-inside: auto; }}
        table {{ table-layout: fixed; overflow-wrap: anywhere; break-inside: auto; }}
        thead {{ display: table-header-group; }}
        tr {{ break-inside: avoid; }}
        .toc {{ break-after: page; }}
        """


class ConverterEngine:
    def __init__(self, markdown_text: str, source_path: Optional[Path] = None,
                 options: Optional[RenderOptions] = None):
        self.markdown_text = markdown_text
        self.source_path = Path(source_path).resolve() if source_path else None
        self.options = options or RenderOptions()

    def convert_to_html(self) -> str:
        import markdown
        from markdown.extensions.codehilite import CodeHiliteExtension
        from markdown.extensions.tables import TableExtension

        extensions = ["fenced_code", CodeHiliteExtension(linenums=False, css_class="highlight"),
                      TableExtension(), "toc"]
        document = markdown.Markdown(extensions=extensions)
        html = document.convert(self.markdown_text)
        if self.options.toc and document.toc_tokens:
            html = '<nav class="toc"><h2>Contents</h2>' + document.toc + '</nav>' + html
        return html

    def apply_theme(self, html_content: str, theme: Theme) -> str:
        title = self.options.title or (self.source_path.stem if self.source_path else "Markdown document")
        css = (theme.get_css() + self.options.get_css()).replace("</", "<\\/")
        return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
          <title>{escape(title)}</title><meta name="author" content="{escape(self.options.author, quote=True)}">
          <style>{css}</style></head><body>{html_content}</body></html>"""

    def convert_to_pdf(self, output_pdf_path: str, style: str = "dark"):
        from weasyprint import HTML

        full_html = self.apply_theme(self.convert_to_html(), get_theme_by_name(style))
        base_url = str(self.source_path.parent) if self.source_path else None
        HTML(string=full_html, base_url=base_url).write_pdf(output_pdf_path)
