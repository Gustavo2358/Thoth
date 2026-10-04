#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname -- "${BASH_SOURCE[0]}")/.."
python3 -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"'
thoth_setup_venv="${THOTH_SETUP_VENV:-.venv}"
python3 -m venv "$thoth_setup_venv"
"$thoth_setup_venv/bin/python" -m pip install --disable-pip-version-check --no-cache-dir -r requirements.lock
"$thoth_setup_venv/bin/python" -m pip install --disable-pip-version-check --no-cache-dir --no-build-isolation --no-deps -e .
"$thoth_setup_venv/bin/python" -m pytest -q
