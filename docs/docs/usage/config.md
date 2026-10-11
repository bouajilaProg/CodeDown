---
title: "Configuration"
---

Show current configuration:

```bash
code-down config show
```

Set the default theme:

```bash
code-down config set-theme
code-down config set-theme dark
```

Config file location:

- `~/.config/codedown/config.toml`

Set validated user defaults:

```bash
code-down config set page_size Letter
code-down config set margin 15mm
code-down config set page_numbers true
code-down config set overwrite false
```

Available keys: `default_theme`, `page_size`, `margin`, `font`, `code_font`,
`wrap_code`, `page_numbers`, `header`, `footer`, `toc`, `title`, `author`, and
`overwrite`. Boolean values use `true` or `false`.

Place a `codedown.toml` in your project directory:

```toml
default_theme = "print"
page_size = "A4"
margin = "20mm"
page_numbers = true
overwrite = false
```

Conversion finds the nearest project file by searching from the Markdown file's
parent directory upwards. Precedence: CLI options, project configuration, user
configuration, built-in defaults. `config show` displays the merged configuration
for the current directory and its configuration paths; setters write user defaults.
On Linux, `XDG_CONFIG_HOME` can override the `~/.config` configuration root.

Existing PDFs are replaced by default. `--no-overwrite` refuses an existing
output without prompting; `--overwrite` explicitly allows replacement. In watch
mode the policy is checked at startup, then each successful rebuild replaces
that session's output. Invalid settings fail with an error before rendering.
