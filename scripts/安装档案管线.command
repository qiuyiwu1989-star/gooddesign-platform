#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
if [[ ! -d /Volumes/邱懿武 ]]; then
  print "项目移动硬盘未挂载，停止安装。"
  exit 1
fi
if [[ ! -x .runtime/pipeline/bin/python ]]; then
  pipeline_python="$(command -v python3.12 || command -v python3.11 || command -v python3.10 || true)"
  if [[ -z "$pipeline_python" && -x /Users/qiuyiwu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 ]]; then
    pipeline_python=/Users/qiuyiwu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
  fi
  if [[ -z "$pipeline_python" ]]; then print "需要 Python 3.10 或更高版本。"; exit 1; fi
  "$pipeline_python" -m venv .runtime/pipeline
fi
.runtime/pipeline/bin/python -m pip install --cache-dir .runtime/pip-cache -r requirements-research-pipeline.txt
mkdir -p .runtime/swift-cache
CLANG_MODULE_CACHE_PATH="$PWD/.runtime/swift-cache" swiftc -module-cache-path "$PWD/.runtime/swift-cache" scripts/vision_ocr.swift -o .runtime/vision-ocr
print "安装完成。双击 scripts/启动档案管线.command。"
