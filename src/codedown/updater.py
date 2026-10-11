import hashlib
import os
from pathlib import Path
import re
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


def _binary_asset_name() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    architecture = {"amd64": "x86_64", "x64": "x86_64", "arm64": "aarch64"}.get(machine, machine)
    suffix = ".exe" if system == "windows" else ""
    return f"code-down-{system}-{architecture}{suffix}"


def _asset_checksum(asset: dict, release: dict) -> str:
    digest = asset.get("digest")
    if digest:
        if not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
            raise ValueError("Release asset has an invalid SHA-256 digest")
        return digest.split(":", 1)[1].lower()
    checksum_asset = next((item for item in release.get("assets", [])
                           if item["name"] == asset["name"] + ".sha256"), None)
    if checksum_asset is None:
        raise ValueError("Release has no SHA-256 checksum; the current binary was kept")
    with requests.get(checksum_asset["browser_download_url"], timeout=15) as response:
        response.raise_for_status()
        checksum = response.text.split()[0] if response.text.split() else ""
    if not re.fullmatch(r"[0-9a-fA-F]{64}", checksum):
        raise ValueError("Release checksum file is invalid")
    return checksum.lower()


def _install_binary(asset: dict, release: dict, destination: Path):
    """Verify before replacement; stage on the destination filesystem."""
    checksum = _asset_checksum(asset, release)
    destination = destination.resolve()
    backup = destination.with_name(destination.name + ".backup")
    fd, temporary = tempfile.mkstemp(prefix=".code-down-update-", dir=destination.parent)
    backup_temp = None
    try:
        hasher = hashlib.sha256()
        with os.fdopen(fd, "wb") as file:
            with requests.get(asset["browser_download_url"], stream=True, timeout=60) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    hasher.update(chunk)
            file.flush()
            os.fsync(file.fileno())
        if hasher.hexdigest() != checksum:
            raise ValueError("Downloaded binary failed SHA-256 verification; current binary was kept")
        os.chmod(temporary, destination.stat().st_mode | stat.S_IEXEC)
        backup_fd, backup_temp = tempfile.mkstemp(prefix=".code-down-backup-", dir=destination.parent)
        os.close(backup_fd)
        shutil.copy2(destination, backup_temp)
        os.replace(backup_temp, backup)
        os.replace(temporary, destination)
        return backup
    finally:
        Path(temporary).unlink(missing_ok=True)
        if backup_temp:
            Path(backup_temp).unlink(missing_ok=True)


def update_via_binary():
    """Update only a matching, verified standalone binary."""
    typer.echo(f"Current version: {get_current_version()}")
    typer.echo("Checking GitHub Releases for updates...")
    try:
        release = get_latest_github_release()
        tag = release.get("tag_name", "unknown")
        typer.echo(f"Latest release: {tag}")
        expected = _binary_asset_name()
        asset = next((item for item in release.get("assets", []) if item["name"] == expected), None)
        if asset is None:
            raise ValueError(f"No binary found for {expected}. Install a matching release or use pip.")
        typer.echo(f"Downloading {asset['name']}...")
        # PyInstaller sets sys.executable to the launched standalone executable.
        destination = Path(sys.executable)
        backup = _install_binary(asset, release, destination)
        typer.echo(f"Updated binary at {destination}; previous binary: {backup}")
    except (requests.RequestException, OSError, ValueError) as error:
        typer.echo(f"Error updating binary: {error}", err=True)
        raise typer.Exit(code=1) from error


def run_update():
    """Auto-detect installation method and update accordingly."""
    if is_pyinstaller_bundle():
        typer.echo("Detected: standalone binary (PyInstaller)")
        update_via_binary()
    else:
        typer.echo("Detected: pip-installed package")
        update_via_pip()
