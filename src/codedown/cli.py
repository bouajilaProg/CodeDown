from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="code-down",
    help="Convert Markdown files into beautifully themed PDFs with syntax-highlighted code blocks.",
    add_completion=False,
    no_args_is_help=True,
)

config_app = typer.Typer(help="Manage codeDown configuration.", no_args_is_help=True)
app.add_typer(config_app, name="config")


@app.command("convert")
def convert_command(
    input_file: Path = typer.Argument(..., help="Input Markdown file to convert"),
    output: Optional[Path] = typer.Option(
        None, "-o", "--output", help="Output PDF file path"
    ),
    style: Optional[str] = typer.Option(
        None, "-s", "--style", help="Theme style (e.g. light, dark)"
    ),
    watch: bool = typer.Option(
        False, "-w", "--watch", help="Watch the file and rebuild PDF on changes"
    ),
):
    """Convert a Markdown file into a themed PDF."""
    if watch:
        _do_watch(input_file, output, style)
    else:
        _do_convert(input_file, output, style)


def _do_convert(
    input_file: Path,
    output: Optional[Path] = None,
    style: Optional[str] = None,
):
    """Core conversion logic shared by convert and watch."""
    from codedown.config import load_config
    from codedown.converter import ConverterEngine

    if not input_file.exists():
        typer.echo(f"Error: Input file '{input_file}' does not exist", err=True)
        raise typer.Exit(code=1)

    output_file = output or input_file.with_suffix(".pdf")
    config = load_config()
    theme_name = style or config.get("default_theme", "dark")

    markdown_text = input_file.read_text(encoding="utf-8")
    converter = ConverterEngine(markdown_text)
    converter.convert_to_pdf(str(output_file), style=theme_name)

    typer.echo(f"PDF successfully created: {output_file}")


def _do_watch(
    input_file: Path,
    output: Optional[Path] = None,
    style: Optional[str] = None,
):
    """Watch the input file and rebuild PDF on changes."""
    from codedown.config import load_config
    from codedown.watcher import watch_and_convert

    if not input_file.exists():
        typer.echo(f"Error: Input file '{input_file}' does not exist", err=True)
        raise typer.Exit(code=1)

    output_file = output or input_file.with_suffix(".pdf")
    config = load_config()
    theme_name = style or config.get("default_theme", "dark")

    watch_and_convert(input_file, output_file, theme_name)


# --- config subcommands ---


@config_app.command("show")
def config_show():
    """Show current configuration."""
    from codedown.config import CONFIG_FILE, load_config

    config = load_config()
    if not config:
        typer.echo("No configuration set. Using defaults.")
        typer.echo(f"  Config file: {CONFIG_FILE}")
        typer.echo(f"  default_theme = dark")
        return

    typer.echo(f"Config file: {CONFIG_FILE}")
    for key, value in config.items():
        typer.echo(f"  {key} = {value}")


@config_app.command("set-theme")
def config_set_theme(
    theme_name: Optional[str] = typer.Argument(
        None, help="Theme name to set as default"
    ),
):
    """Set the default theme. Run without arguments for interactive picker."""
    from codedown.config import set_default_theme
    from codedown.themes import get_all_themes, get_theme_by_name

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
    from codedown.themes import get_all_themes

    themes = get_all_themes()
    current = get_default_theme()

    choices = []
    for theme in themes:
        label = f"{theme.name} (syntax: {theme.code_theme})"
        if theme.name == current:
            label += "  ← current"
        choices.append({"name": label, "value": theme.name})

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
    from codedown.themes import get_all_themes

    themes = get_all_themes()
    current = get_default_theme()

    choices = []
    for theme in themes:
        label = f"{theme.name} (syntax: {theme.code_theme}, v{theme.version})"
        if theme.name == current:
            label += "  ← current"
        choices.append({"name": label, "value": theme.name})

    selected = inquirer.select(
        message="Pick a theme:",
        choices=choices,
        default=current,
    ).execute()

    if selected is None:
        raise typer.Exit(0)

    action = inquirer.select(
        message=f"What to do with '{selected}'?",
        choices=[
            {"name": "Set as default theme", "value": "set_default"},
            {"name": "Cancel", "value": "cancel"},
        ],
    ).execute()

    if action == "set_default":
        set_default_theme(selected)
        typer.echo(f"Default theme set to '{selected}'")
    else:
        typer.echo("Cancelled.")


# --- update command ---


@app.command("update")
def update_command():
    """Update codeDown to the latest version."""
    from codedown.updater import run_update

    run_update()
