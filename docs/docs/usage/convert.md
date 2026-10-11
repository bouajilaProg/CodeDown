---
title: "Convert"
---

Convert a Markdown file to PDF:

```bash
code-down input.md
```

Write to a specific output file:

```bash
code-down input.md out.pdf
# or
code-down input.md -o out.pdf
```

Write into a directory (it will create `out/input.pdf`):

```bash
code-down input.md out/
```

Pick a theme for this run:

```bash
code-down input.md -s light
```

You can also supply a filename without its extension: `code-down input` resolves
`input.md`. An existing file named `input` takes precedence. Supported extensions
are `.md` and `.markdown`; extensionless files are accepted when they exist.
Quote paths containing spaces: `code-down "my notes.md"`.

The explicit form, `code-down convert input.md`, supports the same options.
