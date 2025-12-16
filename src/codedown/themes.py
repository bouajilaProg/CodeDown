from enum import Enum
from pygments.formatters import HtmlFormatter
from codedown.paths import THEMES_DIR


class Theme(Enum):
    DARK = ("dark.css", "monokai")
    LIGHT = ("light.css", "default")

    def __init__(self, css_file: str, codeTheme: str):
        self.css_file = css_file
        self.codeTheme = codeTheme

    def get_css(self) -> str:
        css = ""

        theme_path = THEMES_DIR / self.css_file
        if theme_path.exists():
            css += "\n" + theme_path.read_text(encoding="utf-8")

        css = HtmlFormatter(style=self.codeTheme).get_style_defs(
            ".highlight") + css

        # add the base theme
        base_theme_path = THEMES_DIR / "base.css"
        if base_theme_path.exists():
            css += "\n" + base_theme_path.read_text(encoding="utf-8")
        return css

    @classmethod
    def from_str(cls, name: str):
        name = name.strip().lower()
        for theme in cls:
            if theme.name.lower() == name:
                return theme
        exit(f"Error: Unknown theme '{name}'")
