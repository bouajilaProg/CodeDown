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
