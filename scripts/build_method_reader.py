# -*- coding: utf-8 -*-
"""ML-011 presentation projection. Never writes to the frozen library."""
import ast
import html
import json
import re
from method_library_catalog import catalog, read
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'04-知识库/创新方法库/深度方法库-v0.1.0'
OUT=ROOT/'extensions/method-reader'
E=lambda x: html.escape(str(x),quote=True)
EXEC={'R48','R14','R17','R36','R44','R42'}
LABELS={'identity':'方法从哪里来','problem':'解决什么问题','principle':'为什么有效','applicability':'什么时候适合用','interpretation':'如何理解结果','example':'跟着例子走一遍（教学示例）','pitfalls':'容易走偏的地方','validation':'怎样检查与验证','adaptation':'平台做了哪些适配','gaps':'还缺哪些证据'}
CATS={m['category'][0]:m['category'][1:] for m in json.loads((LIB/'目录.json').read_text())['methods']}

from method_reader_visuals import dependency_svg
from method_supplement_visuals import icon

def paras(s):return ''.join('<p>'+E(p)+'</p>' for p in str(s).split('\n') if p.strip())
from method_reader_markdown import document

def page(title,body):
    from inno_site_chrome import navigation,footer
    return '<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><link rel="icon" href="data:,"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+E(title)+' · 好设计</title><link rel="stylesheet" href="/vendor/tokens.css"><link rel="stylesheet" href="/vendor/design-system.css"><link rel="stylesheet" href="/inno/portal/portal.css"><link rel="stylesheet" href="/inno/portal/system.css"><link rel="stylesheet" href="/library/reader.css"></head><body class="inno-method-site">'+navigation('methods','main')+body+footer()+'<script src="/library/reader.js"></script></body></html>'

def block(title,text):return '<section><h2>'+E(title)+'</h2>'+paras(text)+'</section>'
def code(text):return '<div class="code"><button class="zw-btn copy" type="button">复制</button><pre tabindex="0"><code>'+E(text)+'</code></pre><span role="status" aria-live="polite"></span></div>'

def detail(d,records):
    rid=d['research_id'];sec=d['sections']
    body=f'<main id="main" class="reader"><a href="../index.html">← 全部方法</a><div class="hero cat-{d["category"][0]}"><img class="method-icon" src="../icons/{rid}.svg" alt=""><p class="eyebrow">{E(d["category"])}</p><h1>{E(d["name"])}</h1><p class="english">{E(d["english_name"])}</p><p class="lead">{E(d["summary"])}</p><p class="boundary">研究稿 · {"闻邦椿谱系专题" if rid.startswith("WB") else "创新方法"} · 尚未独立专家审核或工程验证</p></div>'
    if d.get('source_readiness')=='limited_excerpt_only':body+='<p class="decision"><b>原典补证中：</b>当前仅有作者目录及论文检索摘录，直接全文访问失败；请按有限核读研究稿使用。</p>'
    if d.get('integration_rationale'):body+='<div class="decision"><b>本轮增补 · 为什么加入</b>'+paras(d['integration_rationale'])+'<p>内容可读，尚无执行契约。</p></div>'
    if rid=='R35':
        body+='<aside class="notice"><h2>先区分原典与本页示例</h2><p>Sigmund原论文第2页式(1)采用体积分数等式 V/V₀=f。本档教学模型写为体积上限约束，是平台的一般化适配，不能直接当作原代码逐式复现。比较结果前，先固定采用哪一种约束、载荷与边界条件。</p><a href="https://www.topopt.mek.dtu.dk/-/media/subsites/topopt/apps/dokumenter-og-filer-til-apps/matlab-1-.pdf" target="_blank" rel="noopener noreferrer">核对原论文</a></aside>'
    body+='<p><a class="zw-btn zw-btn--primary" href="/inno/needs/?method='+E(rid)+'">带着这个方法研究问题 →</a></p>'
    body+='<nav class="contents" aria-label="文章目录">'+''.join(f'<a href="#{key}">{name}</a>' for key,name in [('understand','理解方法'),('structure','结构图'),('operate','怎么使用'),('example','例子与边界'),('relations','关联方法'),('sources','原始依据'),('connect','调用与档案')])+'</nav>'
    body+='<section id="understand"><h2>先理解这个方法</h2>'+''.join('<h3>'+LABELS[k]+'</h3>'+paras(sec[k]) for k in ['problem','principle','applicability'])+'</section>'
    body+='<section id="structure"><h2>一张图看懂结构</h2><p>依据本档案的输入、步骤与产物生成；卡片按档案顺序排列，具体依赖以“承接”标注为准，不强制串行。未表示实际运行已完成。</p><div class="io-grid"><article><h3>开始前准备</h3>'+''.join('<p>'+E(x['label'])+(' · 必需' if x.get('required') else ' · 可补充')+'</p><small>'+E(x.get('description',''))+'</small>' for x in d['inputs'])+'</article><article><h3>结束时带走</h3>'+''.join('<p>'+E(x['label'])+'</p>' for x in d['outputs'])+'</article></div><ol class="flow">'
    stepmap={s['step_id']:s['title'] for s in d['steps']}
    for i,s in enumerate(d['steps'],1):
        deps='、'.join(stepmap.get(x,x) for x in s.get('depends_on',[]))
        body+=f'<li><a href="#{E(s["step_id"])}"><span>{i:02}</span><strong>{E(s["title"])}</strong></a><p>{E(s["output_description"])}</p>'+('<small>承接：'+E(deps)+'</small>' if deps else '<small>起点或独立准备</small>')+'</li>'
    body+='</ol><div class="dependency-map">'+dependency_svg(d)+'</div></section><section id="operate"><h2>一步一步怎么做</h2>'
    for i,s in enumerate(d['steps'],1):
        body+=f'<article class="step" id="{E(s["step_id"])}"><span class="number">{i:02}</span><h3>{E(s["title"])}</h3>'+paras(s['operation'])+'<div class="decision"><b>到这里，先判断</b>'+paras(s['decision'])+'</div><p><b>本步产物：</b>'+E(s['output_description'])+'</p><p><b>检查：</b>'+E('；'.join(s['checks']))+'</p><p class="stop"><b>何时返回或停下：</b>'+E(s['stop_condition'])+'</p></article>'
    body+='<h3>如何理解结果</h3>'+paras(sec['interpretation'])+'</section><section id="example"><h2>例子与使用边界</h2>'+''.join('<h3>'+LABELS[k]+'</h3>'+paras(sec[k]) for k in ['example','pitfalls','validation'])+'<h3>用这些情境检查你的理解</h3><p>以下为检查设想，未表示真实试验已经执行。</p><div class="relation-grid">'+''.join('<article class="relation"><h3>'+E(x['scenario'])+'</h3><p>'+E(x['expected'])+'</p></article>' for x in d.get('evaluations',[]))+'</div></section>'
    from method_reader_cases import teaching_case
    body+=teaching_case(rid)
    body+='<section id="relations"><h2>可以接着用哪些方法</h2><div class="relation-grid">'
    words={'requires':'前置准备','precedes':'下一步','parallel':'配合使用','complements':'配合使用','alternative':'替代选择'}
    relation_holds={('WB04','WB05'):'这条交接的描述指向深层次设计，但目标页为主辅功能专题，关系意图待核。',('WB06','R39'):'稳健参数与公差设计不等于通用仿真验证，需先明确不确定性或公差输入。',('WB09','R39'):'此目标不代表通用数值求解或仿真验证能力，交接依据待核。',('WB07','R32'):'机构综合可给运动拓扑与几何，不能直接当作结构动态响应。'}
    for r in d.get('relations',[]):
        t=r['target_research_id'];target=records.get(t)
        if (rid,t) in relation_holds:
            body+='<article class="relation"><small>交接关系待核</small><h3>'+E(target['name'] if target else t)+'</h3><p>'+E(relation_holds[(rid,t)])+'</p><p>暂不作为自动交接建议，原档案关系保留供复核。</p></article>'
            continue
        if target:body+=f'<a class="relation" href="{t}.html"><small>{E(words.get(r["relation"],"关联方法"))}</small><h3>{E(target["name"])}</h3><p>{E(r["condition"])}</p></a>'
    body+='</div><h3>平台适配说明</h3>'+paras(sec['adaptation'])+'</section><section id="sources"><h2>原典与依据</h2>'+paras(sec['identity'])
    for s in d['sources']:
        body+='<article class="source" id="source-'+E(s['source_id'])+'"><h3><a target="_blank" rel="noopener noreferrer" href="'+E(s['url'])+'">'+E(s['title'])+' ↗</a></h3><p>'+E(s['publisher'])+'</p><p><b>核读位置：</b>'+E(s['locator'])+'</p><p><b>已读范围：</b>'+E(s['read_scope'])+'</p>'+paras(s['evidence_note'])+'</article>'
    body+='<h3>尚待补证</h3>'+paras(sec['gaps'])+'</section><section id="connect"><h2>调用与档案</h2><p>'+('此方法已有执行契约，仍须检查输入、证据和后续交接。' if rid in EXEC else '此条目目前可检索、阅读；尚无对应的执行契约，不代表可直接自动执行。')+'</p>'+code(json.dumps({'name':'method_supplement_get','arguments':{'method_id':rid}} if d.get('integration_rationale') else {'name':'method_get','arguments':{'method_id':rid,'view':'overview'}},ensure_ascii=False,indent=2))+'<div class="actions"><a class="zw-btn" href="#example">实践档案（教学与验证设想）</a><a class="zw-btn" href="../integration.html">配置方法引擎与MCP</a><a class="zw-btn" href="../contributing.html">方法写入规范</a></div><h3>完整研究档案</h3><p>结构字段和原始资料单独保留，便于复核与开发调用。</p><div class="actions">'
    for file,label in [('方法结构.md','方法结构'),('操作指南.md','操作文档'),('档案.json','原始档案 JSON'),('深度说明.md','深度文档'),('来源核读.md','来源核读')]:body+=f'<a class="zw-btn" href="../档案/{rid}/{E(file)}">{label}</a>'
    return page(d['name'],body+'</div></section></main>')

def build():
    OUT.mkdir(exist_ok=True);(OUT/'methods').mkdir(exist_ok=True);(OUT/'icons').mkdir(exist_ok=True)
    records={m['research_id']:read(m['research_id']) for m in catalog()['methods']}
    for rid,d in records.items():
        (OUT/'icons'/f'{rid}.svg').write_text(icon(d));(OUT/'methods'/f'{rid}.html').write_text(detail(d,records))
    body='<main id="main" class="overview"><p class="eyebrow">好设计 · 方法库</p><h1>为真实问题，找到合适的方法</h1><p class="lead">从理解需求、构思原理到验证方案，探索52份方法档案与12份闻邦椿谱系专题，其中4份为本轮增补研究稿。</p><div class="actions"><a href="integration.html">引擎与MCP接入</a><a href="contributing.html">方法写入规范</a></div><label for="method-search">搜索方法</label><input id="method-search" type="search" placeholder="输入问题、方法名称或关键词"><nav class="categories" aria-label="方法分类"><button class="zw-btn" data-category="" aria-pressed="true">全部</button>'+''.join(f'<button class="zw-btn" data-category="{k}" aria-pressed="false"><b>{k}</b> {E(v)}</button>' for k,v in sorted(CATS.items()))+'</nav><p id="search-status" role="status"></p><div class="cards">'
    for rid,d in records.items():
        search=' '.join([rid,d['method_id'],d['name'],d['english_name'],d['summary']]+d.get('search_terms',[])+d.get('aliases',[])).lower()
        body+=f'<a class="method-card cat-{d["category"][0]}" data-cat="{d["category"][0]}" data-search="{E(search)}" href="methods/{rid}.html"><img src="icons/{rid}.svg" alt=""><small>{E(d["category"])}</small><h2>{E(d["name"])}</h2><p>{E(d["summary"])}</p><span>{"谱系专题" if rid.startswith("WB") else "方法"} · 阅读 →</span></a>'
    (OUT/'index.html').write_text(page('方法库',body+'</div><p id="empty" hidden>没有找到匹配方法，可以换个关键词或选择其他分类。</p></main>'))
    integration(records)
    print('Built',len(records),'readers and icons')

def integration(records):
    conf={'mcpServers':{'gooddesign-methods':{'command':str(ROOT/'.runtime/pipeline/bin/python'),'args':[str(ROOT/'scripts/method_engine_library_mcp.py')],'env':{'METHOD_ENGINE_DB':str(ROOT/'output/method-workbench-private/engine.sqlite')}}}}
    tools=[]
    for name in ['method_engine_mcp.py','method_engine_incremental_mcp.py','method_engine_library_mcp.py']:
        tree=ast.parse((ROOT/'scripts'/name).read_text())
        tools += [n.name for n in tree.body if isinstance(n,ast.FunctionDef) and n.name.startswith('method_')]
    body='<main id="main" class="reader"><h1>方法引擎与 MCP</h1><p class="lead">Agent读取方法、检查交接、记录研究产物；模型生成与规则检查分开调用。</p><h2>复制配置，接到你的Agent</h2><p>下面是本机stdio配置，需MCP客户端支持该配置格式。其他电脑请替换绝对路径，并安装项目固定运行环境；这不是公开远程服务，也不会替你写入全局设置。</p>'+code(json.dumps(conf,ensure_ascii=False,indent=2))+'<p>上述可选内容聚合入口共22个工具：保留原20个工具，另加2个增补方法只读工具。原method_engine_mcp.py仍18个，method_engine_incremental_mcp.py仍20个。现有模型调用依赖本机已配置的Codex服务与额度，不包含在纯规则检查内。</p><h2>一次调用示例</h2><p>以下是MCP tools/call的params结构；完整JSON-RPC请求需由客户端添加id/jsonrpc/method。</p>'+code(json.dumps({'name':'method_get','arguments':{'method_id':'R17','view':'overview'}},ensure_ascii=False,indent=2))+'<h2>读取本轮增补方法</h2>'+code(json.dumps({'name':'method_supplement_get','arguments':{'method_id':'R49'}},ensure_ascii=False,indent=2))+'<p>R49—R52使用method_supplement_search/get检索和阅读。原method_search/get及规则规划器仍读取冻结60份档案；选择增补方法不自动建立执行节点。</p><h2>从需求到验证的参考链</h2><ol class="flow">'+''.join('<li><a href="methods/'+rid+'.html">'+E(records[rid]['name'])+'</a></li>' for rid in ['R48','R14','R17','R36','R44','R42'])+'</ol><p>只有这六项已有当前执行契约。参考链不是所有项目的固定答案，其他58份内容档案不能自动当作已接通的执行算法。</p><h2>工具清单</h2><ul>'+''.join('<li><code>'+x+'</code></li>' for x in tools)+'</ul><h2>调用边界</h2><p>semantic_match、propose_artifact、review_artifact及两个增量生成工具会调用真实模型、消耗额度；propose默认允许一次修复，需单次调用可传max_repairs: 0。生成结果仍是草稿；提交要提供运行版本和幂等键，通过校验也不等于专家审核或工程验证。案例证据归一化不认证原文真实性。</p><p>逐步保存输入版本、证据位置、未知事项和审查记录。输入不足或硬约束冲突应停止或返回；未知不得自动判定为通过。工作台页面的完整调用记录仍在“探索与验证”。</p></main>'
    contract_path=ROOT/'output/method-reader-review/mcp-standard/tool-contracts-v1.json'
    if contract_path.exists():
        contracts=json.loads(contract_path.read_text())
        kinds={'model_spend_and_audit':'模型调用：消耗额度并保留审计','persistent_write':'持久写入','read_or_rule':'读取或规则检查'}
        technical='<section id="tool-contracts"><h2>工具参数与调用类型</h2><p>以下为独立SDK实测的原增量20工具接口快照；新22工具入口额外两只读增补工具以实际tools/list为准。调用前检查当前Schema，不把annotations当权限。</p>'
        for t in contracts:
            technical+='<details class="technical-detail"><summary>'+E(t['name'])+' · '+E(kinds.get(t['category'],t['category']))+'</summary><p>必填：'+E('、'.join(t['required'])or'无')+'</p>'+code(json.dumps(t['inputSchema'],ensure_ascii=False,indent=2))+'</details>'
        body=body.replace('</main>',technical+'</section></main>')
    (OUT/'integration.html').write_text(page('引擎与MCP',body))
    template={'schema_version':'method-dossier-1.0','research_id':'待分配稳定ID','method_id':'待分配稳定ID','version':'0.1.0','name':'方法名称','category':'从A—G中选择','summary':'解决什么问题及边界','sections':{k:'待撰写与核读' for k in LABELS},'inputs':[],'steps':[],'outputs':[],'relations':[],'sources':[],'evaluations':[],'change_log':[]}
    body='<main id="main" class="reader"><h1>方法写入规范</h1><p class="lead">先有可追溯的方法内容，再有可执行契约。资料齐全、程序可读和专家认可分别验收。</p><h2>提交前，写清这七件事</h2><ol class="standards">'+''.join('<li><h3>'+a+'</h3><p>'+b+'</p></li>' for a,b in [('身份和分类','沿用稳定research_id、method_id，填写版本；A需求、B功能概念、C发明矛盾、D架构、E工程优化、F评价验证、G全流程管理。闻邦椿谱系专题与独立方法分开标注。'),('原典与平台适配','区分原典主张、平台操作编排、教学假设和真实实践；不得把获奖项目推断成方法应用实例。'),('来源与核读范围','每条来源保留作者/机构、题名、URL、定位、核读范围、日期、支持内容和权利；摘要或目录不能冒称全文。'),('输入、操作和产物','每项输入写必需性和缺失处置；步骤写稳定ID、依赖、动作、判断、产物、检查和停止条件；输出写含义与字段。'),('关系与示例','关系目标必须存在、交接条件明确；示例写假设和未知，真实实践须有案例及证据定位，不捏造效果。'),('版本与发布','在新版本工作区编辑，不覆盖冻结v0.1.0；记录变更原因、来源变化和关联契约影响。先结构验收，再语义复核，专家审核及工程验证另列。'),('执行与负例','新增执行契约前检查Schema、输入缺失、悬空引用、硬约束冲突、未知保留及跨方法交接；模型自评不能替代独立领域专家。')])+'</ol><h2>起草骨架（不是可直接入库的完整档案）</h2>'+code(json.dumps(template,ensure_ascii=False,indent=2))+'<p>骨架中的占位与空数组必须补齐，并通过项目现有结构验收；不要直接发布为完整方法。</p><h2>当前规范原件</h2><div class="actions"><a href="方法库结构规范.md">方法库结构规范</a><a href="入库依据与类型边界.md">入库依据与类型边界</a><a href="引擎接入说明.md">历史内容版接入说明</a></div><p>历史内容版说明反映冻结时状态；当前执行能力以本页关联的MCP接入页和六项契约为准。</p></main>'
    body=body.replace('</main>','<h2>完整字段形状参考</h2><p>以下为现有形态分析档案的真实结构，只用于理解字段；新增方法必须重新分配身份、撰写内容、核读来源并验收，不能复制后改名发布。</p>'+code(json.dumps(records['R17'],ensure_ascii=False,indent=2))+'<h2>质量目标与发布门槛</h2><p>逐法目标80分，评分分开记录内容质量、执行就绪与专家审核。来源、原理、适用边界、操作、示例和验证须有证据；未知保留，图标、页面或测试通过不能替代内容审核。</p><p>未核读不得按0代填，正分必须有具体原文与字段锚点；存在来源缺失、对象错配、虚构实践或关键调用错误时不得标记达标。</p></main>')
    rubric_path=ROOT/'output/method-reader-review/mcp-standard/rubric-v1.json'
    if rubric_path.exists():
        rubric=json.loads(rubric_path.read_text())
        quality='<section id="quality-standard"><h2>逐方法质量评估标准</h2><p>按实际原典、步骤、产物与验证证据评分；待独立校准，不代表专家认证。未核读留空，不能用页面、字段、来源数量换分。</p><table><thead><tr><th>维度</th><th>权重</th><th>核查内容</th></tr></thead><tbody>'+''.join('<tr><td>'+E(x['id'])+'</td><td>'+str(x['weight'])+'</td><td>'+E(x['criterion'])+'</td></tr>' for x in rubric['dimensions'])+'</tbody></table><p>等级：'+E('；'.join(k+'：'+v for k,v in rubric['scale'].items()))+'</p><p>总分达到80且所有硬门槛通过才标达标；内容质量、执行就绪和专家审核分栏记录。</p></section>'
        body=body.replace('</main>',quality+'</main>')
    from method_reader_quality import quality_section
    body=body.replace('</main>',quality_section(records)+'</main>')
    (OUT/'contributing.html').write_text(page('方法写入规范',body))
if __name__=='__main__':build()
