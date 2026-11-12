#!/usr/bin/env python3
"""打包推理画布 20261112-115 受保护试点 release overlay。"""
import hashlib
import json
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "20261112-115"
OUT = ROOT / "output" / "deploy-115"
PACKAGE = OUT / "canvas-overlay.tar.gz"
FILES = [
    "scripts/reasoning_canvas_server.py",
    "scripts/canvas_gdrp_mapper.py",
    "scripts/build_gdrp_report.py",
    "scripts/activate_canvas_release_115.py",
    "extensions/reasoning-canvas/index.html",
    "extensions/reasoning-canvas/reasoning-canvas.css",
    "extensions/reasoning-canvas/reasoning-canvas.js",
    "extensions/reasoning-canvas/state.js",
    "extensions/reasoning-canvas/data.js",
    "extensions/reasoning-canvas/README.md",
    "04-知识库/项目档案标准-v1/创新研究输出物标准-v1/research-pack.schema.json",
    "output/engine-runs/RUBBER-20261026/run-20261105T140200Z/research-pack.json",
    "output/engine-runs/RUBBER-20261026/run-20261105T140200Z/manifest.json",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_member(item):
    if "__pycache__" in item.name or item.name.endswith(".pyc") or item.issym() or item.islnk():
        return None
    return item


def main():
    missing = [name for name in FILES if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("missing files: " + ", ".join(missing))
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    with tarfile.open(PACKAGE, "w:gz") as archive:
        for name in FILES:
            archive.add(ROOT / name, arcname=name, filter=safe_member)
    manifest = {
        "release": RELEASE,
        "package": {"name": PACKAGE.name, "bytes": PACKAGE.stat().st_size, "sha256": sha(PACKAGE)},
        "files": FILES,
        "port": 18791,
        "public": False,
        "route": "/inno/canvas/",
        "data_dir": "/var/lib/innovation-canvas",
    }
    (OUT / "release-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
