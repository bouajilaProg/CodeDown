from pathlib import Path
from pygments.formatters import HtmlFormatter


class ConverterEngine:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text

    def convert_to_html(self) -> str:
        import markdown
        from markdown.extensions.codehilite import CodeHiliteExtension

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
        if theme_file_path:
            path = Path(theme_file_path)
            if not path.is_absolute():
                path = Path.cwd() / path
            if path.exists():
                css += "\n" + path.read_text(encoding="utf-8")
                print(f"Loaded theme CSS from: {path}")
        return HtmlFormatter(style=style).get_style_defs(".highlight") + css

    def wrap_html(self, html_content: str, style: str = "monokai") -> str:
        css = self.get_theme_css(style, "./styles/dark.css")
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

    def convert_to_pdf(self, output_pdf_path: str, style: str = "monokai"):
        from weasyprint import HTML, CSS

        html_content = self.convert_to_html()
        full_html = self.wrap_html(html_content, style)
        HTML(string=full_html).write_pdf(
            output_pdf_path,
            stylesheets=[
                CSS(string=self.get_theme_css(style, "./styles/dark.css"))]
        )
