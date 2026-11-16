#!/usr/bin/env python3
"""GDRP 可视化报告渲染器：research-pack.json -> report.html

规则（specs/102 第6节）：
- 逐字段消费 research-pack.json，先过 JSON Schema 再渲染；
- 只搬运字段，不发明事实；pack 中没有的项目名称等一律不补；
- 未知、待审、未授权状态原样可见；recommendations=[] 明示；
- 页面正文不得出现破折号字符（—、–），渲染时统一替换并断言。
"""
import argparse
import html
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

STD_ROOT = Path(__file__).resolve().parent.parent / "04-知识库/项目档案标准-v1" / "创新研究输出物标准-v1"

DELIVERY_LEVELS = {
    "L0_brief": "L0 简报",
    "L1_concept_pack": "L1 概念研究包",
    "L2_validated_pack": "L2 验证研究包",
    "L3_engineering_pack": "L3 工程研究包",
}
EXEC_STATUS = {"review_pending": "待审阅"}
JUDGMENT_VALUES = {"unknown": "未知", "pass": "通过", "fail": "未通过", "na": "不适用"}
REVIEW_LABELS = [
    ("customer_confirmed", "客户确认"),
    ("semantic_review", "语义复核"),
    ("domain_expert", "领域专家"),
    ("engineering_validated", "工程验证"),
    ("public_authorized", "公开授权"),
    ("training_authorized", "训练授权"),
]


def clean(text):
    """去掉页面禁用的破折号字符。"""
    return str(text).replace("—", "至").replace("–", "-")


def esc(text):
    return html.escape(clean(text), quote=True)


def join_cn(items):
    return "、".join(esc(i) for i in items)


def ul(items, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f"<ul{c}>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def labeled_badge(req):
    if req.get("hard") is True:
        return '<span class="badge badge-hard">硬性</span>'
    if req.get("hard") is None:
        return '<span class="badge badge-neutral">硬软未决</span>'
    return '<span class="badge badge-neutral">软性</span>'


CSS = r"""
:root{
  --bg:#f4f4f7;--panel:#ffffff;--ink:#1c1c22;--ink-2:#55555f;--ink-3:#8a8a94;
  --line:#e4e4ea;--accent:#5a4fe6;--accent-soft:#efedfc;
  --cover:#15151c;--cover-2:#1d1d27;--cover-ink:#f2f2f7;--cover-ink-2:rgba(236,238,255,.72);
  --warn:#9a6a12;--radius:12px;
}
@media (prefers-color-scheme: dark){
  :root{--bg:#141419;--panel:#1d1d26;--ink:#e9eaf2;--ink-2:#b9bac6;--ink-3:#85868f;
    --line:#2e2e3a;--accent:#8b81f2;--accent-soft:#26243a;}
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;font-size:15px;line-height:1.75;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.cover{background:linear-gradient(160deg,var(--cover) 0%,var(--cover-2) 100%);color:var(--cover-ink);padding:56px 24px 48px}
.cover-inner{max-width:1200px;margin:0 auto}
.cover .kicker{font-size:12px;letter-spacing:.12em;color:#9d95f5;font-weight:600;margin-bottom:14px}
.cover h1{font-size:32px;line-height:1.35;font-weight:700;letter-spacing:.01em;max-width:760px}
.cover .lede{margin-top:14px;max-width:720px;color:var(--cover-ink-2);font-size:15px}
.meta-chips{margin-top:26px;display:flex;flex-wrap:wrap;gap:8px}
.meta-chips span{font-size:12.5px;padding:5px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.18);color:var(--cover-ink-2);white-space:nowrap}
.meta-chips span strong{color:var(--cover-ink);font-weight:600}
.shell{max-width:1200px;margin:0 auto;padding:36px 24px 80px;display:grid;grid-template-columns:210px minmax(0,1fr);gap:36px;align-items:start}
.toc{position:sticky;top:24px;font-size:13.5px}
.toc .toc-title{font-size:12px;letter-spacing:.1em;color:var(--ink-3);font-weight:600;margin-bottom:10px}
.toc a{display:block;padding:7px 10px;border-radius:8px;color:var(--ink-2);line-height:1.5}
.toc a:hover{background:var(--panel);color:var(--ink);text-decoration:none}
.toc a .n{color:var(--ink-3);margin-right:6px;font-variant-numeric:tabular-nums}
.section{margin-bottom:44px;scroll-margin-top:20px}
.section > h2{font-size:21px;font-weight:700;letter-spacing:.01em;margin-bottom:6px}
.section > .sub{color:var(--ink-2);font-size:14px;margin-bottom:18px;max-width:720px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:22px 24px}
.panel + .panel{margin-top:14px}
.badge{display:inline-block;font-size:11.5px;font-weight:600;padding:2px 9px;border-radius:999px;white-space:nowrap;vertical-align:1px}
.badge-hard{color:var(--accent);background:var(--accent-soft)}
.badge-neutral{color:var(--ink-2);background:var(--bg);border:1px solid var(--line)}
.badge-warn{color:var(--warn);background:#faf3e3}
@media (prefers-color-scheme: dark){.badge-warn{background:#2e2718}}
.stat-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:16px}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px}
.stat .v{font-size:22px;font-weight:700;font-variant-numeric:tabular-nums}
.stat .k{font-size:12.5px;color:var(--ink-2);margin-top:2px}
.decision{border-left:3px solid var(--accent)}
.decision .big{font-size:17px;font-weight:650;line-height:1.7}
.decision .why{margin-top:10px;color:var(--ink-2);font-size:14px}
.decision code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;background:var(--accent-soft);color:var(--accent);padding:1px 7px;border-radius:6px}
.req{padding:16px 0;border-bottom:1px solid var(--line)}
.req:last-child{border-bottom:none}
.req .head{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.req .rid{font-weight:700;font-variant-numeric:tabular-nums;color:var(--accent);font-size:13.5px}
.req .rtext{font-weight:600}
.req .acc{color:var(--ink-2);font-size:13.5px;margin-top:5px}
.req .acc b{color:var(--ink-3);font-weight:600}
.req .refs{color:var(--ink-3);font-size:12.5px;margin-top:4px}
.case-card h3{font-size:15.5px;font-weight:700}
.case-card .who{color:var(--ink-3);font-size:12.5px;margin-top:2px}
.case-card dl{margin-top:12px;display:grid;gap:10px}
.case-card dt{font-size:12px;font-weight:600;color:var(--ink-3);letter-spacing:.04em}
.case-card dd{font-size:14px;color:var(--ink)}
.case-card dd ul{list-style:none}
.case-card dd li{padding-left:14px;position:relative}
.case-card dd li::before{content:"";position:absolute;left:0;top:.72em;width:6px;height:1.5px;background:var(--ink-3)}
.fn-group{margin-bottom:8px}
.fn-group h3{font-size:14.5px;font-weight:700;padding:12px 0 6px}
.fn-group h3 .fid{color:var(--accent);font-variant-numeric:tabular-nums;margin-right:6px}
.opt{display:grid;grid-template-columns:56px 1fr;gap:12px;padding:8px 0;border-bottom:1px dashed var(--line);font-size:13.5px}
.opt:last-child{border-bottom:none}
.opt .oid{font-variant-numeric:tabular-nums;color:var(--ink-3);font-weight:600}
.opt .ocond{color:var(--ink-3);font-size:12.5px;margin-top:2px}
.flow-list{list-style:none;font-size:13.5px}
.flow-list li{padding:7px 0;border-bottom:1px dashed var(--line);color:var(--ink-2)}
.flow-list li:last-child{border-bottom:none}
.flow-list b{color:var(--ink);font-variant-numeric:tabular-nums}
.concept-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-top:14px}
.concept{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:18px}
.concept .cid{font-size:17px;font-weight:700;color:var(--accent)}
.concept .cname{font-weight:650;margin-top:2px}
.concept .cpath{font-size:12px;color:var(--ink-3);margin-top:8px;font-variant-numeric:tabular-nums;word-break:break-all}
.concept .cwhy{font-size:13px;color:var(--ink-2);margin-top:8px}
.matrix-scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.matrix{display:grid;grid-template-columns:72px repeat(15,minmax(46px,1fr));min-width:820px;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;background:var(--panel)}
.matrix > div{padding:8px 6px;font-size:12px;text-align:center;border-bottom:1px solid var(--line);border-right:1px solid var(--line)}
.matrix .mh{background:var(--accent-soft);color:var(--accent);font-weight:700;font-variant-numeric:tabular-nums}
.matrix .mr{background:var(--bg);font-weight:700;font-variant-numeric:tabular-nums}
.matrix .cell-u{color:var(--ink-3)}
.matrix-note{font-size:13px;color:var(--ink-2);margin-top:12px}
.gates{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.gate{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;border-top:3px solid var(--accent)}
.gate .gid{font-weight:700;font-variant-numeric:tabular-nums;font-size:15px}
.gate .gwhat{font-size:13.5px;margin-top:4px}
.gate .gstatus{font-size:12px;color:var(--ink-3);margin-top:8px}
.vmethods{list-style:none;font-size:13px}
.vmethods li{padding:7px 0;border-bottom:1px dashed var(--line);display:grid;grid-template-columns:52px 76px 1fr;gap:10px}
.vmethods li:last-child{border-bottom:none}
.vmethods .vid{font-variant-numeric:tabular-nums;color:var(--accent);font-weight:600}
.vmethods .vm{color:var(--ink-2)}
.vmethods .vc{color:var(--ink-3)}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.tabs button{font:inherit;font-size:13.5px;font-weight:600;padding:8px 16px;border-radius:999px;border:1px solid var(--line);background:var(--panel);color:var(--ink-2);cursor:pointer;white-space:nowrap}
.tabs button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.tabs button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.kv{display:grid;grid-template-columns:150px 1fr;gap:6px 18px;font-size:14px}
.kv dt{color:var(--ink-3);font-size:13px;padding:6px 0}
.kv dd{padding:6px 0;border-bottom:1px dashed var(--line)}
.kv dd ul{list-style:none}
.kv dd li{padding:2px 0}
.empty{color:var(--ink-3);font-size:13.5px}
.review-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px}
.review-item{border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px;background:var(--panel);font-size:13px}
.review-item .rk{color:var(--ink-3);font-size:12px}
.review-item .rv{font-weight:650;margin-top:2px}
.src-table{width:100%;border-collapse:collapse;font-size:13px}
.src-table th,.src-table td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line)}
.src-table th{color:var(--ink-3);font-weight:600;font-size:12px;letter-spacing:.04em}
.src-table td{font-variant-numeric:tabular-nums}
.note-list{list-style:none}
.note-list li{padding:10px 0 10px 16px;border-bottom:1px dashed var(--line);position:relative;color:var(--ink-2);font-size:14px}
.note-list li:last-child{border-bottom:none}
.note-list li::before{content:"";position:absolute;left:0;top:1.05em;width:7px;height:7px;border-radius:50%;background:var(--accent);opacity:.55}
.foot{max-width:1200px;margin:0 auto;padding:0 24px 56px;color:var(--ink-3);font-size:12.5px}
@media (max-width:960px){
  .shell{grid-template-columns:minmax(0,1fr);padding-top:24px}
  .toc{position:sticky;top:0;z-index:5;background:var(--bg);margin:0 -24px;padding:10px 24px;display:flex;gap:4px;overflow-x:auto;-webkit-overflow-scrolling:touch;border-bottom:1px solid var(--line)}
  .toc .toc-title{display:none}
  .toc a{white-space:nowrap;padding:6px 10px;font-size:13px}
  .cover{padding:40px 20px 36px}
  .cover h1{font-size:24px}
  .kv{grid-template-columns:1fr}
  .kv dt{padding-bottom:0}
  .vmethods li{grid-template-columns:44px 64px 1fr}
}
@media print{
  .toc{display:none}
  .shell{display:block;padding:0}
  .cover{background:#15151c !important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
  .matrix-scroll{overflow:visible}
  .section{break-inside:avoid-page}
  .tabpanel[hidden]{display:block}
}
"""


def render_cover(pack):
    task = pack["task"]
    chips = [
        ("任务", task["task_id"]),
        ("版本", task["revision"]),
        ("交付层级", DELIVERY_LEVELS.get(task["delivery_level"], task["delivery_level"])),
        ("引擎", pack["execution"]["engine_version"]),
        ("执行模式", pack["execution"]["mode"]),
        ("状态", EXEC_STATUS.get(pack["execution"]["status"], pack["execution"]["status"])),
        ("数据契约", pack["schema_version"]),
    ]
    chips_html = "".join(f"<span>{esc(k)} <strong>{esc(v)}</strong></span>" for k, v in chips)
    return f"""<header class="cover">
  <div class="cover-inner">
    <div class="kicker">GDRP 可视化报告 · 由 research-pack.json 生成</div>
    <h1>{esc(task['title'])}</h1>
    <p class="lede">{esc(pack['summary']['outcome'])}</p>
    <div class="meta-chips">{chips_html}</div>
  </div>
</header>"""


def render_decision(pack):
    comparison = pack["comparison"]
    recs = comparison.get("recommendations", [])
    judgments = comparison.get("judgments", [])
    unknown_count = sum(1 for j in judgments if j.get("value") == "unknown")
    gates = pack["validation_plan"].get("gates", [])
    next_gate = next((g["id"] for g in gates if g.get("status") == "planned"), gates[0]["id"] if gates else "")
    if recs:
        big = "本次给出 {} 项推荐，详见比较章节。".format(len(recs))
        code = ""
    else:
        big = "本次不给出唯一工程推荐。<code>recommendations = []</code> 是合法完成状态。"
        code = ""
    why_bits = []
    if unknown_count:
        why_bits.append(
            f"{len(pack['comparison']['candidate_ids'])} 个概念组合对 {len(comparison['criteria'])} 项准则共 {len(judgments)} 格判断，"
            f"其中 {unknown_count} 格保留未知：未取得同条件客户基线、已冻结验收目标或实测，不以相同分或中分填补。"
        )
    if pack["comparison"].get("unknowns"):
        why_bits.append(join_cn(pack["comparison"]["unknowns"]) + "。")
    stats = [
        (len(pack["problem_brief"]["requirements"]), "研究需求"),
        (len(pack["function_model"]["functions"]), "必要功能"),
        (len(pack["concept_set"]["options"]), "机制选项"),
        (len(pack["concept_set"]["combinations"]), "概念组合"),
        (unknown_count, "未知判断"),
        (next_gate, "下一步门禁"),
    ]
    stats_html = "".join(
        f'<div class="stat"><div class="v">{esc(v)}</div><div class="k">{esc(k)}</div></div>' for v, k in stats
    )
    return f"""<section class="section" id="s0">
  <h2>决策摘要</h2>
  <p class="sub">30 秒读完：这次研究给出了什么、没给出什么、下一步做什么。</p>
  <div class="panel decision">
    <p class="big">{big}{code}</p>
    <p class="why">{''.join(why_bits)}</p>
  </div>
  <div class="stat-row">{stats_html}</div>
</section>"""


def render_problem(pack):
    brief = pack["problem_brief"]
    reqs = []
    for r in brief["requirements"]:
        refs = "、".join(esc(x) for x in r.get("evidence_refs", [])) or "无"
        reqs.append(f"""<div class="req">
  <div class="head"><span class="rid">{esc(r['id'])}</span>{labeled_badge(r)}<span class="rtext">{esc(r['text'])}</span></div>
  <p class="acc"><b>验收口径：</b>{esc(r['acceptance'])}</p>
  <p class="refs">状态 {esc(r['status'])} · 证据 {refs}</p>
</div>""")
    notes = [f"研究边界：{brief['boundary']}"]
    if brief.get("unknowns"):
        notes.append("未确认条件：" + "；".join(brief["unknowns"]) + "。")
    if brief.get("actor"):
        notes.append(f"相关方：{brief['actor']}。")
    return f"""<section class="section" id="s1">
  <h2>问题与边界</h2>
  <p class="sub">{esc(pack['summary']['problem'])}</p>
  <div class="panel">{''.join(reqs)}</div>
  <div class="panel"><ul class="note-list">{''.join(f'<li>{esc(n)}</li>' for n in notes)}</ul></div>
</section>"""


def render_cases(pack):
    counts = {c["project_id"]: c.get("record_count", 0) for c in pack.get("case_retrieval", [])}
    revisions = {c["project_id"]: c.get("revision", "") for c in pack.get("case_retrieval", [])}
    fn_names = {f["id"]: f["verb_object"] for f in pack["function_model"]["functions"]}
    cards = []
    for tm in pack.get("transfer_maps", []):
        pid = tm["source_case"]
        fn = tm["target_function"]
        fn_label = f"{fn} {fn_names.get(fn, '')}".strip()
        diffs = "".join(f"<li>{esc(d)}</li>" for d in tm.get("differences", []))
        nots = "".join(f"<li>{esc(d)}</li>" for d in tm.get("not_transferable", []))
        status_cls = "badge-warn" if tm.get("status") == "research_only" else "badge-neutral"
        cards.append(f"""<div class="panel case-card">
  <h3>来源项目 {esc(pid)} <span class="badge {status_cls}">{esc(tm.get('status',''))}</span></h3>
  <p class="who">研究版 {esc(revisions.get(pid,''))} · {counts.get(pid,0)} 条记录 · 目标功能 {esc(fn_label)}</p>
  <dl>
    <dt>可借鉴机制</dt><dd>{esc(tm['mechanism'])}</dd>
    <dt>关键差异</dt><dd><ul>{diffs}</ul></dd>
    <dt>不能迁移</dt><dd><ul>{nots}</ul></dd>
    <dt>证伪路径</dt><dd>{esc(tm['falsification_path'])}</dd>
  </dl>
</div>""")
    total = sum(counts.values())
    sub = f"从项目库检索 {len(counts)} 个来源案例，逐项写明可借鉴的机制、关键差异、不能迁移的部分与证伪路径。检索合计 {total} 条记录。"
    return f"""<section class="section" id="s2">
  <h2>案例与机制</h2>
  <p class="sub">{esc(sub)}</p>
  {''.join(cards)}
</section>"""


def render_functions(pack):
    fm = pack["function_model"]
    cs = pack["concept_set"]
    options_by_fn = {}
    for o in cs["options"]:
        options_by_fn.setdefault(o["function_id"], []).append(o)
    groups = []
    for f in fm["functions"]:
        opts = []
        for o in options_by_fn.get(f["id"], []):
            conds = "；".join(o.get("conditions", []))
            refs = "、".join(o.get("evidence_refs", []))
            meta_parts = []
            if conds:
                meta_parts.append(conds)
            if refs:
                meta_parts.append(f"证据 {refs}")
            opts.append(
                f'<div class="opt"><span class="oid">{esc(o["id"])}</span><div>{esc(o["principle"])}'
                f'<div class="ocond">{esc("；".join(meta_parts))}</div></div></div>'
            )
        groups.append(
            f'<div class="fn-group"><h3><span class="fid">{esc(f["id"])}</span>{esc(f["verb_object"])}</h3>{"".join(opts)}</div>'
        )
    flows = []
    flow_types = {"signal": "信号", "material": "物料", "energy": "能量"}
    for fl in fm.get("flows", []):
        flows.append(
            f"<li><b>{esc(fl['id'])}</b> {esc(fl['from_function'])} 到 {esc(fl['to_function'])} · "
            f"{esc(flow_types.get(fl['flow_type'], fl['flow_type']))} · {esc(fl['description'])}</li>"
        )
    for itf in fm.get("interfaces", []):
        flows.append(f"<li><b>{esc(itf['id'])}</b> 接口 · {esc(itf['text'])}</li>")
    concepts = []
    for c in cs["combinations"]:
        path = " · ".join(esc(x) for x in c["option_ids"])
        concepts.append(f"""<div class="concept">
  <div class="cid">{esc(c['id'])}</div>
  <div class="cname">状态 {esc(c.get('status',''))}</div>
  <div class="cpath">{path}</div>
  <p class="cwhy">{esc(c.get('reason',''))}</p>
</div>""")
    n_fn = len(fm["functions"])
    n_opt = len(cs["options"])
    sub = (
        f"{n_fn} 个必要功能、{len(fm.get('flows', []))} 条流、{len(fm.get('interfaces', []))} 条接口、"
        f"{n_opt} 个机制选项，组合为 {len(cs['combinations'])} 个概念。"
        "理论组合空间远大于已研究集合，本报告不宣称已研究全部方案。"
    )
    return f"""<section class="section" id="s3">
  <h2>功能与概念</h2>
  <p class="sub">{esc(sub)}</p>
  <div class="panel">{''.join(groups)}</div>
  <div class="panel"><ul class="flow-list">{''.join(flows)}</ul></div>
  <div class="concept-grid">{''.join(concepts)}</div>
</section>"""


def render_comparison(pack):
    comp = pack["comparison"]
    criteria = comp["criteria"]
    candidates = comp["candidate_ids"]
    judgments = {(j["candidate_id"], j["criterion_id"]): j for j in comp.get("judgments", [])}
    n = len(criteria)
    cells = ['<div class="mh" role="columnheader">准则</div>']
    cells += [f'<div class="mh" role="columnheader">{esc(c["id"])}</div>' for c in criteria]
    for cand in candidates:
        cells.append(f'<div class="mr" role="rowheader">{esc(cand)}</div>')
        for c in criteria:
            j = judgments.get((cand, c["id"]))
            value = j.get("value") if j else "missing"
            label = JUDGMENT_VALUES.get(value, value)
            cls = "cell-u" if value in ("unknown", "missing") else "cell-v"
            title = html.escape(j.get("basis", ""), quote=True) if j else ""
            cells.append(f'<div class="{cls}" title="{title}">{esc(label)}</div>')
    matrix = (
        f'<div class="matrix-scroll"><div class="matrix" role="table" '
        f'style="grid-template-columns:72px repeat({n},minmax(46px,1fr))" '
        f'aria-label="概念比较矩阵，{len(comp.get("judgments", []))} 格">{"".join(cells)}</div></div>'
    )
    notes = []
    if comp.get("sensitivity"):
        notes.append("敏感性：" + "；".join(comp["sensitivity"]) + "。")
    notes += comp.get("unknowns", [])
    req_ids = [c["id"].replace("K", "N", 1) for c in criteria]
    sub = (
        f"{len(candidates)} 个候选对 {n} 项准则共 {len(comp.get('judgments', []))} 格判断。"
        "每一格保留原始判断值；未知不以相同或中分填补。"
    )
    note_line = (
        f"准则 {criteria[0]['id']} 至 {criteria[-1]['id']} 与需求 {req_ids[0]} 至 {req_ids[-1]} 一一对应。"
        if criteria else ""
    )
    return f"""<section class="section" id="s4">
  <h2>比较与推荐门禁</h2>
  <p class="sub">{esc(sub)}</p>
  {matrix}
  <p class="matrix-note">{esc(note_line)}给出推荐必须先确认需求与基线，再经门禁取得同条件证据。</p>
  <div class="panel"><ul class="note-list">{''.join(f'<li>{esc(x)}</li>' for x in notes)}</ul></div>
</section>"""


def render_validation(pack):
    vp = pack["validation_plan"]
    gates = "".join(
        f'<div class="gate"><div class="gid">{esc(g["id"])}</div><div class="gwhat">{esc(g["purpose"])}</div>'
        f'<div class="gstatus">状态 {esc(g.get("status",""))}</div></div>'
        for g in vp.get("gates", [])
    )
    rows = "".join(
        f'<li><span class="vid">{esc(m["requirement_id"])}</span><span class="vm">{esc(m["method"])}</span>'
        f'<span class="vc">{esc(m["criterion"])}</span></li>'
        for m in vp.get("matrix", [])
    )
    sub = (
        f"{len(vp.get('gates', []))} 级门禁。{len(vp.get('matrix', []))} 项需求到验证方法的映射已建立，"
        f"执行状态 {vp.get('execution_status', '')}。"
    )
    return f"""<section class="section" id="s5">
  <h2>验证计划</h2>
  <p class="sub">{esc(sub)}</p>
  <div class="gates">{gates}</div>
  <div class="panel" style="margin-top:14px"><ul class="vmethods">{rows}</ul></div>
</section>"""


def _kv(rows):
    body = "".join(f"<dt>{esc(k)}</dt><dd>{v}</dd>" for k, v in rows)
    return f'<dl class="kv">{body}</dl>'


def _empty(text):
    return f'<span class="empty">{esc(text)}</span>'


def _list_or_empty(items, empty_text):
    if not items:
        return _empty(empty_text)
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def render_product(p):
    fp = p.get("feature_priorities", {})
    ba = p.get("business_assumptions", {})
    eod = p.get("evidence_of_desirability", {})
    rows = [
        ("目标用户", join_cn(p.get("target_users", []))),
        ("用户价值", esc(p.get("user_value", ""))),
        ("使用旅程", join_cn(p.get("journey", []))),
        ("概念架构", join_cn(p.get("concept_architecture", []))),
        ("必须研究", join_cn(fp.get("must_research", []))),
        ("可选", join_cn(fp.get("optional", []))),
        ("暂缓", join_cn(fp.get("defer", []))),
        ("MVP 范围", esc(p.get("mvp_scope", ""))),
        ("商业假设", esc(f"成本、价格、利用率均未取得，原因：{ba.get('reason', '')}")
         if ba.get("cost") is None else esc(str(ba))),
        ("需求证据", esc(f"状态 {eod.get('status', '')}；下一步：{eod.get('next', '')}")),
    ]
    return _kv(rows)


def render_engineering(e):
    fns = e.get("technical_architecture", [])
    fn_summary = "、".join(f"{f['id']} {f['verb_object']}" for f in fns)
    itfs = [f"{i['id']} {i['text']}（{i.get('kind', '')}）" for i in e.get("interface_register", [])]
    opts = e.get("mechanism_options", [])
    vm = e.get("verification_matrix", [])
    rows = [
        ("系统边界", esc(e.get("system_boundary", ""))),
        ("技术架构", esc(fn_summary)),
        ("接口登记", _list_or_empty(itfs, "空。")),
        ("机制选项", esc(f"{len(opts)} 个选项按功能分组，全部为研究选项，条件待确认")),
        ("工程风险", _list_or_empty(e.get("engineering_risks", []), "空。")),
        ("计算记录", _list_or_empty(e.get("calculation_records", []), "空。本层级不包含工程计算。")),
        ("求解器结果", _list_or_empty(e.get("solver_results", []), "空。未运行求解器。")),
        ("验证矩阵", esc(f"{len(vm)} 行，证据状态见验证计划章节")),
    ]
    return _kv(rows)


def render_ai4s(a):
    variables = a.get("variables", {})
    dp = a.get("data_plan", {})
    ed = a.get("experiment_design", {})
    se = a.get("scientific_evidence", {})
    rp = a.get("reproducibility", {})
    rows = [
        ("科学问题", esc(a.get("scientific_question", ""))),
        ("假设", _list_or_empty(a.get("hypotheses", []), "空。")),
        ("自变量", join_cn(variables.get("independent", []))),
        ("因变量", join_cn(variables.get("dependent", []))),
        ("控制变量", join_cn(variables.get("controlled", []))),
        ("混杂因素", join_cn(variables.get("confounders", []))),
        ("数据计划", esc(f"{dp.get('samples', '')}；{dp.get('quality', '')}")),
        ("实验设计", esc(
            f"门禁 {' 至 '.join([ed.get('gates', [''])[0], ed.get('gates', [''])[-1]]) if ed.get('gates') else ''}；"
            f"基线：{ed.get('baseline', '')}；停止条件：{'、'.join(ed.get('stop_conditions', []))}"
        )),
        ("不确定性", _list_or_empty(a.get("uncertainty", []), "空。")),
        ("可复现性", esc(
            f"任务 {rp.get('task_id', '')} {rp.get('revision', '')}；"
            f"方法版本 {'、'.join(rp.get('method_versions', []))}；"
            f"执行 {rp.get('execution_mode', '')}；模型后台 {rp.get('model_backend', '')}"
        )),
        ("科学证据", esc(
            f"已支持：{len(se.get('supported', []))} 条；已证伪：{len(se.get('refuted', []))} 条；"
            f"未知：{'、'.join(se.get('unknown', []))}"
        )),
    ]
    return _kv(rows)


DOMAIN_TABS = [
    ("product", "产品创新", render_product),
    ("engineering", "工程创新", render_engineering),
    ("ai4s", "AI4S", render_ai4s),
]


def render_domains(pack):
    ext = pack.get("domain_extension", {})
    buttons, panels = [], []
    first = True
    for key, label, fn in DOMAIN_TABS:
        if key not in ext:
            continue
        buttons.append(
            f'<button type="button" aria-pressed="{"true" if first else "false"}" data-tab="{key}">{esc(label)}</button>'
        )
        hidden = "" if first else " hidden"
        panels.append(f'<div class="panel tabpanel" data-panel="{key}"{hidden}>{fn(ext[key])}</div>')
        first = False
    return f"""<section class="section" id="s6">
  <h2>领域扩展</h2>
  <p class="sub">同一份研究包按产品创新、工程创新、AI4S 三个视角展开，字段均来自 research-pack 的 domain_extension。</p>
  <div class="tabs" role="group" aria-label="领域切换">{''.join(buttons)}</div>
  {''.join(panels)}
</section>"""


def render_execution(pack):
    exe = pack["execution"]
    review = pack["review"]
    mc = exe.get("model_calls", {})
    mc_status = {"failed": "失败", "success": "成功", "not_used": "未使用"}.get(mc.get("status", ""), mc.get("status", ""))
    kv_rows = [
        ("执行模式", esc(exe.get("mode", ""))),
        ("模型调用", esc(f"{mc_status}。成功调用 {mc.get('count', 0)} 次。{mc.get('note', '')}")),
        ("方法版本", esc("、".join(f"{m['research_id']}（{m.get('status', '')}）" for m in exe.get("method_versions", [])))),
        ("执行状态", esc(exe.get("status", ""))),
    ]
    kv = '<dl class="kv">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in kv_rows) + "</dl>"
    review_items = []
    for key, label in REVIEW_LABELS:
        v = review.get(key)
        if isinstance(v, bool):
            v = "是" if v else "否"
        review_items.append(
            f'<div class="review-item"><div class="rk">{esc(label)}</div><div class="rv">{esc(v)}</div></div>'
        )
    src_rows = "".join(
        f"<tr><td>{esc(s['project_id'])}</td><td>{esc(s.get('revision',''))}</td><td>{s.get('record_count',0)}</td></tr>"
        for s in exe.get("source_versions", [])
    )
    return f"""<section class="section" id="s7">
  <h2>执行、审核与版本</h2>
  <p class="sub">谁做的、怎么做的、审核到哪一步。模型调用失败如实记录，不得隐藏。</p>
  <div class="panel">{kv}</div>
  <div class="review-grid" style="margin-top:14px">{''.join(review_items)}</div>
  <div class="panel" style="margin-top:14px">
    <table class="src-table">
      <thead><tr><th>来源项目</th><th>研究版本</th><th>记录数</th></tr></thead>
      <tbody>{src_rows}</tbody>
    </table>
  </div>
</section>"""


def render_appendix(pack):
    evidence = pack.get("evidence", [])
    boundary = pack.get("boundary", {})
    notes = []
    if evidence:
        scopes = sorted({e.get("read_scope", "") for e in evidence})
        notes.append(
            f"证据 {len(evidence)} 条：每条含来源 ID、来源修订指纹、块 ID、字符区间定位、文本指纹；"
            f"读取范围 {'、'.join(scopes)}。"
        )
    else:
        notes.append("本研究包不含证据条目。")
    notes += boundary.get("notes", [])
    notes.append(f"源事实未被修改（source_facts_modified = {str(boundary.get('source_facts_modified')).lower()}）；"
                 f"物理试验授权（physical_test_authorized = {str(boundary.get('physical_test_authorized')).lower()}）。")
    notes.append("本报告由 build_gdrp_report.py 从 research-pack.json 逐字段生成，未另写事实。")
    return f"""<section class="section" id="s8">
  <h2>附录：证据与来源</h2>
  <p class="sub">证据形态、读取范围与边界原文。</p>
  <div class="panel"><ul class="note-list">{''.join(f'<li>{esc(n)}</li>' for n in notes)}</ul></div>
</section>"""


TOC = """<nav class="toc" aria-label="章节目录">
  <div class="toc-title">目录</div>
  <a href="#s0"><span class="n">0</span>决策摘要</a>
  <a href="#s1"><span class="n">1</span>问题与边界</a>
  <a href="#s2"><span class="n">2</span>案例与机制</a>
  <a href="#s3"><span class="n">3</span>功能与概念</a>
  <a href="#s4"><span class="n">4</span>比较与推荐门禁</a>
  <a href="#s5"><span class="n">5</span>验证计划</a>
  <a href="#s6"><span class="n">6</span>领域扩展</a>
  <a href="#s7"><span class="n">7</span>执行、审核与版本</a>
  <a href="#s8"><span class="n">8</span>附录：证据与来源</a>
</nav>"""

TAB_SCRIPT = """<script>
(function(){
  var buttons=document.querySelectorAll('.tabs button');
  var panels=document.querySelectorAll('.tabpanel');
  buttons.forEach(function(btn){
    btn.addEventListener('click',function(){
      buttons.forEach(function(b){b.setAttribute('aria-pressed','false');});
      btn.setAttribute('aria-pressed','true');
      panels.forEach(function(p){
        p.hidden = p.getAttribute('data-panel') !== btn.getAttribute('data-tab');
      });
    });
  });
})();
</script>"""


def render(pack):
    title = esc(pack["task"]["title"])
    body = "".join([
        render_decision(pack),
        render_problem(pack),
        render_cases(pack),
        render_functions(pack),
        render_comparison(pack),
        render_validation(pack),
        render_domains(pack),
        render_execution(pack),
        render_appendix(pack),
    ])
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · GDRP 可视化报告</title>
<style>{CSS}</style>
</head>
<body>
{render_cover(pack)}
<div class="shell">
  {TOC}
  <main id="main">
{body}
  </main>
</div>
<footer class="foot">
  <p>好设计平台 · 创新研究输出物标准 GDRP · 模板结构见 specs/102-可视化报告模板结构.md · 本报告由 build_gdrp_report.py 生成。</p>
</footer>
{TAB_SCRIPT}
</body>
</html>
"""


def self_check(pack, page):
    if "—" in page or "–" in page:
        raise SystemExit("自检失败：渲染结果含禁用破折号字符")
    if not pack["comparison"].get("recommendations") and "recommendations = []" not in page:
        raise SystemExit("自检失败：recommendations 为空但报告未明示")
    expected_cells = len(pack["comparison"]["candidate_ids"]) * len(pack["comparison"]["criteria"])
    if page.count('class="cell-') != expected_cells:
        raise SystemExit(f"自检失败：矩阵单元格数 {page.count('class=cell-')} != {expected_cells}")


def render_md(pack):
    """可编辑摘要 Markdown，字段同样只来自 research-pack。"""
    task = pack["task"]
    comp = pack["comparison"]
    judgments = comp.get("judgments", [])
    unknown = sum(1 for j in judgments if j.get("value") == "unknown")
    lines = [
        f"# {clean(task['title'])}",
        "",
        f"版本：{clean(task['task_id'])} / {clean(task['revision'])}",
        f"层级：{clean(DELIVERY_LEVELS.get(task['delivery_level'], task['delivery_level']))}",
        f"状态：{clean(EXEC_STATUS.get(pack['execution']['status'], pack['execution']['status']))}，"
        "未获客户、领域或工程验证。" if not pack["review"].get("engineering_validated") else "",
        "",
        "## 决策摘要",
        "",
        clean(pack["summary"]["outcome"]),
        "",
        f"recommendations={json.dumps(comp.get('recommendations', []), ensure_ascii=False)}；"
        f"{len(comp['candidate_ids'])} 个概念对 {len(comp['criteria'])} 项准则共 {len(judgments)} 格判断，"
        f"{unknown} 格未知。下一步：{clean(pack['summary']['next_action'])}",
        "",
        "## 需求",
        "",
    ]
    for r in pack["problem_brief"]["requirements"]:
        hard = {True: "硬性", None: "硬软未决", False: "软性"}[r.get("hard")]
        lines.append(f"- {clean(r['id'])}（{hard}，{clean(r['status'])}）：{clean(r['text'])}")
    lines += ["", "## 案例与机制", ""]
    for tm in pack.get("transfer_maps", []):
        lines.append(
            f"- 来源项目 {clean(tm['source_case'])} -> {clean(tm['target_function'])}：{clean(tm['mechanism'])}。"
            f"不能迁移：{'、'.join(clean(x) for x in tm.get('not_transferable', []))}。"
            f"证伪路径：{clean(tm['falsification_path'])}"
        )
    lines += ["", "## 概念组合", ""]
    for c in pack["concept_set"]["combinations"]:
        lines.append(f"- {clean(c['id'])}（{clean(c.get('status', ''))}）：{clean(c.get('reason', ''))}")
    lines += ["", "## 验证计划", ""]
    for g in pack["validation_plan"].get("gates", []):
        lines.append(f"- {clean(g['id'])}（{clean(g.get('status', ''))}）：{clean(g['purpose'])}")
    lines += [
        "",
        "## 执行与边界",
        "",
        f"执行模式 {clean(pack['execution']['mode'])}；模型调用 {clean(pack['execution'].get('model_calls', {}).get('status', ''))}，"
        f"成功 {pack['execution'].get('model_calls', {}).get('count', 0)} 次。",
    ]
    for n in pack.get("boundary", {}).get("notes", []):
        lines.append(f"- {clean(n)}")
    lines += [
        "",
        "本摘要由 build_gdrp_report.py 从 research-pack.json 生成，不是制造方案、专家认证或工程结论。",
        "",
    ]
    return "\n".join(lines)


def write_manifest(pack_path, outputs, manifest_path, pack):
    import hashlib
    files = {pack_path.name: hashlib.sha256(pack_path.read_bytes()).hexdigest()}
    for out in outputs:
        files[out.name] = hashlib.sha256(out.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "gdrp-manifest-0.1",
        "package_id": pack["package_id"],
        "files": files,
        "source_facts_modified": pack.get("boundary", {}).get("source_facts_modified", False),
        "note": "文件指纹用于完整性检查，不是数字签名或专家认证。",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="GDRP research-pack.json -> report.html (+report.md +manifest.json)")
    ap.add_argument("pack", type=Path, help="research-pack.json 路径")
    ap.add_argument("out", type=Path, help="输出 report.html 路径")
    ap.add_argument("--md", type=Path, help="可选：输出 report.md 路径")
    ap.add_argument("--manifest", type=Path, help="可选：输出 manifest.json 路径")
    ap.add_argument("--schema", type=Path, default=STD_ROOT / "research-pack.schema.json")
    args = ap.parse_args()

    pack = json.loads(args.pack.read_text(encoding="utf-8"))
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(pack)

    page = render(pack)
    self_check(pack, page)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")

    outputs = [args.out]
    if args.md:
        md = render_md(pack)
        if "—" in md or "–" in md:
            raise SystemExit("自检失败：Markdown 含禁用破折号字符")
        args.md.parent.mkdir(parents=True, exist_ok=True)
        args.md.write_text(md, encoding="utf-8")
        outputs.append(args.md)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        pack_copy = args.manifest.parent / args.pack.name
        if pack_copy.resolve() != args.pack.resolve():
            pack_copy.write_bytes(args.pack.read_bytes())
        write_manifest(args.pack, outputs, args.manifest, pack)
        outputs.append(args.manifest)

    comp = pack["comparison"]
    unknown = sum(1 for j in comp.get("judgments", []) if j.get("value") == "unknown")
    print(
        "GDRP pack rendered: "
        f"{len(pack['problem_brief']['requirements'])} requirements, "
        f"{len(pack['function_model']['functions'])} functions, "
        f"{len(pack['concept_set']['options'])} options, "
        f"{len(pack['concept_set']['combinations'])} concepts, "
        f"{unknown}/{len(comp.get('judgments', []))} unknown judgments, "
        f"recommendations={comp.get('recommendations', [])}, "
        f"files={[str(o) for o in outputs]}"
    )


if __name__ == "__main__":
    main()
