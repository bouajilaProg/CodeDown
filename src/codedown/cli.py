import sys
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(
    name="code-down",
    help="Convert Markdown files into beautifully themed PDFs with syntax-highlighted code blocks.",
    add_completion=False,
)


@app.command()
def convert(
    input_file: Path = typer.Argument(..., help="Input Markdown file to convert"),
    output: Optional[Path] = typer.Option(
        None, "-o", "--output", help="Output PDF file path"
    ),
    style: Optional[str] = typer.Option(
        None, "-s", "--style", help="Theme style (e.g. light, dark)"
    ),
):
    """Convert a Markdown file into a themed PDF."""
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
