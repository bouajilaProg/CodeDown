import time
from pathlib import Path
from typing import Callable

import typer
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class _MarkdownHandler(FileSystemEventHandler):
    def __init__(self, target_file: Path, on_change: Callable[[], None]):
        super().__init__()
        self.target_file = target_file.resolve()
        self.on_change = on_change
        self._last_trigger = 0.0

    def on_modified(self, event):
        if event.is_directory:
            return

        if Path(event.src_path).resolve() != self.target_file:
            return

        # Debounce: ignore events within 1 second of each other
        now = time.time()
        if now - self._last_trigger < 1.0:
            return
        self._last_trigger = now

        self.on_change()


def watch_and_convert(
    input_file: Path,
    output_file: Path,
    style: str,
):
    """Watch a Markdown file and regenerate the PDF on every change."""
    from codedown.converter import ConverterEngine

    input_file = input_file.resolve()
    watch_dir = input_file.parent

    def rebuild():
        try:
            markdown_text = input_file.read_text(encoding="utf-8")
            converter = ConverterEngine(markdown_text)
            converter.convert_to_pdf(str(output_file), style=style)
            typer.echo(f"[watch] Rebuilt: {output_file}")
        except Exception as e:
            typer.echo(f"[watch] Error: {e}", err=True)

    # Initial build
    rebuild()
    typer.echo(f"[watch] Watching {input_file} for changes... (Ctrl+C to stop)")

    handler = _MarkdownHandler(input_file, rebuild)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        typer.echo("\n[watch] Stopped.")
    finally:
        observer.stop()
        observer.join()
