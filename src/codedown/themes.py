import sys
from dataclasses import dataclass
from pathlib import Path

from pygments.formatters import HtmlFormatter

from codedown.paths import THEMES_DIR

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib


@dataclass
class Theme:
    name: str
    css_file: str
    code_theme: str
    version: str

    def get_css(self) -> str:
        css = ""

        theme_path = THEMES_DIR / self.css_file
        if theme_path.exists():
            css += "\n" + theme_path.read_text(encoding="utf-8")

        css = HtmlFormatter(style=self.code_theme).get_style_defs(".highlight") + css

        base_theme_path = THEMES_DIR / "base.css"
        if base_theme_path.exists():
            css += "\n" + base_theme_path.read_text(encoding="utf-8")

        return css

    @classmethod
    def from_toml(cls, path: Path) -> "Theme":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(
            name=data["name"],
            css_file=data["css_file"],
            code_theme=data["code_theme"],
            version=data.get("version", "1.0.0"),
        )


def get_all_themes() -> list[Theme]:
    themes = []
    for toml_file in sorted(THEMES_DIR.glob("*.toml")):
        themes.append(Theme.from_toml(toml_file))
    return themes


def get_theme_by_name(name: str) -> Theme:
    name = name.strip().lower()
    for theme in get_all_themes():
        if theme.name.lower() == name:
            return theme

    available = ", ".join(t.name for t in get_all_themes())
    print(f"Error: Unknown theme '{name}'. Available: {available}")
    sys.exit(1)
