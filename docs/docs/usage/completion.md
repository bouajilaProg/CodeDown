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
```

Completion only reads filenames and the theme registry; it does not render PDFs
or save configuration. Quote paths containing spaces when entering them manually.
