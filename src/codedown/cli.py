from contextlib import contextmanager
from dataclasses import fields
from pathlib import Path
from typing import Optional

import typer

from codedown.converter import RenderOptions
from codedown.completion import ShortcutGroup, complete_markdown, complete_paths, complete_themes
from codedown.completion import complete_page_sizes, complete_config_keys, complete_config_values


def _get_package_version() -> str:
    try:
        from importlib.metadata import PackageNotFoundError, version

        return version("code-down")
    except Exception:
        return "unknown"


def _version_callback(value: bool):
    if not value:
        return
    typer.echo(_get_package_version())
    raise typer.Exit(0)


app = typer.Typer(
    name="code-down",
    help="Convert Markdown files into beautifully themed PDFs with syntax-highlighted code blocks.",
    add_completion=True,
    cls=ShortcutGroup,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)

config_app = typer.Typer(
    help="Manage codeDown configuration.",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
app.add_typer(config_app, name="config")


@app.callback()
def _global_options(
    version: bool = typer.Option(
        False,
        "-v",
        "--version",
        help="Show version and exit",
        callback=_version_callback,
        is_eager=True,
    ),
):
    return


@contextmanager
def _friendly_errors():
    try:
        yield
    except (ImportError, OSError, UnicodeError, ValueError, RuntimeError) as error:
        message = str(error)
        if isinstance(error, ImportError):
            message += ". Install code-down and its rendering dependencies."
        elif isinstance(error, UnicodeError):
            message = "Input Markdown must use UTF-8 encoding."
        typer.echo(f"Error: {message}", err=True)
        raise typer.Exit(code=1) from error


def _resolve_input_file(input_file: Path) -> Path:
    """Prefer an explicit existing path; otherwise resolve a Markdown stem."""
    if not input_file.exists() and not input_file.suffix:
        candidate = input_file.with_suffix(".md")
        if candidate.is_file():
            input_file = candidate
    if not input_file.exists():
        raise typer.BadParameter(f"Input file '{input_file}' does not exist")
    if not input_file.is_file():
        raise typer.BadParameter(f"Input path '{input_file}' is not a file")
    if input_file.suffix and input_file.suffix.lower() not in {".md", ".markdown"}:
        raise typer.BadParameter("Input must be a Markdown file (.md or .markdown)")
    return input_file


def _resolve_output_file(
    input_file: Path,
    output_arg: Optional[Path],
    output_opt: Optional[Path],
) -> Path:
    if output_arg is not None and output_opt is not None:
        typer.echo(
            "Error: provide output either as 2nd argument or via -o/--output", err=True
        )
        raise typer.Exit(code=2)

    output_raw = output_opt or output_arg
    if output_raw is None:
        return input_file.with_suffix(".pdf")

    # Treat as directory if it is a dir, or has no suffix (e.g. `temp`).
    if output_raw.exists() and output_raw.is_dir():
        output_dir = output_raw
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{input_file.stem}.pdf"

    if output_raw.suffix == "":
        output_dir = output_raw
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{input_file.stem}.pdf"

    if output_raw.suffix.lower() != ".pdf":
        output_raw = output_raw.with_suffix(".pdf")

    output_raw.parent.mkdir(parents=True, exist_ok=True)
    return output_raw


def _theme_choice_values(current: str) -> list[str]:
    from codedown.themes import get_all_themes

    names = sorted({t.name for t in get_all_themes()}, key=str.lower)
    if current in names:
        names.remove(current)
        return [current, *names]
    return names


@app.command("convert")
def convert_command(
    input_file: Path = typer.Argument(..., help="Input Markdown file to convert", autocompletion=complete_markdown),
    output_location: Optional[Path] = typer.Argument(None, help="Output directory or PDF path", autocompletion=complete_paths),
    output: Optional[Path] = typer.Option(None, "-o", "--output", autocompletion=complete_paths),
    style: Optional[str] = typer.Option(None, "-s", "--style", autocompletion=complete_themes),
    watch: bool = typer.Option(False, "-w", "--watch", help="Rebuild on changes"),
    preview: bool = typer.Option(False, "--preview", help="Open the live browser workspace instead of creating a PDF"),
    page_size: Optional[str] = typer.Option(None, help="A4, A5, Letter, or Legal", autocompletion=complete_page_sizes),
    margin: Optional[str] = typer.Option(None, help="Page margin, e.g. 20mm"),
    font: Optional[str] = typer.Option(None, help="Document font family"),
    code_font: Optional[str] = typer.Option(None, help="Code font family"),
    wrap_code: Optional[bool] = typer.Option(None, "--wrap-code/--no-wrap-code"),
    page_numbers: Optional[bool] = typer.Option(None, "--page-numbers/--no-page-numbers"),
    header: Optional[str] = typer.Option(None, help="Page header text"),
    footer: Optional[str] = typer.Option(None, help="Page footer text"),
    toc: Optional[bool] = typer.Option(None, "--toc/--no-toc", help="Include a table of contents"),
    title: Optional[str] = typer.Option(None, help="PDF title; defaults to input filename"),
    author: Optional[str] = typer.Option(None, help="PDF author metadata"),
    overwrite: Optional[bool] = typer.Option(None, "--overwrite/--no-overwrite", help="Replace an existing PDF (default: overwrite)"),
):
    """Convert a Markdown file into a themed PDF."""
    from codedown.config import load_config
    from codedown.themes import get_theme_by_name

    explicit = dict(page_size=page_size, margin=margin, font=font, code_font=code_font,
                    wrap_code=wrap_code, page_numbers=page_numbers, header=header,
                    footer=footer, toc=toc, title=title, author=author)
    with _friendly_errors():
        input_file = _resolve_input_file(input_file)
        config = load_config(input_file.parent)
        settings = {field.name: config[field.name] for field in fields(RenderOptions) if field.name in config}
        settings.update({key: value for key, value in explicit.items() if value is not None})
        options = RenderOptions(**settings)
        theme_name = style if style is not None else config.get("default_theme", "dark")
        get_theme_by_name(theme_name)
        if preview:
            if watch or output_location is not None or output is not None:
                raise ValueError("--preview cannot be combined with --watch or PDF output paths")
            from codedown.preview import run_preview
            run_preview(input_file, theme_name, options)
            return
        output_file = _resolve_output_file(input_file, output_location, output)
        if output_file.resolve() == input_file.resolve():
            raise ValueError("Output must be different from the input file")
        allow_overwrite = overwrite if overwrite is not None else config.get("overwrite", True)
        if output_file.exists() and not allow_overwrite:
            raise ValueError(f"Output '{output_file}' exists; use --overwrite to replace it")
        if watch:
            _do_watch(input_file, None, output_file, theme_name, options)
        else:
            _do_convert(input_file, None, output_file, theme_name, options)


def _do_convert(
    input_file: Path,
    output_location: Optional[Path] = None,
    output_opt: Optional[Path] = None,
    style: Optional[str] = None,
    render_options: Optional[RenderOptions] = None,
):
    """Core conversion logic shared by convert and watch."""
    from codedown.config import load_config
    from codedown.converter import ConverterEngine

    input_file = _resolve_input_file(input_file)

    output_file = _resolve_output_file(input_file, output_location, output_opt)
    theme_name = style if style is not None else load_config(input_file.parent).get("default_theme", "dark")

    markdown_text = input_file.read_text(encoding="utf-8")
    converter = ConverterEngine(markdown_text, input_file, render_options)
    converter.convert_to_pdf(str(output_file), style=theme_name)

    typer.echo(f"PDF successfully created: {output_file}")


def _do_watch(
    input_file: Path,
    output_location: Optional[Path] = None,
    output_opt: Optional[Path] = None,
    style: Optional[str] = None,
    render_options: Optional[RenderOptions] = None,
):
    """Watch the input file and rebuild PDF on changes."""
    from codedown.config import load_config
    from codedown.watcher import watch_and_convert

    input_file = _resolve_input_file(input_file)

    output_file = _resolve_output_file(input_file, output_location, output_opt)
    theme_name = style if style is not None else load_config(input_file.parent).get("default_theme", "dark")

    watch_and_convert(input_file, output_file, theme_name, render_options)


@app.command("preview")
def preview_command(
    input_file: Path = typer.Argument(..., help="Markdown file to preview", autocompletion=complete_markdown),
    style: Optional[str] = typer.Option(None, "-s", "--style", autocompletion=complete_themes),
    port: int = typer.Option(0, min=0, max=65535, help="Local port; 0 chooses an available port"),
    open_browser: bool = typer.Option(True, "--open/--no-open", help="Open the preview in your browser"),
):
    """Live preview with code copying and adjustable editor/preview splits."""
    from codedown.config import load_config
    from codedown.preview import run_preview
    with _friendly_errors():
        input_file = _resolve_input_file(input_file)
        config = load_config(input_file.parent)
        settings = {field.name: config[field.name] for field in fields(RenderOptions) if field.name in config}
        run_preview(input_file, style or config.get("default_theme", "dark"),
                    RenderOptions(**settings), port, open_browser)


# --- config subcommands ---


@config_app.command("show")
def config_show():
    """Show current configuration."""
    from codedown.config import CONFIG_FILE, find_project_config, load_config

    with _friendly_errors():
        config = load_config(Path.cwd())
        if not config:
            typer.echo("No configuration set. Using defaults.")
            typer.echo(f"  Config file: {CONFIG_FILE}")
            typer.echo(f"  default_theme = dark")
            return

        typer.echo(f"User config: {CONFIG_FILE}")
        project_file = find_project_config(Path.cwd())
        if project_file:
            typer.echo(f"Project config: {project_file}")
        for key, value in config.items():
            typer.echo(f"  {key} = {value}")


@config_app.command("set-theme")
def config_set_theme(
    theme_name: Optional[str] = typer.Argument(
        None, help="Theme name to set as default", autocompletion=complete_themes
    ),
):
    """Set the default theme. Run without arguments for interactive picker."""
    from codedown.config import set_default_theme
    from codedown.themes import get_theme_by_name

    with _friendly_errors():
        if theme_name is None:
            _pick_and_set_theme()
            return

        # Validate the theme exists
        get_theme_by_name(theme_name)
        set_default_theme(theme_name)
        typer.echo(f"Default theme set to '{theme_name}'")


def _pick_and_set_theme():
    """Interactive theme picker using InquirerPy."""
    from InquirerPy import inquirer

    from codedown.config import get_default_theme, set_default_theme

    current = get_default_theme()
    theme_names = _theme_choice_values(current)

    choices = [{"name": name, "value": name} for name in theme_names]

    selected = inquirer.select(
        message="Select default theme:",
        choices=choices,
        default=current,
    ).execute()

    if selected is None:
        typer.echo("Cancelled.")
        raise typer.Exit(0)

    set_default_theme(selected)
    typer.echo(f"Default theme set to '{selected}'")


# --- themes command ---


@app.command("themes")
def themes_command():
    """Browse and select a theme interactively."""
    from InquirerPy import inquirer

    from codedown.config import get_default_theme, set_default_theme

    with _friendly_errors():
        current = get_default_theme()
        theme_names = _theme_choice_values(current)

        choices = [{"name": name, "value": name} for name in theme_names]

        selected = inquirer.select(
            message="Pick a theme:",
            choices=choices,
            default=current,
        ).execute()

        if selected is None:
            raise typer.Exit(0)

        set_default_theme(selected)
        typer.echo(f"Default theme set to '{selected}'")


# --- update command ---


@app.command("update")
def update_command():
    """Update codeDown to the latest version."""
    from codedown.updater import run_update

    with _friendly_errors():
        run_update()


@config_app.command("set")
def config_set(key: str = typer.Argument(..., help="Configuration key", autocompletion=complete_config_keys),
               value: str = typer.Argument(..., help="String value or true/false for booleans", autocompletion=complete_config_values)):
    """Set a validated user default; project config may override it."""
    from codedown.config import load_config, save_config
    with _friendly_errors():
        config = load_config()
        bool_keys = {"overwrite", "wrap_code", "page_numbers", "toc"}
        if key in bool_keys:
            if value not in {"true", "false"}:
                raise ValueError(f"{key} must be true or false")
            config[key] = value == "true"
        else:
            config[key] = value
        save_config(config)
        typer.echo(f"Saved {key} = {config[key]}")
