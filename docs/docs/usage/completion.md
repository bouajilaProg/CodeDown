---
title: "Autocomplete"
---

From your Bash, Zsh, or Fish shell, install completion once:

```bash
code-down --install-completion
```

Restart that shell to load its completion configuration. Run
`code-down --show-completion` to inspect the script instead of installing it.
Shell detection uses the shell running the command; run installation directly
from the shell you intend to configure.

Press Tab to complete commands, Markdown filenames, directories, options, and
available theme names. Both command forms work:

```text
code-down no<Tab>
code-down notes.md --style <Tab>
code-down convert notes.md --output <Tab>
code-down config set-theme <Tab>
code-down preview no<Tab>
code-down preview notes.md --style <Tab>
code-down notes.md --page-size <Tab>
code-down config set <Tab>
code-down config set default_theme <Tab>
code-down config set wrap_code <Tab>
```

Completion only reads filenames and the theme registry; it does not render PDFs
or save configuration. Quote paths containing spaces when entering them manually.

Preview completion includes Markdown files, all eight themes, and options such
as `--no-open` and `--port`. Configuration completion suggests validated keys,
theme names, page sizes, boolean values, and standard font families.

To choose a shell explicitly:

```bash
code-down --install-completion bash
code-down --install-completion zsh
code-down --install-completion fish
```

After upgrading, reinstall completion and restart your shell to refresh its
script. Completion is available in both the pip package and standalone binary.
