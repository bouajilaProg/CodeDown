import sys
from pathlib import Path


class CliParser:
    def __init__(self, args):
        self.args = args[1:]
        self.input_file = None
        self.output_file = None
        self.style = None

    def parse(self):
        if not self.args:
            self._print_usage()
            sys.exit(1)

        # help flag
        if "-h" in self.args or "--help" in self.args:
            self._print_usage()
            sys.exit(0)

        self.input_file = Path(self.args[0])

        # Parse optional arguments
        for i in range(1, len(self.args)):
            if self.args[i] in ("-o", "--output") and i + 1 < len(self.args):
                self.output_file = Path(self.args[i + 1])
            elif self.args[i] in ("-s", "--style") and i + 1 < len(self.args):
                self.style = self.args[i + 1]

        # Set defaults and validate
        if not self.input_file.exists():
            print(f"Error: Input file '{self.input_file}' does not exist")
            sys.exit(1)

        if self.output_file is None:
            self.output_file = self.input_file.with_suffix(".pdf")

        return self

    def _print_usage(self):
        print("Usage: codedown <input.md> [-o output.pdf] [-s style]")
