import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile

import requests
import typer

GITHUB_REPO = "bouajilaProg/CodeDown"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
PYPI_PACKAGE_NAME = "code-down"


def get_current_version() -> str:
    from importlib.metadata import version

    try:
        return version(PYPI_PACKAGE_NAME)
    except Exception:
        return "unknown"


def is_pyinstaller_bundle() -> bool:
    return getattr(sys, "_MEIPASS", None) is not None


def get_latest_github_release() -> dict:
    response = requests.get(GITHUB_API_URL, timeout=15)
    response.raise_for_status()
    return response.json()


def update_via_pip():
    """Update using pip install --upgrade."""
    current = get_current_version()
    typer.echo(f"Current version: {current}")
    typer.echo("Checking PyPI for updates...")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", PYPI_PACKAGE_NAME],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        typer.echo(f"Error updating via pip:\n{result.stderr}", err=True)
        raise typer.Exit(code=1)

    new_version = get_current_version()
    if new_version == current:
        typer.echo("Already up to date.")
    else:
        typer.echo(f"Updated: {current} → {new_version}")


def update_via_binary():
    """Update the standalone binary from GitHub Releases."""
    current = get_current_version()
    typer.echo(f"Current version: {current}")
    typer.echo("Checking GitHub Releases for updates...")

    try:
        release = get_latest_github_release()
    except Exception as e:
        typer.echo(f"Error fetching release info: {e}", err=True)
        raise typer.Exit(code=1)

    tag = release.get("tag_name", "unknown")
    typer.echo(f"Latest release: {tag}")

    # Find the Linux binary asset
    system = platform.system().lower()
    asset = None
    for a in release.get("assets", []):
        name = a["name"].lower()
        if system in name or "code-down" in name:
            asset = a
            break

    if asset is None:
        typer.echo(
            f"No binary found for {system} in release {tag}. "
            "Try updating via pip: pip install --upgrade code-down",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(f"Downloading {asset['name']}...")

    response = requests.get(asset["browser_download_url"], stream=True, timeout=60)
    response.raise_for_status()

    current_exe = os.path.realpath(sys.executable)
    if is_pyinstaller_bundle():
        current_exe = os.path.realpath(sys.argv[0])

    # Write to a temp file, then replace the current binary
    fd, tmp_path = tempfile.mkstemp(prefix="code-down-update-")
    try:
        with os.fdopen(fd, "wb") as tmp:
            for chunk in response.iter_content(chunk_size=8192):
                tmp.write(chunk)

        # Make executable
        os.chmod(tmp_path, os.stat(tmp_path).st_mode | stat.S_IEXEC)

        # Replace the current binary
        shutil.move(tmp_path, current_exe)
        typer.echo(f"Updated binary at {current_exe}")
    except PermissionError:
        typer.echo(
            f"Permission denied. Try: sudo code-down update",
            err=True,
        )
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise typer.Exit(code=1)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def run_update():
    """Auto-detect installation method and update accordingly."""
    if is_pyinstaller_bundle():
        typer.echo("Detected: standalone binary (PyInstaller)")
        update_via_binary()
    else:
        typer.echo("Detected: pip-installed package")
        update_via_pip()
