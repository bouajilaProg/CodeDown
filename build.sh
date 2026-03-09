#!/bin/bash
set -e # stop on error

conda-init || true
conda activate codeDown || true

echo "=== Running Python Build ==="
./utils/python-build.sh

echo "=== Running Linux Build ==="
./utils/linux-build.sh

echo "=== All Builds Finished ==="
