# coding: utf-8
"""100: version-bound, evidence-readable project knowledge graphs."""
import argparse
import html
import json
import math
from pathlib import Path

import project_ownership as own
import project_pipeline as pp
import research_workflow as rw
from archive_presentation import fact_cells, complete_evidence
from steward_dossier_ui import DISPLAY_MODULE_ENTITIES, UNIT_LABELS

ROOT = pp.ROOT
LIB = pp.LIB
OUT = ROOT / 'output/research-100/previews/graphs'
MODULE_NAMES = pp.MODULES


def source_title(source):
    title = source.get('title') or source['id']
    for suffix in ('.pdf', '.html', '.md', '.txt'):
        if title.lower().endswith(suffix):
            return title[:-len(suffix)]
    return title


def display_value(value):
    if isinstance(value, list):
        return '、'.join(display_value(item) for item in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    text = str(value)
    return UNIT_LABELS.get(text, text).replace('%', '％')


def graph_data(lib, pid):
    p = pp.project(lib, pid)
    state = pp.state(p)
    revision = 'research-%06d' % rw.current(p)['revision']
    folder, _ = rw.check_version(p, revision)
    data = rw.dataset(p, revision=revision)
    sources = own.select(p, state['sources'])
    dataset_sha256 = pp.sha((folder / '档案.json').read_bytes())
    short_name = '嫦娥钻取采样' if pid == '2025-00' else state['project']['name']
    nodes = [{'id': 'project', 'type': 'project', 'label': short_name, 'x': 600, 'y': 380}]
    edges = []
    modules = []
    record_nodes = []
    source_nodes = []
    traceable_total = 0
    fact_total = 0
    platform_metadata = 0
    platform_analysis = 0
    for index, (name, entities) in enumerate(zip(MODULE_NAMES, DISPLAY_MODULE_ENTITIES), 1):
        records = [r for r in data['records'] if r['entity'] in entities]
        angle = -math.pi / 2 + (index - 1) * math.pi / 4
        mx, my = 600 + 230 * math.cos(angle), 380 + 230 * math.sin(angle)
        facts = sum(len(fact_cells(r)) for r in records)
        traced = sum(1 for r in records for _, c in fact_cells(r) if complete_evidence(c, sources))
        analysis = sum(1 for r in records for c in r.get('cells', {}).values()
                       if c.get('value_state') == 'known' and c.get('value') is not None
                       and c.get('content_nature') in ('platform_metadata', 'platform_analysis'))
        platform_metadata += sum(1 for r in records for c in r.get('cells', {}).values()
                                 if c.get('value_state') == 'known' and c.get('value') is not None
                                 and c.get('content_nature') == 'platform_metadata')
        platform_analysis += sum(1 for r in records for c in r.get('cells', {}).values()
                                 if c.get('value_state') == 'known' and c.get('value') is not None
                                 and c.get('content_nature') == 'platform_analysis')
        fact_total += facts
        traceable_total += traced
        module_id = f'module-{index}'
        modules.append({'id': module_id, 'name': name, 'facts': facts, 'traceable': traced, 'analysis': analysis})
        nodes.append({'id': module_id, 'type': 'module', 'label': name, 'x': mx, 'y': my,
                      'facts': facts, 'traceable': traced, 'analysis': analysis})
        edges.append({'source': 'project', 'target': module_id, 'relation': 'contains'})
        count = len(records)
        for position, record in enumerate(records):
            spread = 0 if count == 1 else (position / (count - 1) - 0.5) * 1.25
            x = mx + 125 * math.cos(angle + spread)
            y = my + 125 * math.sin(angle + spread)
            record_facts = len(fact_cells(record))
            record_traceable = sum(1 for _, c in fact_cells(record) if complete_evidence(c, sources))
            status = 'verified' if record_facts and record_traceable == record_facts else ('partial' if record_traceable else 'missing')
            node = {'id': 'record-' + record['id'], 'record_id': record['id'], 'type': 'record',
                    'entity': record['entity'], 'label': record['title'], 'module': module_id,
                    'x': x, 'y': y, 'facts': record_facts, 'traceable': record_traceable,
                    'evidence_status': status}
            record_nodes.append(node)
            nodes.append(node)
            edges.append({'source': module_id, 'target': node['id'], 'relation': 'contains'})
            for field, cell in record.get('cells', {}).items():
                if cell.get('value_state') != 'known' or cell.get('value') is None:
                    continue
                evidence = cell.get('evidence') or {}
                sid = evidence.get('source_id')
                if sid in sources:
                    edges.append({'source': node['id'], 'target': 'source-' + sid,
                                  'relation': 'evidence', 'field': field})
            for field in ('related_record_ids',):
                related = record.get('cells', {}).get(field, {}).get('value') or []
                for target in related:
                    if target != record['id']:
                        edges.append({'source': node['id'], 'target': 'record-' + target, 'relation': 'related'})
    for sid, source in sorted(sources.items()):
        source_nodes.append({'id': 'source-' + sid, 'source_id': sid, 'type': 'source',
                             'label': source_title(source), 'read_scope': source.get('read_scope') or 'unread'})
    nodes.extend(source_nodes)
    record_ids = {node['id'] for node in nodes}
    edges = [edge for edge in edges if edge['source'] in record_ids and edge['target'] in record_ids]
    summary = {
        'records': len(record_nodes), 'sources': len(source_nodes), 'facts': fact_total,
        'traceable': traceable_total, 'gaps': fact_total - traceable_total,
        'platform_metadata': platform_metadata, 'platform_analysis': platform_analysis,
    }
    return {
        'schema': 'gooddesign-project-graph-1.0',
        'project': {'id': pid, 'name': state['project']['name'], 'research_revision': revision,
                    'dataset_sha256': dataset_sha256},
        'summary': summary,
        'modules': modules,
        'nodes': nodes,
        'edges': edges,
    }


def detail_record(data, record_id):
    p = pp.project(LIB, data['project']['id'])
    state = pp.state(p)
    sources = own.select(p, state['sources'])
    record = next(r for r in rw.dataset(p, revision=data['project']['research_revision'])['records']
                  if r['id'] == record_id)
    fields = []
    dictionary = rw.schema().get(record['entity'], {})
    for field, cell in record.get('cells', {}).items():
        if cell.get('value_state') != 'known' or cell.get('value') is None:
            continue
        evidence = cell.get('evidence') or {}
        fields.append({'field': dictionary.get(field, {}).get('label', field), 'value': display_value(cell['value']),
                       'content_nature': cell.get('content_nature'),
                       'source_id': evidence.get('source_id'),
                       'quote': evidence.get('quote') or '',
                       'locator': cell.get('locator') or evidence.get('locator') or ''})
    return record, fields, sources


CSS = '''
:root{--paper:#F4F5F8;--ink:#16181F;--muted:#5E6474;--line:#DDE0E9;--accent:#5A4FE6;--pale:#EEEDFC;--surface:#FFF;--soft:#F8F9FC;--warn:#83550E}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.75 -apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif}a{color:var(--accent);text-underline-offset:4px}button,input,select{font:inherit;color:inherit}button{cursor:pointer}.wrap{max-width:1440px;margin:auto;padding:30px 32px 60px}.top{display:flex;justify-content:space-between;gap:24px;align-items:flex-start}.top h1{font-size:32px;line-height:1.45;margin:8px 0 12px}.top p{color:var(--muted);max-width:780px}.back{white-space:nowrap}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:26px 0}.metric{padding:18px 20px;border:1px solid var(--line);border-radius:16px;background:var(--surface)}.metric b{display:block;font-size:26px}.metric span{color:var(--muted);font-size:12px}.filters{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}.filters label{display:grid;gap:5px;color:var(--muted);font-size:12px}.filters select,.filters input{min-height:40px;padding:7px 10px;border:1px solid var(--line);border-radius:9px;background:var(--surface)}.filters input{min-width:220px}.filters button{min-height:40px;padding:7px 14px;border:1px solid var(--line);border-radius:9px;background:var(--surface)}.layout{display:grid;grid-template-columns:minmax(0,1fr) 350px;gap:22px}.graph-box{overflow:auto;border:1px solid var(--line);border-radius:18px;background:var(--surface)}.graph-box svg{display:block;width:100%;min-width:800px;height:auto}.graph-node{cursor:pointer;outline:none}.graph-node circle{stroke-width:1.5}.graph-node.project circle{fill:var(--accent);stroke:var(--accent)}.graph-node.module circle{fill:var(--pale);stroke:var(--accent)}.graph-node.record.verified circle{fill:#E4F2E9;stroke:#2B7350}.graph-node.record.partial circle{fill:#FBF3E4;stroke:var(--warn)}.graph-node.record.missing circle{fill:#F3ECE1;stroke:#A56B36}.graph-node.source circle{fill:#EDF0F5;stroke:#6C7590}.graph-node text{pointer-events:none;font-size:12px;fill:var(--ink)}.graph-node.project text{fill:white;font-size:15px;font-weight:600}.graph-node.module text{font-weight:600}.graph-node.selected circle{stroke:var(--accent);stroke-width:4}.graph-edge{stroke:#B9C0D0;stroke-width:1.2;fill:none}.graph-edge.related{stroke-dasharray:5 4}.detail{border:1px solid var(--line);border-radius:18px;background:var(--surface);padding:22px;align-self:start;max-height:760px;overflow:auto}.detail h2{font-size:20px;line-height:1.5;margin:0 0 12px}.detail h3{font-size:15px;margin:22px 0 8px}.detail-meta{color:var(--muted);font-size:12px}.field{padding:12px 0;border-bottom:1px solid var(--line)}.field b{display:block;font-size:12px;color:var(--muted);margin-bottom:4px}.field p{margin:0}.quote{font-size:12px;color:var(--muted);white-space:pre-wrap;margin-top:8px}.badge{display:inline-block;padding:3px 8px;border-radius:999px;background:var(--pale);color:var(--accent);font-size:11px}.legend{display:flex;gap:14px;flex-wrap:wrap;color:var(--muted);font-size:12px;margin:10px 0}.legend span:before{content:'';display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}.legend .v:before{background:#2B7350}.legend .p:before{background:#A56B36}.legend .m:before{background:#6C7590}.hint{color:var(--muted);font-size:12px}.graph-actions{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;border-bottom:1px solid var(--line)}.graph-actions span{font-size:12px;color:var(--muted)}@media(max-width:1000px){.layout{grid-template-columns:1fr}.detail{max-height:none}.summary{grid-template-columns:1fr 1fr}.wrap{padding:22px 20px 44px}.top h1{font-size:26px}}@media(max-width:560px){.summary{grid-template-columns:1fr 1fr}.filters input{min-width:160px}.top{display:block}.back{display:inline-block;margin-top:12px}}@media print{.filters,.graph-actions,.detail{display:none}.layout{display:block}.graph-box svg{min-width:0}.summary{grid-template-columns:repeat(4,1fr)}}
'''


def render_html(data):
    project = data['project']
    summary = data['summary']
    h = lambda value: html.escape(str(value), quote=True)
    nodes = []
    for node in data['nodes']:
        if node['type'] == 'source':
            continue
        label = '' if node['type'] == 'record' else f'<text x="{node["x"]}" y="{node["y"] + 5}" text-anchor="middle">{h(node["label"])}</text>'
        title = html.escape(node['label'], quote=True)
        nodes.append(f'<g class="graph-node {node["type"]} {node.get("evidence_status", "")}" id="node-{h(node["id"])}" data-node-id="{h(node["id"])}" data-module="{h(node.get("module", ""))}" data-status="{h(node.get("evidence_status", ""))}" tabindex="0" role="button" aria-label="查看{title}"><title>{title}</title><circle cx="{node["x"]}" cy="{node["y"]}" r="{18 if node["type"] == "project" else 12 if node["type"] == "module" else 6}"/>{label}</g>')
    edge_by_id = {node['id']: node for node in data['nodes']}
    edge_lines = []
    for edge in data['edges']:
        if edge['relation'] == 'evidence':
            continue
        source, target = edge_by_id[edge['source']], edge_by_id[edge['target']]
        cls = 'graph-edge related' if edge['relation'] == 'related' else 'graph-edge'
        edge_lines.append(f'<line class="{cls}" x1="{source["x"]}" y1="{source["y"]}" x2="{target["x"]}" y2="{target["y"]}"/>')
    graph_json = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    metrics = ''.join(f'<div class="metric"><b>{h(value)}</b><span>{h(label)}</span></div>'
                      for value, label in ((summary['records'], '项目记录'), (summary['facts'], '项目事实'),
                                           (summary['traceable'], '可追溯事实'), (summary['gaps'], '证据缺口')))
    body = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>{h(project['name'])} · 知识图谱</title><style>{CSS}</style></head><body><main class="wrap"><div class="top"><div><div class="hint">GoodDesign · 项目知识图谱</div><h1>{h(project['name'])}</h1><p>从项目到主题、记录与来源，按当前档案版本查看关系。节点与证据状态由同一份真源生成，缺口不做隐藏。</p></div><a class="back" href="{h(project['id'])}.html">返回项目档案</a></div><div class="summary">{metrics}</div><div class="filters"><label>主题<select id="module-filter"><option value="">全部主题</option>{''.join(f'<option value="{h(m["id"])}">{h(m["name"])}</option>' for m in data['modules'])}</select></label><label>证据状态<select id="status-filter"><option value="">全部状态</option><option value="verified">证据完整</option><option value="partial">部分可追溯</option><option value="missing">待补证据</option></select></label><label>查找记录<input id="graph-search" type="search" placeholder="输入名称或编号"></label><button id="graph-reset" type="button">重置</button><span id="visible-count" role="status"></span></div><div class="layout"><section class="graph-box"><div class="graph-actions"><span>项目 → 主题 → 记录；点选记录查看来源</span><div class="legend"><span class="v">证据完整</span><span class="p">部分可追溯</span><span class="m">待补证据</span></div></div><svg viewBox="0 0 1200 760" role="img" aria-label="项目知识图谱">{''.join(edge_lines)}{''.join(nodes)}</svg></section><aside class="detail" id="record-detail" aria-live="polite"><h2>选择一个记录</h2><p class="hint">点击图中的记录节点，查看项目事实、平台解读、来源与逐字证据。全部节点已包含在图谱数据中，筛选只改变显示，不改变数据。</p></aside></div><details><summary>图谱数据与版本</summary><p class="hint">当前研究版本：{h(project['research_revision'])}。全部 {summary['records']} 条记录、{summary['sources']} 个来源、{summary['facts']} 条项目事实均来自当前档案；未核验内容不自动升格为事实。</p><a href="{h(project['id'])}.json">下载图谱 JSON</a></details></main><script id="graph-data" type="application/json">{graph_json}</script><script>'''
    script = '''
const data=JSON.parse(document.getElementById('graph-data').textContent);const detail=document.getElementById('record-detail');const nodes=[...document.querySelectorAll('.graph-node')];const moduleFilter=document.getElementById('module-filter');const statusFilter=document.getElementById('status-filter');const search=document.getElementById('graph-search');
function text(tag,value,cls){const el=document.createElement(tag);if(cls)el.className=cls;el.textContent=value;return el}
function selectNode(id){const node=data.nodes.find(x=>x.id===id);if(!node)return;nodes.forEach(el=>el.classList.toggle('selected',el.dataset.nodeId===id));detail.replaceChildren();const title=document.createElement('h2');title.textContent=node.label;detail.append(title);const moduleName=node.module?data.modules.find(x=>x.id===node.module).name:node.type;const meta=text('p',`主题：${moduleName} · 项目事实 ${node.facts||0} 条 · 可追溯 ${node.traceable||0} 条`,'detail-meta');detail.append(meta);const status=text('p',node.evidence_status==='verified'?'证据完整':node.evidence_status==='partial'?'部分可追溯':'待补证据','badge');detail.append(status);const fields=data.details&&data.details[id]||[];fields.forEach(field=>{const box=document.createElement('div');box.className='field';box.append(text('b',field.field),text('p',field.value));if(field.quote)box.append(text('p',field.quote,'quote'));if(field.locator)box.append(text('p',field.locator,'detail-meta'));detail.append(box)});if(!fields.length)detail.append(text('p','这条记录没有已登记字段。','hint'))}
function applyFilters(){const module=moduleFilter.value,status=statusFilter.value,query=search.value.trim().toLowerCase();let visible=0;nodes.forEach(el=>{const node=data.nodes.find(x=>x.id===el.dataset.nodeId);const show=(!module||node.module===module||node.type==='project')&&(!status||node.evidence_status===status||node.type!=='record')&&(!query||node.label.toLowerCase().includes(query)||node.id.toLowerCase().includes(query));el.style.display=show?'':'none';if(show&&node.type==='record')visible++});document.getElementById('visible-count').textContent=`显示 ${visible} 条记录`}
nodes.forEach(el=>{el.addEventListener('click',()=>selectNode(el.dataset.nodeId));el.addEventListener('keydown',event=>{if(['Enter',' '].includes(event.key)){event.preventDefault();selectNode(el.dataset.nodeId)}})});[moduleFilter,statusFilter,search].forEach(el=>el.addEventListener('input',applyFilters));document.getElementById('graph-reset').addEventListener('click',()=>{moduleFilter.value='';statusFilter.value='';search.value='';applyFilters();detail.replaceChildren()});applyFilters();
</script></body></html>'''
    return body + script


def build_project(lib, pid, out_dir=OUT):
    data = graph_data(lib, pid)
    out_dir.mkdir(parents=True, exist_ok=True)
    details = {}
    for node in data['nodes']:
        if node['type'] != 'record':
            continue
        record, fields, sources = detail_record(data, node['record_id'])
        details[node['id']] = fields
    data['details'] = details
    (out_dir / f'{pid}.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    (out_dir / f'{pid}.html').write_text(render_html(data))
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('project_ids', nargs='+')
    args = parser.parse_args()
    for project_id in args.project_ids:
        result = build_project(LIB, project_id)
        print(project_id, result['summary'])
