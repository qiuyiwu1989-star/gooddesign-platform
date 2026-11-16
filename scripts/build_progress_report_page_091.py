# coding: utf-8
import html
import json
from pathlib import Path

from gooddesign_assets import links
from gooddesign_chrome import footer, navigation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/reports'
CSS = '''
.report-shell{max-width:1180px;margin:auto;padding:36px var(--page-gutter) 56px}.report-hero{display:grid;grid-template-columns:1.15fr .85fr;gap:56px;align-items:start;padding:24px 0 36px;border-bottom:1px solid var(--bdrSoft)}.report-hero h1{margin:12px 0 16px;max-width:680px;font-size:clamp(34px,4.6vw,52px);line-height:1.18;letter-spacing:-.045em}.report-hero .gd-lead{max-width:650px}.report-date{margin:18px 0 0;color:var(--fg2);font-size:var(--fs-caption)}.report-kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.report-kpi{padding:22px;border:1px solid var(--bdrSoft);border-radius:18px;background:var(--card)}.report-kpi strong{display:block;font-size:30px;font-weight:500;line-height:1.2;letter-spacing:-.035em;font-variant-numeric:tabular-nums}.report-kpi span{display:block;margin-top:6px;color:var(--fg2);font-size:var(--fs-xs)}.report-kpi small{display:block;margin-top:4px;color:var(--fg2);font-size:11px}.report-summary{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:32px 0}.report-panel{padding:26px;border:1px solid var(--bdrSoft);border-radius:22px;background:var(--card)}.report-panel h2,.report-section h2{margin:0 0 16px;font-size:25px;line-height:1.4;letter-spacing:-.025em}.report-panel p,.report-section p{line-height:1.85}.report-panel p:last-child,.report-section p:last-child{margin-bottom:0}.report-coverage{display:flex;align-items:baseline;gap:10px}.report-coverage strong{font-size:36px;font-weight:500}.report-coverage span{color:var(--fg2);font-size:var(--fs-caption)}.report-meter{height:6px;margin:18px 0 8px;overflow:hidden;border-radius:99px;background:var(--demo)}.report-meter>i{display:block;height:100%;border-radius:inherit;background:var(--accent)}.report-note{color:var(--fg2);font-size:var(--fs-xs);line-height:1.7}.report-section{margin-top:36px}.report-section-intro{max-width:760px;color:var(--fg2)}.report-architecture{display:grid;gap:0;border-top:1px solid var(--bdrSoft)}.report-architecture-row{display:grid;grid-template-columns:180px 1fr 1fr;gap:20px;padding:18px 0;border-bottom:1px solid var(--bdrSoft)}.report-architecture-row strong{font-size:var(--fs-sm)}.report-architecture-row span,.report-architecture-row p{margin:0;color:var(--fg2);font-size:var(--fs-caption);line-height:1.75}.report-updates{display:grid;grid-template-columns:1fr 1fr;gap:14px 24px}.report-update{padding:18px 0;border-bottom:1px solid var(--bdrSoft)}.report-update strong{display:block;margin-bottom:6px;font-size:var(--fs-sm)}.report-update p{margin:0;color:var(--fg2);font-size:var(--fs-caption);line-height:1.75}.report-metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px}.report-metric{padding:18px 0;border-top:1px solid var(--bdr)}.report-metric strong{display:block;font-size:24px;font-weight:500;font-variant-numeric:tabular-nums}.report-metric span{color:var(--fg2);font-size:var(--fs-xs)}.report-queues{display:grid;gap:14px}.report-queue{display:grid;grid-template-columns:28px minmax(180px,1fr) 100px 50px;align-items:center;gap:14px}.report-queue b{font-size:var(--fs-sm)}.report-queue span{font-size:var(--fs-caption);color:var(--fg2)}.report-queue small{text-align:right;font-variant-numeric:tabular-nums}.report-issues{display:grid;grid-template-columns:1fr 1fr;gap:14px}.report-issue{padding:20px;border:1px solid var(--bdrSoft);border-radius:18px;background:var(--card)}.report-issue strong{display:block;margin-bottom:8px}.report-issue p{margin:0;color:var(--fg2);font-size:var(--fs-caption);line-height:1.75}.report-issue--warn{border-color:var(--warn)}.report-steps{display:grid;gap:16px}.report-step{display:grid;grid-template-columns:70px 1fr;gap:18px;padding-top:16px;border-top:1px solid var(--bdrSoft)}.report-step b{color:var(--accentDeep)}.report-step h3{margin:0 0 8px;font-size:18px}.report-step p{margin:0;color:var(--fg2);font-size:var(--fs-caption);line-height:1.75}.report-quote{padding:26px;border-left:3px solid var(--accent);border-radius:0 18px 18px 0;background:var(--acBg);font-size:20px;line-height:1.75}.report-evidence{display:grid;grid-template-columns:1fr 1fr;gap:12px}.report-evidence a{display:flex;align-items:center;min-height:48px;padding:10px 14px;border:1px solid var(--bdrSoft);border-radius:12px;background:var(--card);font-size:var(--fs-caption);overflow-wrap:anywhere}.report-footer-note{margin-top:28px;color:var(--fg2);font-size:var(--fs-xs);line-height:1.75}@media(max-width:900px){.report-hero{grid-template-columns:1fr;gap:28px}.report-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.report-summary{grid-template-columns:1fr}.report-architecture-row{grid-template-columns:140px 1fr}.report-architecture-row p{grid-column:2}.report-updates{grid-template-columns:1fr}}@media(max-width:560px){.report-shell{padding-top:24px}.report-kpis{grid-template-columns:1fr 1fr}.report-kpi{padding:16px}.report-panel{padding:20px}.report-architecture-row{grid-template-columns:1fr;gap:8px}.report-architecture-row p{grid-column:auto}.report-metrics{grid-template-columns:repeat(2,minmax(0,1fr))}.report-queue{grid-template-columns:24px minmax(0,1fr) 42px;gap:10px}.report-queue>span:nth-child(3){display:none}.report-issues{grid-template-columns:1fr}.report-step{grid-template-columns:48px 1fr;gap:12px}.report-evidence{grid-template-columns:1fr}}@media print{.gd-nav,.gd-footer,.gd-ip-trigger,#report-print{display:none!important}.report-shell{max-width:none;padding:0}.report-hero{display:block;padding-top:0}.report-kpis{margin-top:20px}.report-panel,.report-section,.report-kpi,.report-issue,.report-step{break-inside:avoid}.report-panel,.report-kpi,.report-issue{box-shadow:none}.report-section{break-before:auto}.report-evidence a{color:var(--fg)}}
'''
ASSET_CSS = '''
.asset-flow{display:flex;align-items:stretch;gap:10px;margin:20px 0 24px;overflow-x:auto;padding-bottom:8px}.asset-flow>div{min-width:150px;flex:1;padding:16px;border:1px solid var(--bdrSoft);border-radius:16px;background:var(--card)}.asset-flow>div+div:before{content:'·';display:block;margin:-20px 0 8px;color:var(--accent);font-size:12px}.asset-flow strong{display:block;font-size:22px;font-weight:500}.asset-flow span{color:var(--fg2);font-size:var(--fs-xs)}.asset-filters{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}.asset-filters button{min-height:40px;padding:8px 14px;border:1px solid var(--bdrSoft);border-radius:99px;background:transparent;color:var(--fg2);font-size:var(--fs-caption)}.asset-filters button[aria-pressed=true]{border-color:var(--accent);background:var(--acBg);color:var(--accentDeep)}.asset-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}.asset-card{display:flex;min-width:0;min-height:236px;padding:20px;border:1px solid var(--bdrSoft);border-radius:20px;background:var(--card);color:var(--fg);text-align:left;flex-direction:column;transition:transform var(--t-fast) var(--ease),border-color var(--t-fast),box-shadow var(--t-fast)}.asset-card:hover{transform:translateY(-2px);border-color:var(--accent);box-shadow:var(--sh1)}.asset-card:active{transform:translateY(0)}.asset-card-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px}.asset-kind{color:var(--accentDeep);font-size:var(--fs-xs);font-weight:500}.asset-status{padding:3px 8px;border-radius:99px;background:var(--acBg);color:var(--accentDeep);font-size:11px;white-space:nowrap}.asset-card h3{margin:0;font-size:18px;line-height:1.5;letter-spacing:-.015em}.asset-value{display:block;margin:14px 0 8px;font-size:28px;font-weight:500;letter-spacing:-.035em;font-variant-numeric:tabular-nums}.asset-unit{color:var(--fg2);font-size:var(--fs-xs)}.asset-card p{margin:10px 0 0;color:var(--fg2);font-size:var(--fs-caption);line-height:1.65}.asset-card-foot{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-top:auto;padding-top:16px;color:var(--accentDeep);font-size:var(--fs-xs)}.asset-meter{height:4px;margin-top:14px;overflow:hidden;border-radius:99px;background:var(--demo)}.asset-meter i{display:block;height:100%;background:var(--accent)}.asset-case-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:12px}.asset-case-metrics span{padding:6px;border-radius:8px;background:var(--demo);color:var(--fg2);font-size:11px;text-align:center}.asset-detail{width:min(620px,calc(100% - 32px));max-height:calc(100dvh - 48px);padding:28px;border:1px solid var(--bdr);border-radius:24px;background:var(--surface-content);color:var(--fg);box-shadow:var(--sh2)}.asset-detail::backdrop{background:transparent;backdrop-filter:none}.asset-detail-head{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.asset-detail-head h2{margin:6px 0 0;font-size:25px}.asset-detail-value{margin:20px 0;font-size:30px;font-weight:500}.asset-detail dl{display:grid;grid-template-columns:100px 1fr;gap:12px;margin:20px 0}.asset-detail dt{color:var(--fg2);font-size:var(--fs-caption)}.asset-detail dd{margin:0;font-size:var(--fs-caption);line-height:1.75}.asset-detail a{display:inline-flex;align-items:center;min-height:44px;margin-top:8px}@media(max-width:1100px){.asset-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:560px){.asset-grid{grid-template-columns:1fr}.asset-card{min-height:0}.asset-detail{padding:20px}.asset-detail dl{grid-template-columns:82px 1fr}}@media print{.asset-filters,.asset-detail{display:none!important}.asset-grid{grid-template-columns:repeat(2,1fr)}.asset-card{box-shadow:none;break-inside:avoid}.asset-flow{flex-wrap:wrap}}
.asset-flow>div{position:relative}.asset-flow>div+div:before{content:'';position:absolute;left:-11px;top:50%;width:10px;height:1px;margin:0;background:var(--bdr)}
.asset-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:20px}.asset-toolbar .asset-filters{margin:0}.asset-count{flex:none;margin:0;color:var(--fg2);font-size:var(--fs-xs)}
.asset-card[hidden]{display:none}.asset-card[data-kind=application]{background:var(--acBg)}.asset-card-foot{align-items:flex-end;color:var(--fg2);line-height:1.55}.asset-card-foot>span:first-child{min-width:0}.asset-open-label{flex:none;color:var(--accentDeep);font-weight:500}.asset-case-metrics strong{display:block;margin-top:3px;color:var(--fg);font-size:17px;font-weight:500}.asset-detail::backdrop{-webkit-backdrop-filter:none}
@media(max-width:560px){.asset-toolbar{align-items:flex-start;flex-direction:column;gap:10px}.asset-flow{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));overflow:visible}.asset-flow>div{min-width:0}.asset-flow>div+div:before{display:none}.asset-card-foot{padding-top:20px}.asset-detail-head{gap:10px}.asset-detail-head h2{font-size:22px}.asset-detail-value{font-size:26px}}
@media(prefers-reduced-motion:reduce){.asset-card{transition:none}.asset-card:hover{transform:none}}
@media print{.asset-toolbar{display:none!important}.asset-card[data-kind=application]{background:transparent}}
'''


def e(value):
    return html.escape(str(value), quote=True)


def knowledge_assets(data):
    r = data['research']
    p = data['product']
    c = data['case_079']
    native_percent = round(r['native_projects'] / p['index_projects'] * 100, 1)
    return [
        {
            'id': 'directory', 'kind': 'archive', 'kind_label': '项目档案', 'title': '项目目录',
            'value': p['index_projects'], 'unit': '个项目', 'status': '目录完整',
            'description': '稳定项目ID连接题录、素材目录和后续研究版本。',
            'next': '按A、B、C、D队列补齐研究，而不是重复检索全库。',
            'relation': '全部知识资产的项目入口，560个目录与权威索引一致。',
            'boundary': '目录齐全只说明资产已组织，不代表项目已完成深研。',
            'evidence': '/research-088/queues.json', 'evidence_label': '查看560个项目分层队列',
        },
        {
            'id': 'native', 'kind': 'archive', 'kind_label': '项目档案', 'title': '原生研究版',
            'value': r['native_projects'], 'unit': '个项目', 'status': f'覆盖 {native_percent}%',
            'description': f"{r['records']}条记录、{r['known_fact_cells']}个有值事实字段、{r['ai_items']}条AI分析。",
            'next': '优先核读B队列397个已有标准批但无原生版的项目。',
            'relation': f"由可追溯来源核读形成，目前覆盖{r['native_projects']} / {p['index_projects']}个项目。",
            'boundary': f"覆盖率不是质量分；2025-00仍有{r['evidence_issues']}项旧底稿证据绑定异常。",
            'evidence': '/research-088/audit-summary.json', 'evidence_label': '查看原生研究与追溯审计',
            'meter': native_percent,
        },
        {
            'id': 'full', 'kind': 'sources', 'kind_label': '来源素材', 'title': 'full 来源',
            'value': r['full_sources'], 'unit': '条来源记录', 'status': f"{r['full_batch_status']['needs_correction']}批待修",
            'description': '项目综合检索批次的实际JSONL条目，记录来源与查询过程。',
            'next': '先修正越界路径和非标准文件角色，再开展内容核读。',
            'relation': f"467个标准批中，{r['full_batch_status']['mechanical_pass_pending_content_review']}批机械通过，{r['full_batch_status']['needs_correction']}批待修。",
            'boundary': '机械通过仍需内容审核；来源条目不因结构校验失败而归零。',
            'evidence': '/research-088/audit-summary.json', 'evidence_label': '查看full批次校验结果',
        },
        {
            'id': 'patents', 'kind': 'sources', 'kind_label': '来源素材', 'title': 'patents 来源',
            'value': r['patents_sources'], 'unit': '条来源记录', 'status': f"{r['patents_batch_status']['needs_correction']}批待修",
            'description': '专利专项检索批次的实际条目，与项目综合检索分开统计。',
            'next': '修正批次结构，并将专利线索逐项核对公开文本与项目关系。',
            'relation': f"467个标准批中，{r['patents_batch_status']['mechanical_pass_pending_content_review']}批机械通过，{r['patents_batch_status']['needs_correction']}批待修。",
            'boundary': '专利lead不是公开号、权属、法律状态或项目实际采用的证明。',
            'evidence': '/research-088/audit-summary.json', 'evidence_label': '查看patents批次校验结果',
        },
        {
            'id': 'raw', 'kind': 'sources', 'kind_label': '来源素材', 'title': '原始来源文件',
            'value': r['raw_source_files'], 'unit': '个文件', 'status': '私有保存',
            'description': f"全库深研素材约{r['material_bytes'] / 1e9:.2f} GB，原件与可读件按项目归档。",
            'next': '从素材总表定位缺批、缺文档和证据绑定异常，逐项补证。',
            'relation': '原始文件为来源核读和研究版本提供本地证据基础。',
            'boundary': '文件数不等于独立来源数，也不代表全文已核读；私有原件不公开。',
            'evidence': '/research-089/material-inventory.csv', 'evidence_label': '查看560个项目素材总表',
        },
        {
            'id': 'images', 'kind': 'sources', 'kind_label': '来源素材', 'title': '图片素材',
            'value': r['image_files'], 'unit': '个文件', 'status': '版权待核',
            'description': f"图片约{r['image_bytes'] / 1e9:.2f} GB，保留来源位置与原始记录。",
            'next': '核对图片语义、项目归属和再发布授权，不用缺图项目硬补素材。',
            'relation': '图片作为项目理解与展示素材，和文字来源分别登记。',
            'boundary': '图片数量不代表可用版权或独立证据；未知授权保持未知。',
            'evidence': '/research-089/material-inventory.csv', 'evidence_label': '查看逐项目图片与缺口',
        },
        {
            'id': 'methods', 'kind': 'application', 'kind_label': '方法应用', 'title': '创新方法库',
            'value': p['method_count'], 'unit': '个方法档案', 'status': '研究稿',
            'description': '冻结基础方法与增补研究稿聚合，为项目分析提供方法参考。',
            'next': '在真实研究任务中继续校准适用条件、步骤和验证方式。',
            'relation': '连接项目证据与创新研究路线，不把方法内容混入项目原始事实。',
            'boundary': '方法档案不是专家认证，也不等于已验证的通用自动求解能力。',
            'evidence': '/reports/项目进展数据-2026-11-04.json', 'evidence_label': '查看方法资产统计与来源',
        },
        {
            'id': 'case079', 'kind': 'application', 'kind_label': '方法应用', 'title': '079 原生单案示范',
            'value': c['revision'].replace('research-', ''), 'unit': '研究版本',
            'status': '质量未评', 'description': '6000HP电动压裂泵，事实、AI分析和补证边界分层保存。',
            'next': '补专利清单、原始试验记录、成本依据和项目方确认。',
            'relation': f"{c['project_id']}形成{c['revision']}，把来源核读转为可继续应用的项目档案。",
            'boundary': '未评分、未专家审核；三种等效台数与不同成本口径不合并。',
            'evidence': '/research-079/2019-s19/publish-result.json', 'evidence_label': '查看079单案发布结果',
            'case_metrics': [('记录', c['records']), ('事实字段', c['known_fact_cells']), ('AI分析', c['ai_items'])],
        },
    ]


def render_knowledge_assets(data):
    assets = knowledge_assets(data)
    cards = []
    for asset in assets:
        meter = ''
        if 'meter' in asset:
            meter = f'<div class="asset-meter" role="img" aria-label="原生研究覆盖率 {asset["meter"]}%"><i style="width:{asset["meter"]}%"></i></div>'
        case_metrics = ''
        if 'case_metrics' in asset:
            case_metrics = '<div class="asset-case-metrics">' + ''.join(f'<span>{e(label)} <strong>{e(value)}</strong></span>' for label, value in asset['case_metrics']) + '</div>'
        cards.append(f'''<button class="asset-card" type="button" data-kind="{asset['kind']}" data-asset="{asset['id']}" aria-haspopup="dialog" aria-controls="asset-detail" aria-expanded="false"><span class="asset-card-top"><span class="asset-kind">{e(asset['kind_label'])}</span><span class="asset-status">{e(asset['status'])}</span></span><h3>{e(asset['title'])}</h3><span class="asset-value">{e(asset['value'])} <span class="asset-unit">{e(asset['unit'])}</span></span>{meter}{case_metrics}<p>{e(asset['description'])}</p><span class="asset-card-foot"><span>{e(asset['next'])}</span><span class="asset-open-label">详情</span></span></button>''')
    serialized = json.dumps({asset['id']: asset for asset in assets}, ensure_ascii=False).replace('<', '\\u003c')
    return f'''<section class="report-section" data-assets><h2>数据资产进展</h2><p class="report-section-intro">从项目目录到来源、研究版和方法应用，八类资产共享同一份数据快照。选择卡片可查看关系、下一步与证据边界。</p><div class="asset-flow" aria-label="知识资产关系"><div><strong>{data['product']['index_projects']}</strong><span>项目目录</span></div><div><strong>{data['research']['full_sources']} / {data['research']['patents_sources']}</strong><span>full / patents 来源</span></div><div><strong>{data['research']['native_projects']}</strong><span>原生研究版</span></div><div><strong>{data['product']['method_count']}</strong><span>方法档案承接应用</span></div></div><div class="asset-toolbar"><div class="asset-filters" role="group" aria-label="筛选知识资产"><button type="button" data-asset-filter="all" aria-pressed="true">全部</button><button type="button" data-asset-filter="archive" aria-pressed="false">项目档案</button><button type="button" data-asset-filter="sources" aria-pressed="false">来源素材</button><button type="button" data-asset-filter="application" aria-pressed="false">方法应用</button></div><p class="asset-count" id="asset-count" aria-live="polite">显示 8 / 8 项资产</p></div><div class="asset-grid">{''.join(cards)}</div><script type="application/json" id="asset-data">{serialized}</script><dialog class="asset-detail" id="asset-detail" aria-labelledby="asset-detail-title" aria-describedby="asset-detail-summary"><div class="asset-detail-head"><div><span class="asset-kind" id="asset-detail-kind"></span><h2 id="asset-detail-title"></h2></div><button class="gd-button gd-button-secondary" id="asset-detail-close" type="button">关闭</button></div><div class="asset-detail-value" id="asset-detail-value"></div><p id="asset-detail-summary"></p><dl><dt>资产关系</dt><dd id="asset-detail-relation"></dd><dt>当前状态</dt><dd id="asset-detail-status"></dd><dt>下一步</dt><dd id="asset-detail-next"></dd><dt>证据边界</dt><dd id="asset-detail-boundary"></dd></dl><a id="asset-detail-evidence" href="/reports/项目进展数据-2026-11-04.json">查看可复核数据</a></dialog></section>'''


def main():
    data = json.loads((OUT / '项目进展数据-2026-11-04.json').read_text())
    r = data['research']
    p = data['product']
    c = data['case_079']
    native_percent = round(r['native_projects'] / p['index_projects'] * 100, 1)
    full_fix = r['full_batch_status'].get('needs_correction', 0)
    patents_fix = r['patents_batch_status'].get('needs_correction', 0)
    full_pass = r['full_batch_status'].get('mechanical_pass_pending_content_review', 0)
    patents_pass = r['patents_batch_status'].get('mechanical_pass_pending_content_review', 0)
    queue_max = max(r['queue_counts'].values())
    queue_rows = ''.join(f'<div class="report-queue"><b>{key[0]}</b><span>{label}</span><div class="report-meter"><i style="width:{count / queue_max * 100:.1f}%"></i></div><small>{count}</small></div>' for key, label, count in [
        ('A', '无标准批、无原生版', r['queue_counts']['A_no_standard_no_native']),
        ('B', '有标准批、无原生版', r['queue_counts']['B_standard_no_native']),
        ('C', '有标准批、有原生版', r['queue_counts']['C_standard_with_native']),
        ('D', '无标准批、有原生版', r['queue_counts']['D_no_standard_with_native']),
    ])
    page = f'''<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>项目进展汇报 · 好设计</title>{links()}<style>{CSS}{ASSET_CSS}</style></head><body>{navigation('projects')}<main class="report-shell" id="main">
<section class="report-hero"><div><span class="gd-kicker">GOODDESIGN · 项目进展</span><h1>从项目展示，走向可追溯的创新底座。</h1><p class="gd-lead">真实项目档案数据库、设计创新引擎与企业研究应用，正在形成同一套工作系统。</p><p class="report-date">汇报日期：{data['date']}<br>数据快照：{data['snapshot_at']}</p><button class="gd-button" id="report-print" type="button">打印 / 保存 PDF</button></div><div class="report-kpis"><div class="report-kpi"><strong>560</strong><span>项目总数</span><small>目录与索引完整</small></div><div class="report-kpi"><strong>{r['native_projects']}</strong><span>原生研究版</span><small>不是全库深研完成</small></div><div class="report-kpi"><strong>{r['full_sources']} / {r['patents_sources']}</strong><span>full / patents 来源条目</span><small>按JSONL实际条目统计</small></div><div class="report-kpi"><strong>{p['built_html_pages']}</strong><span>构建页面</span><small>本地预览，未部署生产</small></div></div></section>
<section class="report-summary"><div class="report-panel"><h2>管理层摘要</h2><p>好设计正在从“项目展示网站”升级为“真实项目档案数据库 + 设计创新引擎 + 企业研究应用”。本轮同时推进统一设计系统、可追溯研究版本和560个项目的数据资产化。</p><p><strong>产品骨架和本地体验已基本成形，深研仍处在分层建设阶段。</strong> 560个项目目录齐全，不等于560个真深研完成。生产站点尚未部署本轮更新，专家审核和工程验证未完成。</p></div><div class="report-panel"><h2>原生研究覆盖</h2><div class="report-coverage"><strong>{native_percent}%</strong><span>{r['native_projects']} / {p['index_projects']} 项目</span></div><div class="report-meter"><i style="width:{native_percent}%"></i></div><p class="report-note">这是原生研究版覆盖，不是研究完整度或质量分。另有 {p['index_projects'] - r['native_projects']} 个项目尚未生成原生研究版。</p></div></section>
<section class="report-section"><h2>项目当前架构</h2><div class="report-architecture"><div class="report-architecture-row"><strong>项目档案数据库</strong><span>560项目索引、原子字段、来源块、研究版本、导读评估、素材总表</span><p>查找项目、核对原文、追踪证据和缺口</p></div><div class="report-architecture-row"><strong>设计创新引擎</strong><span>64个方法档案、方法阅读、MCP只读工具与配置中心</span><p>提供分析路径和可复用调用方式</p></div><div class="report-architecture-row"><strong>应用能力</strong><span>需求研究、企业创新工作台、好设计馆、动态案例、小好Copilot</span><p>把项目与方法用于研究、展示和企业问题</p></div><div class="report-architecture-row"><strong>长期设计系统</strong><span>造物云V2.3底座 + GoodDesign UI组件、中文品牌与IP</span><p>统一页面、导航、底部、状态和交互品质</p></div></div></section>
<section class="report-section"><h2>产品与设计系统更新</h2><div class="report-updates"><div class="report-update"><strong>069-072 · 长期设计基础</strong><p>确立GoodDesign UI，完成全站页面迁移、统一导航/底部、GoodDesign品牌和小好IP。</p></div><div class="report-update"><strong>073-078 · 真实应用组件</strong><p>奖项图标、需求研究、数据可视化、企业创新工作台、MCP接入中心与小好角色。</p></div><div class="report-update"><strong>079 · 原生单案示范</strong><p>6000HP电动压裂泵形成{c['revision']}，{c['records']}条记录、{c['known_fact_cells']}个事实字段、{c['ai_items']}条AI分析。</p></div><div class="report-update"><strong>080-082 · 体验与执行过程</strong><p>首页精修、右下角Copilot、Deep Research式动态案例。</p></div><div class="report-update"><strong>083-087 · 品牌与展馆品质</strong><p>恢复展馆图片、中文主导Logo、清晰Copilot背景、统一顶底栏、石墨色首屏。</p></div><div class="report-update"><strong>真实交互边界</strong><p>动态案例为0次模型调用的脚本演示，小好只提供真实导览，不冒充模型能力。</p></div></div></section>
{render_knowledge_assets(data)}
<section class="report-section"><h2>全量深研分层队列</h2><p class="report-section-intro">下一轮按缺口推进，而不是把560个项目机械地再跑一遍。</p><div class="report-queues">{queue_rows}</div></section>
<section class="report-section"><h2>质量现状与必须正视的问题</h2><div class="report-issues"><div class="report-issue report-issue--warn"><strong>批次结构需要修正</strong><p>full有{full_fix}批、patents有{patents_fix}批需要修正，主要是越界路径和非标准文件角色。当前机械通过为full {full_pass}/467、patents {patents_pass}/467。</p></div><div class="report-issue"><strong>旧底稿证据需要重绑</strong><p><code>2025-00</code>有{r['evidence_issues']}项异常，主要来自旧版只有<code>source_ids</code>，不能直接复制成新版已核验字段。</p></div><div class="report-issue"><strong>专利与图片仍有缺口</strong><p>专利多数仍是lead，CNIPA登录墙不能绕过；图片版权未知保留，不能虚构应用、客户或授权。</p></div><div class="report-issue"><strong>上线与研究审核是两回事</strong><p>本轮只有本地预览，没有生产部署；动态展示和机械校验都不能代替领域专家或项目方确认。</p></div></div></section>
<section class="report-section"><h2>下一阶段计划</h2><div class="report-steps"><div class="report-step"><b>P0</b><div><h3>先修数据可信度</h3><p>修复full {full_fix}批、patents {patents_fix}批路径和角色；重绑2025-00证据；继续补2021-c30可定位专利公开文本。</p></div></div><div class="report-step"><b>P1</b><div><h3>按队列推进全量深研</h3><p>A队列60项完整检索，B队列397项存量核读，C队列70项深化，D队列33项证据绑定。</p></div></div><div class="report-step"><b>P2</b><div><h3>把研究成果接入真实应用</h3><p>以079为标准，把可追溯事实转成机制解释、方法参考和企业研究输入，不生成无依据的迁移结论。</p></div></div><div class="report-step"><b>P3</b><div><h3>按页面族发布</h3><p>先准备备份、回滚、权限和线上回归，再逐步发布首页、档案、方法库、展馆和需求研究，不直接全站覆盖。</p></div></div></div></section>
<section class="report-section"><div class="report-quote">好设计已经完成从项目展示到数据底座、设计系统和研究应用的骨架搭建；下一阶段不再追求页面和文件数量，而是把每个项目的证据、工程验证和真实应用做深。</div></section>
<section class="report-section"><h2>可复核入口</h2><div class="report-evidence"><a href="/research-088/audit-summary.json">全量质量审计</a><a href="/research-088/queues.json">560个分层队列</a><a href="/research-089/material-inventory.csv">560个素材总表</a><a href="/research-079/2019-s19/publish-result.json">079单案结果</a><a href="/reports/项目进展数据-2026-11-04.json">结构化汇报数据</a><a href="http://127.0.0.1:8892/inno/">GoodDesign 首页</a><a href="http://127.0.0.1:8892/inno/museum/">好设计馆</a><a href="http://127.0.0.1:8892/inno/needs-v2/">需求研究</a></div><p class="report-footer-note">本报告不包含私有原件、未公开推荐书或会议内容。质量总分、专家审核与生产发布均保持未完成状态。</p></section>
</main>{footer()}<script>
document.getElementById('report-print').addEventListener('click',()=>window.print());
(()=>{{
  const root=document.querySelector('[data-assets]');
  const cards=[...root.querySelectorAll('.asset-card')];
  const filters=[...root.querySelectorAll('[data-asset-filter]')];
  const count=root.querySelector('#asset-count');
  const dialog=root.querySelector('#asset-detail');
  const details=JSON.parse(root.querySelector('#asset-data').textContent);
  let activeFilter='all';
  let activeCard=null;
  let printFilter='all';
  function applyFilter(kind){{
    activeFilter=kind;
    let visible=0;
    cards.forEach(card=>{{
      const show=kind==='all'||card.dataset.kind===kind;
      card.hidden=!show;
      if(show)visible+=1;
    }});
    filters.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.assetFilter===kind)));
    count.textContent=`显示 ${{visible}} / ${{cards.length}} 项资产`;
  }}
  filters.forEach(button=>button.addEventListener('click',()=>applyFilter(button.dataset.assetFilter)));
  function closeDetail(){{if(dialog.open)dialog.close();}}
  cards.forEach(card=>card.addEventListener('click',()=>{{
    const asset=details[card.dataset.asset];
    activeCard=card;
    cards.forEach(item=>item.setAttribute('aria-expanded',String(item===card)));
    root.querySelector('#asset-detail-kind').textContent=asset.kind_label;
    root.querySelector('#asset-detail-title').textContent=asset.title;
    root.querySelector('#asset-detail-value').textContent=`${{asset.value}} ${{asset.unit}}`;
    root.querySelector('#asset-detail-summary').textContent=asset.description;
    root.querySelector('#asset-detail-relation').textContent=asset.relation;
    root.querySelector('#asset-detail-status').textContent=asset.status;
    root.querySelector('#asset-detail-next').textContent=asset.next;
    root.querySelector('#asset-detail-boundary').textContent=asset.boundary;
    const evidence=root.querySelector('#asset-detail-evidence');
    evidence.href=asset.evidence;
    evidence.textContent=asset.evidence_label;
    dialog.showModal();
  }}));
  root.querySelector('#asset-detail-close').addEventListener('click',closeDetail);
  dialog.addEventListener('click',event=>{{
    if(event.target!==dialog)return;
    const rect=dialog.getBoundingClientRect();
    if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)closeDetail();
  }});
  dialog.addEventListener('close',()=>{{
    cards.forEach(card=>card.setAttribute('aria-expanded','false'));
    if(activeCard)activeCard.focus();
  }});
  window.addEventListener('beforeprint',()=>{{
    printFilter=activeFilter;
    closeDetail();
    applyFilter('all');
  }});
  window.addEventListener('afterprint',()=>applyFilter(printFilter));
}})();
</script></body></html>'''
    (OUT / '项目进展汇报-2026-11-04.html').write_text(page, encoding='utf-8')
    print(json.dumps({'html': str(OUT / '项目进展汇报-2026-11-04.html'), 'native_projects': r['native_projects'], 'native_percent': native_percent, 'full_regression_tests': data['verification']['full_regression_tests']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
