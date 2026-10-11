---
title: "Watch mode"
---

Watch mode regenerates the PDF whenever the input file changes.

```bash
code-down -w input.md
```

Note: `-w` comes before the file.

You can still set theme/output:

```bash
code-down -w input.md -s light
code-down -w input.md -o out.pdf
```

Watch mode handles file modifications, creation, deletion, and replacement saves
used by editors. It waits until changes settle, then rebuilds once per burst.
Changes during a render trigger a subsequent render rather than overlapping it.
Referenced local images and HTML resource links are watched too, including
resources outside the Markdown directory. New references are discovered on save.

PDF output is replaced only after rendering succeeds. A failed rebuild keeps the
previous PDF and prints an error; watch mode continues until Ctrl+C.
