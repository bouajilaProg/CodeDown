from codedown.themes import Theme, get_theme_by_name


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

    def apply_theme(self, html_content: str, theme: Theme) -> str:
        return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
                    <title>Markdown Preview</title><style>{theme.get_css()}
                    </style></head>
                    <body>{html_content}</body></html>"""

    def convert_to_pdf(self, output_pdf_path: str, style: str = "dark"):
        from weasyprint import HTML

        html_content = self.convert_to_html()
        theme = get_theme_by_name(style)
        full_html = self.apply_theme(html_content, theme)

        HTML(string=full_html).write_pdf(output_pdf_path)
