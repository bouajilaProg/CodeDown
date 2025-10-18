import sys
from pathlib import Path
from converter import ConverterEngine

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python converter.py <input_markdown.md> <output.pdf>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file '{input_file}' does not exist.")
        sys.exit(1)

    markdown_text = input_file.read_text(encoding="utf-8")

    converter = ConverterEngine(markdown_text)
    converter.convert_to_pdf(str(output_file))

    print(f"PDF successfully created: {output_file}")
