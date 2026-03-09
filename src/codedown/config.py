import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

CONFIG_DIR = Path.home() / ".config" / "codedown"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def save_config(config: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    for key, value in config.items():
        if isinstance(value, str):
            lines.append(f'{key} = "{value}"')
        elif isinstance(value, bool):
            lines.append(f"{key} = {'true' if value else 'false'}")
        elif isinstance(value, int):
            lines.append(f"{key} = {value}")
        else:
            lines.append(f'{key} = "{value}"')

    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_default_theme() -> str:
    config = load_config()
    return config.get("default_theme", "dark")


def set_default_theme(theme_name: str) -> None:
    config = load_config()
    config["default_theme"] = theme_name
    save_config(config)
