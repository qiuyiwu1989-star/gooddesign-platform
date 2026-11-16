# coding: utf-8
"""118 全站视觉与一致性审计：结构、口径、红线、链接、交互细节。

只读审计，不修改任何文件。输入为构建产物目录，输出 JSON 报告与控制台摘要。
违规分级：P0 错误信息或断链；P1 结构不一致（导航/底部/双 chrome）；P2 交互与可访问性；
P3 建议项。白名单显式登记，白名单外的差异全算违规。
"""
import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SCHEMA = "site-audit-118-1"

# 动态路由白名单：由运行时/鉴权服务提供，静态目录中不存在文件属正常
DYNAMIC_PREFIXES = (
    "/inno/dossier/", "/inno/login/", "/inno/logout/", "/inno/auth/", "/inno/api/",
    "/inno/loop/", "/inno/canvas/", "/inno/mcp/api", "/inno/admin/",
    "/dossier/", "/login/", "/logout/", "/auth/", "/api/", "/loop/", "/canvas/", "/innovation/", "/admin/", "/expo/",
)
# 120/122 根路径 → 构建产物路径（nginx 规则的同构映射，详见 specs/117/120/122）
ROUTE_MAP = (
    ("/projects/", "inno/index.html"),
    ("/museum/zones", "categories.html"),
    ("/museum/hall", "hall.html"),
    ("/museum/x-ray", "x-ray.html"),
    ("/museum/playground", "playground.html"),
    ("/museum/laureates", "laureates.html"),
    ("/museum/assistant", "assistant.html"),
    ("/museum/connect", "connect.html"),
    ("/museum/award", "award.html"),
    ("/museum/", "inno/museum/"),
    ("/apps/", "inno/apps/"),
    ("/needs/", "inno/needs-v2/"),
    ("/report/", "inno/report/"),
    ("/mcp/", "inno/mcp/"),
    ("/about/", "inno/about/"),
    ("/model/", "inno/model/"),
    ("/guide/", "inno/guide/"),
    ("/cases/", "inno/cases/"),
    ("/methods/", "inno/methods/"),
)
BANNED_HOSTS = ("opendesign.cc", "gooddesign.qiuyiwu.com")
ARROW_CHARS = "↗↘→←↔⇄↑↓"
# 无 chrome 的页面白名单（打印页、嵌入页等），逐页登记
CHROME_WHITELIST: set = set()
# href="#" 但由页面 JS 动态赋值的元素（id 登记）
JS_ASSIGNED_HREF = {"/connect.html": {"inqOkReport"}}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.base_href = ""
        self._rel = ""
        self.headers = []
        self.footers = []
        self.main_ids = []
        self.skip_links = 0
        self.h1 = 0
        self.imgs_no_alt = 0
        self.buttons_no_type = 0
        self.blank_no_rel = 0
        self.dead_hash = 0
        self.arrow_anchors = 0
        self.refs = []
        self.banned = []
        self.http_links = []
        self._stack = []
        self._capture = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._stack.append(tag)
        if tag == "title":
            self._in_title = True
        if tag == "header":
            self._capture = ("header", a.get("data-gd-chrome"), [])
        elif tag == "footer":
            self._capture = ("footer", a.get("data-gd-chrome"), [])
        elif self._capture:
            self._capture[2].append(tag)
        if tag == "main":
            self.main_ids.append(a.get("id", ""))
        if tag == "base" and a.get("href"):
            self.base_href = a["href"]
        if tag == "a":
            if "gd-skip" in a.get("class", ""):
                self.skip_links += 1
            href = a.get("href", "")
            if href == "#" and a.get("id", "") not in JS_ASSIGNED_HREF.get(self._rel, set()):
                self.dead_hash += 1
            if a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
                self.blank_no_rel += 1
        if tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1
        if tag == "button" and "type" not in a:
            self.buttons_no_type += 1
        if tag == "h1":
            self.h1 += 1
        for k in ("href", "src", "poster"):
            v = a.get(k)
            if v:
                self.refs.append(v)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if self._capture and tag == self._capture[0]:
            kind, chrome, children = self._capture
            sig = hashlib.sha256(" ".join(children).encode()).hexdigest()[:12]
            entry = {"chrome": chrome or "none", "sig": sig, "tags": len(children)}
            (self.headers if kind == "header" else self.footers).append(entry)
            self._capture = None
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()


def audit_page(path, root):
    text = path.read_text(encoding="utf-8", errors="replace")
    p = Page()
    p._rel = "/" + path.relative_to(root).as_posix()
    p.feed(text)
    p.feed("")
    issues = []
    rel = p._rel
    base = p.base_href if p.base_href.startswith("/") else ""

    if rel not in CHROME_WHITELIST:
        navs = [h for h in p.headers if h["chrome"] == "navigation"]
        fts = [f for f in p.footers if f["chrome"] == "footer"]
        if len(navs) != 1:
            issues.append(("P1", f"导航数量为 {len(navs)}（应为 1）"))
        if len(fts) != 1:
            issues.append(("P1", f"底部数量为 {len(fts)}（应为 1）"))
        if len(p.headers) > len(navs):
            issues.append(("P3", f"存在非 chrome 的 header 共 {len(p.headers)} 个"))
        if not p.skip_links:
            issues.append(("P2", "缺少跳转主要内容的 skip link"))
    if p.main_ids.count("main") != 1:
        issues.append(("P1", f"main#main 数量为 {p.main_ids.count('main')}（应为 1）"))
    if not p.title:
        issues.append(("P1", "缺少 <title>"))
    if p.h1 == 0:
        issues.append(("P2", "没有 h1"))
    elif p.h1 > 1:
        issues.append(("P2", f"h1 有 {p.h1} 个"))
    if p.imgs_no_alt:
        issues.append(("P2", f"{p.imgs_no_alt} 个 img 缺 alt"))
    if p.buttons_no_type:
        issues.append(("P2", f"{p.buttons_no_type} 个 button 缺 type"))
    if p.blank_no_rel:
        issues.append(("P2", f"{p.blank_no_rel} 个 target=_blank 缺 rel=noopener"))
    if p.dead_hash:
        issues.append(("P1", f"{p.dead_hash} 个 href=# 死链"))

    for v in p.refs:
        u = urlsplit(v)
        if any(h in v for h in BANNED_HOSTS):
            p.banned.append(v)
        if u.scheme == "http":
            p.http_links.append(v)
        if u.scheme or u.netloc or not u.path or u.path.startswith("data:"):
            continue
        if any(v.startswith(dp) for dp in DYNAMIC_PREFIXES):
            continue
        pure = unquote(u.path)
        if pure == '/inno/legacy/':
            target = root
        elif pure.startswith('/inno/legacy/'):
            target = root / pure[len('/inno/legacy/'):]
        elif pure.startswith("/"):
            target = None
            for prefix, mapped in ROUTE_MAP:
                if pure == prefix or pure.startswith(prefix):
                    rest = pure[len(prefix):]
                    if mapped.endswith(".html"):
                        target = root / mapped
                    else:
                        target = root / mapped / rest
                    break
            if target is None:
                target = root / pure.lstrip("/")
        elif base:
            target = root / pure if base == '/inno/legacy/' else root / (base.lstrip("/") + pure)
        else:
            target = (path.parent / pure)
        if not target.exists():
            if pure.endswith("/") and (target.parent / (target.name + ".html")).exists():
                continue
            if (target / "index.html").exists():
                continue
            issues.append(("P0", f"断链 {v}"))
    if p.banned:
        issues.append(("P0", f"{len(p.banned)} 处旧域名引用：{p.banned[0][:60]}"))
    for host in BANNED_HOSTS:
        # 文本与脚本内容中的旧域名（配置示例、说明文字等不在 href/src 中的引用）
        text_hits = len(re.findall(re.escape(host), text)) - sum(v.count(host) for v in p.refs)
        if text_hits > 0:
            issues.append(("P0", f"{text_hits} 处文本中的旧域名 {host}"))
    if p.http_links:
        issues.append(("P2", f"{len(p.http_links)} 个 http:// 链接"))

    # 链接文本中的箭头字符
    for m in re.finditer(r"<a\b[^>]*>([^<]*[" + re.escape(ARROW_CHARS) + r"][^<]*)</a>", text):
        p.arrow_anchors += 1
    if p.arrow_anchors:
        issues.append(("P2", f"{p.arrow_anchors} 个链接文本含箭头字符"))
    return issues


def main():
    ap = argparse.ArgumentParser(description="118 全站视觉与一致性审计")
    ap.add_argument("--root", default="output/inno-preview/gooddesign-site")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-per-rule", type=int, default=12)
    args = ap.parse_args()
    root = Path(args.root)
    if not root.is_dir():
        print(f"构建目录不存在: {root}", file=sys.stderr)
        raise SystemExit(2)

    by_rule = defaultdict(list)
    counts = defaultdict(int)
    total = 0
    for path in sorted(root.rglob("*.html")):
        rel = "/" + path.relative_to(root).as_posix()
        total += 1
        for sev, msg in audit_page(path, root):
            key = f"{sev} {re.sub(r'\\d+', 'N', msg)[:70]}"
            counts[key] += 1
            if len(by_rule[key]) < args.max_per_rule:
                by_rule[key].append(rel)
    report = {"schema": SCHEMA, "root": str(root), "pages": total,
              "rules": [{"rule": k, "count": v, "examples": by_rule[k]}
                        for k, v in sorted(counts.items(), key=lambda x: (x[0][:2], -x[1]))],
              "whitelist": sorted(CHROME_WHITELIST)}
    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            raise FileExistsError(f"审计报告不可覆盖: {out}")
        out.write_text(text + "\n", encoding="utf-8")
    p0 = sum(v for k, v in counts.items() if k.startswith("P0"))
    p1 = sum(v for k, v in counts.items() if k.startswith("P1"))
    p2 = sum(v for k, v in counts.items() if k.startswith("P2"))
    p3 = sum(v for k, v in counts.items() if k.startswith("P3"))
    print(f"审计 {total} 页：P0={p0} P1={p1} P2={p2} P3={p3}")
    for r in report["rules"]:
        print(f"  {r['rule']} ×{r['count']}  例: {', '.join(r['examples'][:3])}")
    raise SystemExit(1 if p0 or p1 else 0)


if __name__ == "__main__":
    main()
