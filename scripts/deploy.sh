#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST=yongle-nanjing
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REMOTE=/var/www/gooddesign.qiuyiwu.com
python3 "$ROOT/scripts/build_original.py"
python3 "$ROOT/scripts/check_design.py"
test -s "$ROOT/original-app/public/index.html"
test -s "$ROOT/original-app/server.js"
COPYFILE_DISABLE=1 tar --no-xattrs -C "$ROOT/original-app" -czf /tmp/gooddesign-original.tgz .
scp -q /tmp/gooddesign-original.tgz "$HOST:/tmp/gooddesign-original-$STAMP.tgz"
scp -q "$ROOT/deploy/nginx-gooddesign.qiuyiwu.com.conf" "$HOST:/tmp/gooddesign-nginx.conf"
scp -q "$ROOT/deploy/gooddesign.service" "$HOST:/tmp/gooddesign.service"
ssh "$HOST" bash -s -- "$STAMP" <<'REMOTE'
set -euo pipefail
STAMP="$1"
BASE=/var/www/gooddesign.qiuyiwu.com
sudo mkdir -p "$BASE/releases/$STAMP" "$BASE/backups" /var/lib/gooddesign
sudo chown www-data:www-data /var/lib/gooddesign
sudo chmod 700 /var/lib/gooddesign
readlink "$BASE/current" | sudo tee "$BASE/backups/$STAMP.previous" >/dev/null
sudo cp /etc/nginx/sites-available/gooddesign.qiuyiwu.com "$BASE/backups/$STAMP.nginx"
rollback() {
 sudo ln -s "$(cat "$BASE/backups/$STAMP.previous")" "$BASE/rollback.next"
 sudo mv -Tf "$BASE/rollback.next" "$BASE/current"
 sudo cp "$BASE/backups/$STAMP.nginx" /etc/nginx/sites-available/gooddesign.qiuyiwu.com
 sudo systemctl restart gooddesign || true
 sudo nginx -t && sudo systemctl reload nginx
}
trap rollback ERR
sudo tar -xzf "/tmp/gooddesign-original-$STAMP.tgz" -C "$BASE/releases/$STAMP"
sudo chmod -R a+rX "$BASE/releases/$STAMP"
test -s "$BASE/releases/$STAMP/public/index.html"
sudo install -m 644 /tmp/gooddesign.service /etc/systemd/system/gooddesign.service
sudo ln -s "$BASE/releases/$STAMP" "$BASE/current.next"
sudo mv -Tf "$BASE/current.next" "$BASE/current"
sudo systemctl daemon-reload
sudo systemctl enable --now gooddesign
sudo systemctl restart gooddesign
sleep 2
curl -fsS http://127.0.0.1:3187/api/health >/dev/null
sudo cp /tmp/gooddesign-nginx.conf /etc/nginx/sites-available/gooddesign.qiuyiwu.com
sudo nginx -t >/tmp/gooddesign-nginx-test.log 2>&1
sudo systemctl reload nginx
curl -fsS --retry 3 --retry-all-errors --retry-delay 1 --resolve gooddesign.qiuyiwu.com:443:127.0.0.1 https://gooddesign.qiuyiwu.com/api/health >/dev/null
REMOTE
printf '%s\n' "$STAMP" > "$ROOT/deploy/LAST_RELEASE"
echo "Original release: $STAMP"
