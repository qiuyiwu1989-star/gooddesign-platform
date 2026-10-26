#!/bin/zsh
cd "$(dirname "$0")/.." || exit 1
printf '启动后请打开 http://127.0.0.1:8786/\n需求保存在当前项目 output/method-workbench-private/\n'
exec python3 scripts/method_workbench_server.py
