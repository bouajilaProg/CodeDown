import sys
from pathlib import Path


def _assets_dir() -> Path:
    # When bundled by PyInstaller (onefile/onedir), data files are unpacked
    # under sys._MEIPASS.
    meipass = getattr(sys, "_MEIPASS", None)
    if getattr(sys, "frozen", False) and meipass:
        return Path(meipass) / "assets"

    return Path(__file__).resolve().parent / "assets"


ASSETS_DIR = _assets_dir()
THEMES_DIR = ASSETS_DIR / "themes"
