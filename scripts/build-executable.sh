#!/usr/bin/env bash
# Build the self-contained tagalog-g2p executable into dist/tagalog-g2p.
#
# Must run inside the project container: it uses the container's Python 3.10,
# where the Phonetisaurus binding and OpenFst libraries are installed.
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON=/usr/local/bin/python3

if ! "$PYTHON" -c 'import Phonetisaurus' 2>/dev/null; then
    echo "error: Phonetisaurus binding not importable by $PYTHON (run inside the project container)" >&2
    exit 1
fi

"$PYTHON" -m PyInstaller --version >/dev/null 2>&1 || "$PYTHON" -m pip install pyinstaller
exec "$PYTHON" -m PyInstaller --clean --noconfirm tagalog-g2p.spec
