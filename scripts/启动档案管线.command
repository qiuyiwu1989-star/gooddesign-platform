#!/bin/zsh
set -e
cd "$(dirname "$0")/.."
if [[ ! -x .runtime/pipeline/bin/python || ! -x .runtime/vision-ocr ]]; then
  print "请先双击 scripts/安装档案管线.command。"
  exit 1
fi
if curl -fsS --max-time 3 http://127.0.0.1:8776/ >/dev/null 2>&1; then
  open "http://127.0.0.1:8776/?project=2025-00"
  print "资料后台已运行；如需加载新代码，请在其终端按Ctrl-C后重新启动。"
  exit 0
fi
open "http://127.0.0.1:8776/?project=2025-00"
exec .runtime/pipeline/bin/python scripts/file_admin.py --port 8776
