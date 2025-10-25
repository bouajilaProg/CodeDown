from pathlib import Path
from pygments.formatters import HtmlFormatter


class ConverterEngine:
    def __init__(self, markdown_text):
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

    def get_theme_css(self, style: str = "monokai", theme_file_path: str = "") -> str:
        css = ""
        # later addition: load custom css from file
#        if theme_file_path:
#            path = Path(theme_file_path)
#            if not path.is_absolute():
#                path = Path.cwd() / path
#            if path.exists():
#                css += "\n" + path.read_text(encoding="utf-8")

        css = """
                    
            @page {
            margin: 0;
            padding: 30px;
            }

            body {
            background-color: #1a1b26;
            color: #c0caf5;
            font-family: "Fira Code", "JetBrains Mono", Consolas, monospace;
            padding: 30px;
            margin: 0;
            line-height: 1.6;
            font-size: 16px;
            }

            h1,
            h2,
            h3,
            h4,
            h5,
            h6 {
            color: #7aa2f7;
            border-bottom: 1px solid #2f3549;
            padding-bottom: 0.2em;
            }

            a {
            color: #7dcfff;
            text-decoration: none;
            }

            a:hover {
            text-decoration: underline;
            }

            pre,
            code {
            font-family: "Fira Code", "JetBrains Mono", Consolas, monospace;
            }

            pre {
            background-color: #24283b !important;
            /* override Pygments */
            padding: 12px 16px;
            border-radius: 8px;
            overflow-x: auto;
            color: #c0caf5;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
            white-space: pre-wrap;
            word-wrap: break-word;
            }

            .highlight pre,
            .highlight {
            background: #24283b !important;
            color: #c0caf5 !important;
            }

            blockquote {
            border-left: 4px solid #565f89;
            margin: 1em 0;
            padding-left: 1em;
            color: #a9b1d6;
            background-color: #1f2335;
            }

            hr {
            border: none;
            border-top: 1px solid #3b4261;
            margin: 2em 0;
            }

            img {
            max-width: 100%;
            border-radius: 6px;
            }

            table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            }

            th,
            td {
            border: 1px solid #3b4261;
            padding: 8px 12px;
            text-align: left;
            }

            th {
            background-color: #2f3549;
            color: #bb9af7;
            }

        """
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
