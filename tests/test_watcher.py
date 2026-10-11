import threading
import time

from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileModifiedEvent, FileMovedEvent

from codedown.watcher import _MarkdownHandler, local_resources


def test_burst_rebuilds_after_last_event_and_handles_replacement(tmp_path):
    calls = []
    done = threading.Event()
    source = tmp_path / "notes.md"
    def rebuild():
        calls.append(time.monotonic())
        done.set()
    handler = _MarkdownHandler(source, rebuild, debounce=0.08)
    try:
        handler.on_any_event(FileModifiedEvent(str(source)))
        time.sleep(0.04)
        handler.on_any_event(FileMovedEvent(str(tmp_path / "temp"), str(source)))
        assert not done.wait(0.04)
        assert done.wait(2)
        assert len(calls) == 1
        done.clear()
        handler.on_any_event(FileCreatedEvent(str(source)))
        assert done.wait(2)
        done.clear()
        handler.on_any_event(FileDeletedEvent(str(source)))
        assert done.wait(2)
    finally:
        handler.close()


def test_assets_rebuild_and_unrelated_files_do_not(tmp_path):
    done = threading.Event()
    source = tmp_path / "notes.md"
    image = tmp_path / "assets" / "my image.png"
    handler = _MarkdownHandler(source, done.set, debounce=0.02)
    try:
        resources = local_resources('![image](assets/my%20image.png)\n<img src="../outside.png">\n![remote](https://example.com/a.png)', source)
        assert resources == {image.resolve(), (tmp_path.parent / "outside.png").resolve()}
        handler.set_resources(resources)
        handler.on_any_event(FileModifiedEvent(str(tmp_path / "unrelated.md")))
        assert not done.wait(0.05)
        handler.on_any_event(FileModifiedEvent(str(image)))
        assert done.wait(2)
    finally:
        handler.close()


def test_changes_during_render_schedule_serial_rebuild(tmp_path):
    started = threading.Event()
    release = threading.Event()
    twice = threading.Event()
    calls = []
    def rebuild():
        calls.append(1)
        if len(calls) == 1:
            started.set()
            release.wait(2)
        else:
            twice.set()
    source = tmp_path / "notes.md"
    handler = _MarkdownHandler(source, rebuild, debounce=0.01)
    try:
        handler.on_any_event(FileModifiedEvent(str(source)))
        assert started.wait(2)
        handler.on_any_event(FileModifiedEvent(str(source)))
        release.set()
        assert twice.wait(2)
        assert len(calls) == 2
    finally:
        release.set()
        handler.close()


def test_failed_pdf_render_preserves_output_and_cleans_temp(tmp_path, monkeypatch):
    from codedown.converter import ConverterEngine
    import weasyprint
    output = tmp_path / "notes.pdf"
    output.write_bytes(b"previous valid PDF")
    def fail(self, target, **kwargs):
        from pathlib import Path
        Path(target).write_bytes(b"incomplete PDF")
        raise RuntimeError("render failed")
    monkeypatch.setattr(weasyprint.HTML, "write_pdf", fail)
    import pytest
    with pytest.raises(RuntimeError, match="render failed"):
        ConverterEngine("# Notes").convert_to_pdf(str(output))
    assert output.read_bytes() == b"previous valid PDF"
    assert list(tmp_path.iterdir()) == [output]
