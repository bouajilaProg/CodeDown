import markdown


class ConverterEngine:
    def __init__(self, markdown_text):
        self.markdown_text = markdown_text

    def convert_to_html(self):
        html = markdown.markdown(self.markdown_text)
        return html
