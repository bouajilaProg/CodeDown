import threading
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Callable
from urllib.parse import unquote, urlsplit

import typer
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def local_resources(markdown_text: str, source_file: Path) -> set[Path]:
    """Find local resources in rendered Markdown, including HTML image tags."""
    from codedown.converter import ConverterEngine
    resources = set()

    class Resources(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for name, value in attrs:
                if not value or not (name in {"src", "poster"} or (tag == "link" and name == "href")):
                    continue
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path:
                    continue
                resources.add((source_file.parent / unquote(url.path)).resolve())

    Resources().feed(ConverterEngine(markdown_text).convert_to_html())
    return resources


class _MarkdownHandler(FileSystemEventHandler):
    """One worker rebuilds after the last relevant event in a burst."""
    def __init__(self, target_file: Path, on_change: Callable[[], None], debounce: float = 0.3):
        super().__init__()
        self.target_file = target_file.resolve()
        self.on_change = on_change
        self.debounce = debounce
        self._targets = {self.target_file}
        self._condition = threading.Condition()
        self._deadline = None
        self._stopped = False
        self._worker = threading.Thread(target=self._run, daemon=True)
        self._worker.start()

    def set_resources(self, resources: set[Path]):
        with self._condition:
            self._targets = {self.target_file, *resources}

    def on_any_event(self, event):
        if event.is_directory or event.event_type not in {"modified", "created", "moved", "deleted"}:
            return
        paths = {Path(event.src_path).resolve()}
        if getattr(event, "dest_path", None):
            paths.add(Path(event.dest_path).resolve())
        with self._condition:
            if paths & self._targets and not self._stopped:
                self._deadline = time.monotonic() + self.debounce
                self._condition.notify()

    def _run(self):
        while True:
            with self._condition:
                while not self._stopped:
                    if self._deadline is None:
                        self._condition.wait()
                    else:
                        remaining = self._deadline - time.monotonic()
                        if remaining <= 0:
                            self._deadline = None
                            break
                        self._condition.wait(remaining)
                if self._stopped:
                    return
            # Serial worker: an event during rendering schedules another rebuild.
            self.on_change()

    def close(self):
        with self._condition:
            self._stopped = True
            self._condition.notify()
        self._worker.join()


def watch_and_convert(input_file: Path, output_file: Path, style: str, render_options=None):
    """Watch Markdown and referenced local resources; preserve PDF on failures."""
    from codedown.converter import ConverterEngine

    input_file = input_file.resolve()
    observer = Observer()
    watched_dirs = set()
    rebuild_lock = threading.Lock()

    def update_resources(markdown_text):
        resources = local_resources(markdown_text, input_file)
        handler.set_resources(resources)
        for directory in {input_file.parent, *(path.parent for path in resources)}:
            # Watch nearest existing ancestor, including resources created later.
            while not directory.is_dir() and directory != directory.parent:
                directory = directory.parent
            if directory not in watched_dirs:
                observer.schedule(handler, str(directory), recursive=True)
                watched_dirs.add(directory)

    def rebuild():
        with rebuild_lock:
            _rebuild()

    def _rebuild():
        try:
            markdown_text = input_file.read_text(encoding="utf-8")
            update_resources(markdown_text)
            ConverterEngine(markdown_text, input_file, render_options).convert_to_pdf(str(output_file), style=style)
            typer.echo(f"[watch] Rebuilt: {output_file}")
        except Exception as error:
            typer.echo(f"[watch] Error: {error}", err=True)

    handler = _MarkdownHandler(input_file, rebuild)
    try:
        observer.schedule(handler, str(input_file.parent), recursive=True)
        watched_dirs.add(input_file.parent)
        observer.start()
        rebuild()
        typer.echo(f"[watch] Watching {input_file} and local resources... (Ctrl+C to stop)")
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        typer.echo("\n[watch] Stopped.")
    finally:
        observer.stop()
        observer.join()
        handler.close()
