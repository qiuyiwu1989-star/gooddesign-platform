#!/bin/zsh
set -eu
project_pipeline_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$project_pipeline_root"
exec python3 -u scripts/project_pipeline.py watch
