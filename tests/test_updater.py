import hashlib
import os
from pathlib import Path

import pytest

from codedown import updater


class Response:
    def __init__(self, content=b"new binary", error=None):
        self.content = content
        self.text = content.decode()
        self.error = error
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def raise_for_status(self):
        if self.error:
            raise self.error
    def iter_content(self, chunk_size):
        yield self.content


def asset(content=b"new binary"):
    return {"name": "code-down-linux-x86_64", "browser_download_url": "https://example.com/binary",
            "digest": "sha256:" + hashlib.sha256(content).hexdigest()}


@pytest.mark.parametrize("system,machine,name", [
    ("Linux", "x86_64", "code-down-linux-x86_64"),
    ("Linux", "arm64", "code-down-linux-aarch64"),
    ("Windows", "AMD64", "code-down-windows-x86_64.exe"),
    ("Darwin", "arm64", "code-down-darwin-aarch64"),
])
def test_platform_asset_names(monkeypatch, system, machine, name):
    monkeypatch.setattr(updater.platform, "system", lambda: system)
    monkeypatch.setattr(updater.platform, "machine", lambda: machine)
    assert updater._binary_asset_name() == name


def test_verified_install_keeps_backup_and_mode(tmp_path, monkeypatch):
    destination = tmp_path / "code-down"
    destination.write_bytes(b"old binary")
    destination.chmod(0o755)
    monkeypatch.setattr(updater.requests, "get", lambda *args, **kwargs: Response())
    backup = updater._install_binary(asset(), {}, destination)
    assert destination.read_bytes() == b"new binary"
    assert backup.read_bytes() == b"old binary"
    assert destination.stat().st_mode & 0o777 == 0o755
    assert sorted(path.name for path in tmp_path.iterdir()) == ["code-down", "code-down.backup"]


@pytest.mark.parametrize("failure", ["checksum", "download", "replacement", "missing_digest"])
def test_failure_preserves_binary_and_cleans_staging(tmp_path, monkeypatch, failure):
    destination = tmp_path / "code-down"
    destination.write_bytes(b"old binary")
    selected = asset()
    error = None
    if failure == "checksum":
        selected["digest"] = "sha256:" + "0" * 64
    elif failure == "download":
        error = updater.requests.ConnectionError("offline")
    elif failure == "missing_digest":
        selected.pop("digest")
    elif failure == "replacement":
        original_replace = os.replace
        def replace(source, target):
            if Path(target) == destination:
                raise PermissionError("cannot replace")
            return original_replace(source, target)
        monkeypatch.setattr(updater.os, "replace", replace)
    monkeypatch.setattr(updater.requests, "get", lambda *args, **kwargs: Response(error=error))
    with pytest.raises((ValueError, OSError, updater.requests.RequestException)):
        updater._install_binary(selected, {}, destination)
    assert destination.read_bytes() == b"old binary"
    assert not list(tmp_path.glob(".code-down-*"))


def test_checksum_file_fallback(monkeypatch):
    selected = asset()
    checksum = selected.pop("digest").split(":")[1]
    release = {"assets": [{"name": selected["name"] + ".sha256", "browser_download_url": "checksum"}]}
    monkeypatch.setattr(updater.requests, "get", lambda *args, **kwargs: Response((checksum + "  binary\n").encode()))
    assert updater._asset_checksum(selected, release) == checksum


def test_wrong_platform_never_downloads(monkeypatch):
    monkeypatch.setattr(updater, "get_latest_github_release", lambda: {"assets": [{"name": "code-down-darwin-aarch64"}]})
    monkeypatch.setattr(updater, "_binary_asset_name", lambda: "code-down-linux-x86_64")
    def unexpected(*args, **kwargs):
        pytest.fail("Should not download a mismatched asset")
    monkeypatch.setattr(updater.requests, "get", unexpected)
    import typer
    with pytest.raises(typer.Exit):
        updater.update_via_binary()
