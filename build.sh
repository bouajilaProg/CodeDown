#!/bin/bash
set -e # stop on error

# If conda is available, initialize it (matches local alias `conda-init`).
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
  # shellcheck disable=SC1091
  source "$HOME/miniconda3/etc/profile.d/conda.sh"
fi

echo "=== Running Python Build ==="
./utils/python-build.sh

echo "=== Running Linux Build ==="
./utils/linux-build.sh

echo "=== All Builds Finished ==="
