#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST=yongle-nanjing
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE=/var/www/gooddesign.qiuyiwu.com
python3 "$ROOT/scripts/build_site.py"
python3 "$ROOT/scripts/check_site.py" > "$ROOT/00-项目管理/发布检查输出.txt"
test -s "$ROOT/site/index.html"
test -s "$ROOT/site/awards.json"
# Each deploy is an immutable release. Retain the previous target for rollback.
ssh -o BatchMode=yes "$HOST" "sudo mkdir -p '$REMOTE/releases/$STAMP' '$REMOTE/backups'; sudo chown ubuntu:ubuntu '$REMOTE/releases/$STAMP'; if test -L '$REMOTE/current'; then readlink '$REMOTE/current' | sudo tee '$REMOTE/backups/$STAMP.previous' >/dev/null; fi"
COPYFILE_DISABLE=1 tar --no-xattrs -C "$ROOT/site" -czf /tmp/gooddesign-release.tgz .
scp -q /tmp/gooddesign-release.tgz "$HOST:/tmp/gooddesign-release-$STAMP.tgz"
ssh -o BatchMode=yes "$HOST" "tar -xzf '/tmp/gooddesign-release-$STAMP.tgz' -C '$REMOTE/releases/$STAMP'; test -s '$REMOTE/releases/$STAMP/index.html'; sudo ln -s '$REMOTE/releases/$STAMP' '$REMOTE/current.next'; sudo mv -Tf '$REMOTE/current.next' '$REMOTE/current'"
printf '%s\n' "$STAMP" > "$ROOT/deploy/LAST_RELEASE"
if curl -fsS --max-time 20 https://gooddesign.qiuyiwu.com/ | grep -q '创新设计知识平台'; then
  echo "Healthy release: $STAMP"
else
  echo 'Health check failed; restoring previous release if present.'
  ssh -o BatchMode=yes "$HOST" "if test -s '$REMOTE/backups/$STAMP.previous'; then sudo ln -s \"\$(cat '$REMOTE/backups/$STAMP.previous')\" '$REMOTE/rollback.next'; sudo mv -Tf '$REMOTE/rollback.next' '$REMOTE/current'; fi"
  exit 1
fi
