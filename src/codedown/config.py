import json
import os
import sys
from dataclasses import fields
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

from codedown.converter import RenderOptions

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "codedown"
CONFIG_FILE = CONFIG_DIR / "config.toml"
PROJECT_CONFIG_NAME = "codedown.toml"


def validate_config(config: dict) -> dict:
    allowed = {field.name for field in fields(RenderOptions)} | {"default_theme", "overwrite"}
    unknown = set(config) - allowed
    if unknown:
        raise ValueError("Unknown configuration keys: " + ", ".join(sorted(unknown)))
    if "default_theme" in config:
        from codedown.themes import get_theme_by_name
        if not isinstance(config["default_theme"], str):
            raise ValueError("default_theme must be a string")
        get_theme_by_name(config["default_theme"])
    if "overwrite" in config and not isinstance(config["overwrite"], bool):
        raise ValueError("overwrite must be true or false")
    RenderOptions(**{key: value for key, value in config.items()
                     if key not in {"default_theme", "overwrite"}})
    return config


def _read_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        with path.open("rb") as file:
            return validate_config(tomllib.load(file))
    except (OSError, ValueError, TypeError) as error:
        raise ValueError(f"Cannot read configuration '{path}': {error}") from error


def find_project_config(directory: Path) -> Optional[Path]:
    directory = directory.resolve()
    for parent in (directory, *directory.parents):
        candidate = parent / PROJECT_CONFIG_NAME
        if candidate.exists():
            return candidate
    return None


def load_config(project_dir: Optional[Path] = None) -> dict:
    config = _read_config(CONFIG_FILE)
    if project_dir is not None:
        project_file = find_project_config(project_dir)
        if project_file:
            config.update(_read_config(project_file))
    return config


def save_config(config: dict) -> None:
    validate_config(config)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines = []
    for key, value in config.items():
        # JSON strings share TOML basic-string escaping for these scalar values.
        serialized = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key} = {serialized}")
    CONFIG_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def get_default_theme() -> str:
    return load_config(Path.cwd()).get("default_theme", "dark")


def set_default_theme(theme_name: str) -> None:
    config = load_config()
    config["default_theme"] = theme_name
    save_config(config)
