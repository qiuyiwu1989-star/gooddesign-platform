#!/usr/bin/env python3
"""激活推理画布 20261112-115 受保护试点。部署阶段在服务器上运行。"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

RELEASE = "20261112-115"
PORT = 18791
BASE = Path("/var/www/innovation-design")
CURRENT = BASE / "current"
TARGET = BASE / "releases" / RELEASE
DATA = Path("/var/lib/innovation-canvas")
BACKUP = Path("/var/lib/innovation-design/release-backups") / RELEASE
NGINX_SNIPPET = Path("/etc/nginx/snippets/inno-readonly.conf")
SERVICE = Path("/etc/systemd/system/innovation-canvas.service")

NGINX_BLOCK = r'''
# 115 reasoning canvas begin
location ^~ /inno/canvas/api/rc/ {
    auth_basic off;
    auth_request /inno/auth/check;
    error_page 401 = @inno_login;
    proxy_pass http://127.0.0.1:18791/api/rc/;
    proxy_set_header Host 127.0.0.1:18791;
    proxy_set_header Connection "";
    proxy_http_version 1.1;
    proxy_read_timeout 60s;
    add_header Cache-Control "private, no-store" always;
    add_header X-Content-Type-Options "nosniff" always;
}
location ^~ /inno/canvas/ {
    auth_basic off;
    auth_request /inno/auth/check;
    error_page 401 = @inno_login;
    proxy_pass http://127.0.0.1:18791/extensions/reasoning-canvas/;
    proxy_set_header Host 127.0.0.1:18791;
    proxy_set_header Connection "";
    proxy_http_version 1.1;
    proxy_read_timeout 60s;
    add_header Cache-Control "private, no-store" always;
    add_header X-Content-Type-Options "nosniff" always;
}
location ^~ /inno/method-workbench/vendor/ {
    auth_basic off;
    auth_request /inno/auth/check;
    error_page 401 = @inno_login;
    alias /var/www/innovation-design/current/extensions/method-workbench/vendor/;
    add_header Cache-Control "private, no-cache" always;
    add_header X-Content-Type-Options "nosniff" always;
}
location ^~ /inno/design-system/ {
    auth_basic off;
    auth_request /inno/auth/check;
    error_page 401 = @inno_login;
    alias /var/www/innovation-design/current/extensions/design-system/;
    add_header Cache-Control "private, no-cache" always;
    add_header X-Content-Type-Options "nosniff" always;
}
# 115 reasoning canvas end
'''

SERVICE_TEXT = f'''[Unit]
Description=GoodDesign reasoning canvas protected pilot
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory={TARGET}
ExecStart=/var/www/innovation-design/venv/bin/python scripts/reasoning_canvas_server.py --port {PORT} --state-db {DATA}/canvas-state.sqlite3
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={DATA}
UMask=0077

[Install]
WantedBy=multi-user.target
'''


def run(*args, check=True, **kwargs):
    return subprocess.run(args, check=check, **kwargs)


def sudo_write(path, content):
    run("sudo", "tee", str(path), input=content.encode(), stdout=subprocess.DEVNULL)


def remove_nginx_block(text):
    start = text.find("# 115 reasoning canvas begin")
    end = text.find("# 115 reasoning canvas end")
    if start < 0 or end < 0:
        return text
    return text[:start] + text[end + len("# 115 reasoning canvas end"):]


def configure_nginx():
    run("sudo", "install", "-d", "-o", "ubuntu", "-g", "ubuntu", str(BACKUP))
    BACKUP.mkdir(parents=True, exist_ok=True)
    original = NGINX_SNIPPET.read_text(encoding="utf-8")
    (BACKUP / "inno-readonly.conf.before").write_text(original, encoding="utf-8")
    cleaned = remove_nginx_block(original).rstrip() + "\n" + NGINX_BLOCK
    sudo_write(NGINX_SNIPPET, cleaned)


def rollback_nginx():
    backup = BACKUP / "inno-readonly.conf.before"
    if backup.exists():
        sudo_write(NGINX_SNIPPET, backup.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", required=True, type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.stage / "release-manifest.json").read_text())
    assert manifest["release"] == RELEASE
    package = args.stage / manifest["package"]["name"]
    assert package.stat().st_size == manifest["package"]["bytes"]
    assert hashlib.sha256(package.read_bytes()).hexdigest() == manifest["package"]["sha256"]
    assert CURRENT.resolve().is_dir()
    if TARGET.exists() or TARGET.is_symlink():
        shutil.rmtree(TARGET)

    try:
        TARGET.mkdir(parents=True)
        for name in ("scripts", "extensions", "04-知识库"):
            run("cp", "-a", str(CURRENT.resolve() / name), str(TARGET / name))
        with tarfile.open(package) as archive:
            members = archive.getmembers()
            for member in members:
                target = TARGET / member.name
                if target.exists() or target.is_symlink():
                    target.unlink()
            archive.extractall(TARGET, filter="data")
        run("sudo", "install", "-d", "-o", "ubuntu", "-g", "ubuntu", str(DATA))
        sudo_write(SERVICE, SERVICE_TEXT)
        configure_nginx()
        run("sudo", "systemctl", "daemon-reload")
        run("sudo", "systemctl", "enable", "--now", "innovation-canvas")
        run("sudo", "nginx", "-t")
        run("sudo", "systemctl", "reload", "nginx")
        request = urllib.request.Request(f"http://127.0.0.1:{PORT}/api/rc/engine_candidates", headers={"Host": f"127.0.0.1:{PORT}"})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200 and payload["ok"]
        anonymous = subprocess.run(
            ["curl", "-sk", "-o", "/dev/null", "-w", "%{http_code}", "https://127.0.0.1/inno/canvas/", "-H", "Host: opendesign.cc"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        assert anonymous == "302", anonymous
        result = {
            "release": RELEASE,
            "service": "innovation-canvas.service",
            "port": PORT,
            "route": "/inno/canvas/",
            "anonymous_status": anonymous,
            "backup": str(BACKUP),
            "data": str(DATA),
        }
        (args.stage / "activation-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except BaseException:
        run("sudo", "systemctl", "disable", "--now", "innovation-canvas", check=False)
        rollback_nginx()
        run("sudo", "nginx", "-t", check=False)
        run("sudo", "systemctl", "reload", "nginx", check=False)
        raise


if __name__ == "__main__":
    main()
