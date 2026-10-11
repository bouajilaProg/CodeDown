import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import zipfile

from pypdf import PdfReader
import pytest


def command_env(tmp_path):
    return {**os.environ, "XDG_CONFIG_HOME": str(tmp_path / "config")}


@pytest.mark.parametrize("arguments", [
    ["my notes"], ["my notes.md"], ["convert", "my notes.md"],
    ["--page-size=Letter", "my notes.md"], ["--", "my notes.md"],
])
def test_actual_entrypoint(tmp_path, arguments):
    (tmp_path / "my notes.md").write_text("# Direct conversion\n\nWorking.", encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "codedown", *arguments], cwd=tmp_path,
                            env=command_env(tmp_path), capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    output = tmp_path / "my notes.pdf"
    assert "Working." in PdfReader(output).pages[0].extract_text()
    assert "PDF successfully created" in result.stdout


def test_real_watch_replacement_and_external_resource(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    image = tmp_path / "image.svg"
    image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"><rect width="20" height="20" fill="red"/></svg>', encoding="utf-8")
    source = docs / "notes.md"
    source.write_text("# Original\n\n![image](../image.svg)", encoding="utf-8")
    log = tmp_path / "watch.log"
    def wait_for_builds(count):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            text = log.read_text(encoding="utf-8")
            assert "[watch] Error" not in text, text
            if text.count("[watch] Rebuilt:") >= count:
                return
            assert process.poll() is None, text
            time.sleep(0.05)
        pytest.fail("Watch did not rebuild: " + log.read_text(encoding="utf-8"))
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.Popen([sys.executable, "-m", "codedown", str(source), "--watch", "-s", "print"],
                                   env=command_env(tmp_path), stdout=stream, stderr=stream)
        try:
            wait_for_builds(1)
            replacement = docs / "replacement.tmp"
            replacement.write_text("# Changed\n\n![image](../image.svg)", encoding="utf-8")
            os.replace(replacement, source)
            wait_for_builds(2)
            output = source.with_suffix(".pdf")
            assert "Changed" in PdfReader(output).pages[0].extract_text()
            previous = output.read_bytes()
            image.write_text(image.read_text(encoding="utf-8").replace('fill="red"', 'fill="blue"'), encoding="utf-8")
            wait_for_builds(3)
            assert output.read_bytes() != previous
        finally:
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    assert process.returncode == 0, log.read_text(encoding="utf-8")


def test_distribution_contains_all_themes(tmp_path):
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(tmp_path)],
                            cwd=root, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    with zipfile.ZipFile(next(tmp_path.glob("*.whl"))) as wheel:
        files = set(wheel.namelist())
        for name in ("light", "dark", "print"):
            assert f"codedown/assets/themes/{name}.toml" in files
            assert f"codedown/assets/themes/{name}.css" in files
        assert "codedown/assets/themes/base.css" in files
        assert "codedown/completion.py" in files
        entrypoints = next(name for name in files if name.endswith("entry_points.txt"))
        assert b"code-down = codedown.__main__:main" in wheel.read(entrypoints)
