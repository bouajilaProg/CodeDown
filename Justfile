set dotenv-load := true

default:
  @just --list

install:
  python -m pip install -U pip
  python -m pip install -r requirements.txt
  python -m pip install -e '.[dev]'

test:
  pytest

build: test
  python -m pip install -U build
  python -m build

uv-build:
  uv build

release TAG:
  gh release create {{TAG}} --title "{{TAG}}" --generate-notes

clean:
  rm -rf build/ dist/ .pytest_cache/ htmlcov/ *.egg-info/
