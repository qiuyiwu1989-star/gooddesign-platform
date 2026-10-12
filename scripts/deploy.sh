#!/usr/bin/env bash
# Publish committed, pushed code only; runtime secrets/data stay on the server.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
HOST=yongle-nanjing
BASE=/var/www/gooddesign.qiuyiwu.com
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo 'Commit tracked changes before deploying.' >&2; exit 1
fi
git fetch origin main
SHA=$(git rev-parse HEAD)
git merge-base --is-ancestor "$SHA" origin/main || { echo 'Push this commit to main first.' >&2; exit 1; }
STAMP="$(date -u +%Y%m%dT%H%M%SZ)-${SHA:0:12}"
WORK=$(mktemp -d "$ROOT/.deploy-work.XXXXXX")
trap 'rm -rf "$WORK"' EXIT
git archive "$SHA" original-app | tar -xf - -C "$WORK"
printf '%s\n' "$SHA" > "$WORK/original-app/REVISION"
test -s "$WORK/original-app/server.js"
test -s "$WORK/original-app/public/index.html"
COPYFILE_DISABLE=1 tar -czf "$WORK/release.tgz" -C "$WORK/original-app" .
scp -q "$WORK/release.tgz" "$HOST:/tmp/gooddesign-$STAMP.tgz"
ssh "$HOST" sudo bash -s -- "$STAMP" "$SHA" <<'REMOTE'
set -euo pipefail
STAMP=$1
SHA=$2
BASE=/var/www/gooddesign.qiuyiwu.com
exec 9>"$BASE/.deploy.lock"
flock -n 9 || { echo 'Another deployment is running'; exit 1; }
PREVIOUS=$(readlink -f "$BASE/current")
RELEASE="$BASE/releases/$STAMP"
mkdir -p "$RELEASE" "$BASE/backups"
printf '%s\n' "$PREVIOUS" > "$BASE/backups/$STAMP.previous"
tar -xzf "/tmp/gooddesign-$STAMP.tgz" -C "$RELEASE"
chmod -R a+rX "$RELEASE"
test "$(cat "$RELEASE/REVISION")" = "$SHA"
test -s "$RELEASE/public/index.html"
test -s "$RELEASE/server.js"
[ "$(readlink -f "$BASE/current")" = "$PREVIOUS" ]
rollback() {
  ln -s "$PREVIOUS" "$BASE/rollback.$STAMP"
  mv -Tf "$BASE/rollback.$STAMP" "$BASE/current"
  systemctl restart gooddesign || true
}
trap rollback ERR
ln -s "$RELEASE" "$BASE/current.$STAMP"
mv -Tf "$BASE/current.$STAMP" "$BASE/current"
systemctl restart gooddesign
curl -fsS --retry 5 --retry-connrefused --retry-delay 1 --max-time 15 http://127.0.0.1:3187/api/health >/dev/null
curl -fsS --max-time 15 --resolve gooddesign.qiuyiwu.com:443:127.0.0.1 https://gooddesign.qiuyiwu.com/ -o "/tmp/gooddesign-$STAMP-index.html"
cmp "/tmp/gooddesign-$STAMP-index.html" "$RELEASE/public/index.html"
trap - ERR
rm -f "/tmp/gooddesign-$STAMP.tgz" "/tmp/gooddesign-$STAMP-index.html"
printf 'Published %s (%s)\n' "$STAMP" "$SHA"
REMOTE
printf '%s\n' "$STAMP" > "$ROOT/deploy/LAST_RELEASE"
