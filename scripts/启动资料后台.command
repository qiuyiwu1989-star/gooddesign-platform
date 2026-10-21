#!/bin/zsh
cd "$(dirname "$0")/.." || exit 1
python3 scripts/file_admin.py --port 8776
