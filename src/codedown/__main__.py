# src/codedown/__main__.py
import sys

from codedown.cli import CliParser
from codedown.converter import ConverterEngine


def main():
    parser = CliParser(sys.argv).parse()

    if parser.input_file is None:
        print(f"Error: Input file '{parser.input_file}' does not exist")
        sys.exit(1)

    markdown_text = parser.input_file.read_text(encoding="utf-8")
    converter = ConverterEngine(markdown_text)

    if parser.style:
        converter.convert_to_pdf(str(parser.output_file), style=parser.style)
    else:
        converter.convert_to_pdf(str(parser.output_file))
    print(f"PDF successfully created: {parser.output_file}")


if __name__ == "__main__":
    main()
