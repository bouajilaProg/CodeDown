import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from pygments.formatters import HtmlFormatter
from weasyprint import HTML, CSS


class ConverterEngine:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text

    def convert_to_html(self) -> str:
        html = markdown.markdown(
            self.markdown_text,
            extensions=[
                "fenced_code",
                CodeHiliteExtension(linenums=False, css_class="highlight"),
            ],
        )
        return html

    def get_theme_css(self, style: str = "monokai", theme_file_path: str = "") -> str:
        css = ""
        with open(theme_file_path, "r", encoding="utf-8") as theme_file:
            css += "\n" + theme_file.read()
        return HtmlFormatter(style=style).get_style_defs(".highlight") + css

    def wrap_html(self, html_content: str, style: str = "monokai") -> str:
        css = self.get_theme_css(style)
        return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8">
                <title>Markdown Preview</title>
                <style>
                    {css}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>"""
