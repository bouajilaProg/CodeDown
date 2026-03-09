set dotenv-load := true

default:
  @just --list

install:
  python -m pip install -U pip
  python -m pip install -e '.[dev]'

test:
  pytest

build:
  python -m build

uv-build:
  uv build

publish:
  uv publish --token "$PYPI_API_TOKEN"

release TAG:
  gh release create {{TAG}} --title "{{TAG}}" --generate-notes

clean:
  rm -rf build/ dist/ .pytest_cache/ htmlcov/ *.egg-info/
