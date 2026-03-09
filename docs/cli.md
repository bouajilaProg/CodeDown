# CLI

## Convert

```bash
code-down input.md
code-down input.md out.pdf
code-down input.md out/          # outputs out/input.pdf
code-down input.md -s light
code-down -w input.md            # watch mode (note: -w comes before the file)
```

Options:

- `-o, --output`: output path (alternative to the 2nd argument)
- `-s, --style`: theme name
- `-w, --watch`: watch and rebuild on changes

## Themes

```bash
code-down themes
```

Picks a theme interactively and stores it as the default theme.

## Config

```bash
code-down config show
code-down config set-theme
code-down config set-theme dark
```

Config file:

- `~/.config/codedown/config.toml`

## Update

```bash
code-down update
```

## Version

```bash
code-down -v
code-down --version
```
