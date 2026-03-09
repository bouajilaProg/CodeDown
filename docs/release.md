# Release

## GitHub Release (CI)

This repo publishes to PyPI and attaches the Linux binary when a GitHub Release is published.

Required GitHub secret:

- `PYPI_API_TOKEN` (PyPI API token)

Create a release:

```bash
just release v2.0.0
```

## Local publish with uv

Create `.env` in the repo root:

```
PYPI_API_TOKEN=YOUR_TOKEN
```

Then run:

```bash
just publish
```
