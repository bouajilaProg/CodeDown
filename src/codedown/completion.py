"""Read-only completion for both explicit and implicit conversion."""
from pathlib import Path

from typer.core import TyperGroup

try:  # Typer 0.26+ bundles Click; older releases use the installed Click.
    from typer._click.shell_completion import CompletionItem
except ImportError:
    from click.shell_completion import CompletionItem


def _complete_paths(incomplete: str, markdown_only: bool = False) -> list[str]:
    expanded = Path(incomplete).expanduser()
    directory = expanded if incomplete.endswith("/") else expanded.parent
    prefix = "" if incomplete.endswith("/") else expanded.name
    display_dir = incomplete if incomplete.endswith("/") else incomplete[:len(incomplete) - len(prefix)]
    try:
        entries = sorted(directory.iterdir(), key=lambda path: path.name.lower())
        return [
            display_dir + entry.name + ("/" if entry.is_dir() else "")
            for entry in entries
            if entry.name.startswith(prefix)
            and (prefix.startswith(".") or not entry.name.startswith("."))
            and (not markdown_only or entry.is_dir() or entry.suffix.lower() in {".md", ".markdown", ""})
        ]
    except OSError:
        return []


def complete_paths(incomplete: str) -> list[str]:
    return _complete_paths(incomplete)


def complete_markdown(incomplete: str) -> list[str]:
    return _complete_paths(incomplete, markdown_only=True)


def complete_themes(incomplete: str) -> list[str]:
    from codedown.themes import get_all_themes
    return sorted(theme.name for theme in get_all_themes()
                  if theme.name.lower().startswith(incomplete.lower()))


def complete_page_sizes(incomplete: str) -> list[str]:
    return [size for size in ("A4", "A5", "Letter", "Legal")
            if size.lower().startswith(incomplete.lower())]


def complete_config_keys(incomplete: str) -> list[str]:
    from dataclasses import fields
    from codedown.converter import RenderOptions
    keys = {field.name for field in fields(RenderOptions)} | {"default_theme", "overwrite"}
    return sorted(key for key in keys if key.startswith(incomplete))


def complete_config_values(ctx, incomplete: str) -> list[str]:
    key = ctx.params.get("key")
    if key == "default_theme":
        return complete_themes(incomplete)
    if key == "page_size":
        return complete_page_sizes(incomplete)
    choices = []
    if key in {"overwrite", "wrap_code", "page_numbers", "toc"}:
        choices = ["true", "false"]
    elif key in {"font", "code_font"}:
        choices = ["sans-serif", "serif", "monospace"]
    return [value for value in choices if value.startswith(incomplete)]


class ShortcutGroup(TyperGroup):
    def parse_args(self, ctx, args):
        from codedown.__main__ import _rewrite_argv_for_implicit_convert
        args = _rewrite_argv_for_implicit_convert(["code-down", *args])[1:]
        return super().parse_args(ctx, args)

    def shell_complete(self, ctx, incomplete):
        results = super().shell_complete(ctx, incomplete)
        if incomplete.startswith("-"):
            command = self.get_command(ctx, "convert")
            if command is not None:
                known = {item.value for item in results}
                results.extend(item for item in command.shell_complete(ctx, incomplete)
                               if item.value not in known)
        else:
            results.extend(CompletionItem(path) for path in complete_markdown(incomplete))
        return results
