# Development

## Install (editable)

```bash
python -m pip install -U pip
python -m pip install -e '.[dev]'
```

## Just + uv (recommended)

```bash
just install
just test
```

## Run

```bash
code-down -h
code-down examples/example.md out/
```

## Tests

```bash
pytest
```

## Clean

```bash
rm -rf build/ dist/ .pytest_cache/ htmlcov/ *.egg-info/
```
