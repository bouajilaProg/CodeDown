from pygments.formatters import HtmlFormatter
from codedown import themes
from codedown.paths import THEMES_DIR
from codedown.themes import Theme


class ConverterEngine:
    def __init__(self, markdown_text: str):
        self.markdown_text = markdown_text

    def convert_to_html(self) -> str:
        import markdown
        from markdown.extensions.codehilite import CodeHiliteExtension
        from markdown.extensions.tables import TableExtension

        html = markdown.markdown(
            self.markdown_text,
            extensions=[
                "fenced_code",
                CodeHiliteExtension(linenums=False, css_class="highlight"),
                TableExtension(),
            ],
        )
        return html

    def applyTheme(self, html_content: str, theme: Theme) -> str:

        return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
                    <title>Markdown Preview</title><style>{theme.get_css()}
                    </style></head>
                    <body>{html_content}</body></html>"""

    def convert_to_pdf(self, output_pdf_path: str, style: str = "DARK"):
        from weasyprint import HTML, CSS

        html_content = self.convert_to_html()
        full_html = self.applyTheme(
            html_content, Theme.from_str(style))

        # Write PDF with the same CSS
        HTML(string=full_html).write_pdf(
            output_pdf_path,
        )
