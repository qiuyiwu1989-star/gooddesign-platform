# coding: utf-8
"""040 readable method cards, progressive disclosure, and evidence-linked enterprise report."""
import html,json,urllib.parse
import innovation_methods as im
H=lambda x:html.escape(str(x),quote=True)
def lis(rows):return '<ul>'+''.join('<li>'+H(x)+'</li>'for x in rows)+'</ul>'
def value(v):
 if v is None:return '<span class="muted">待确认</span>'
 if isinstance(v,str):return '<p>'+H(v)+'</p>'
 return '<pre>'+H(json.dumps(v,ensure_ascii=False,indent=2))+'</pre>'
def refs(ids):return '<div class="refs">'+''.join('<button data-evidence="'+H(e)+'">'+H(e)+' · 查看依据</button>'for e in ids)+'</div>'
def render(run):
 rid=run['run_id'];brief=run['enterprise_output'];methods=[im.read_method(m['method_id'],m['version'],'full')['data']for m in run['method_versions']]
 report='<div class="notice">模拟企业需求 · AI研究分析 · 未开展目标设备试验</div><h2>先把“取到样品”和“保留信息”分开验收</h2><p class="lead">'+H(brief['summary'])+'</p><div class="decision"><strong>当前可做：概念探索与试验准备</strong><span>材料、企业基线和验收阈值尚缺，暂不作工程选型。</span></div><h3>三个可讨论的方向</h3>'
 labels={'conditional':'条件性方向 · 未验证','excluded':'与已知约束冲突 · 排除'}
 for i,d in enumerate(brief['directions'],1):
  report+='<article class="direction"><div class="card-heading"><span class="num">0'+str(i)+'</span><div><span class="badge">'+H(labels[d['status']])+'</span><h3>'+H(d['title'])+'</h3></div></div><p>'+H(d['proposal'])+'</p><details><summary>使用前提与新增代价</summary><h4>需要先确认</h4>'+lis(d['assumptions'])+'<h4>需要一起评估</h4>'+lis(d['costs_and_risks'])+('<p>排除条件：'+H(', '.join(d['blocked_by']))+'</p>'if d['blocked_by']else'')+'</details>'+refs(d['evidence_ids'])+'<details><summary>方法与知识的关联</summary>'+value(dict(method_steps=d['method_step_ids'],knowledge_ids=d['source_knowledge_ids'],validation=d['validation_id']))+'</details></article>'
 report+='<h3>先向企业确认这些问题</h3><ol class="questions">'+''.join('<li><span class="badge">'+H(q['priority'])+'</span> '+H(q['question'])+'</li>'for q in brief['questions'])+'</ol><h3>下一步怎样验证</h3>'
 for v in brief['validation_plan']:
  report+='<details class="test"><summary>'+H(v['id']+' · '+v['hypothesis'])+'</summary><dl><dt>怎么比较</dt><dd>'+H(v['comparison'])+'</dd><dt>测量什么</dt><dd>'+H('、'.join(v['measurements']))+'</dd><dt>通过标准</dt><dd>'+H(v['acceptance'])+'</dd><dt>何时停止</dt><dd>'+H(v['stop'])+'</dd><dt>当前结果</dt><dd>未试验</dd></dl></details>'
 report+='<p class="lead">下一决策：'+H(brief['next_decision'])+'</p><details><summary>结论边界</summary>'+lis(brief['limitations'])+'</details>'
 library='<h2>三种方法，三个清楚的任务</h2><p class="muted">每张卡包含来源、平台改编范围、输入、步骤、产物、停止条件和评估要求。</p>'
 for m in methods:
  library+='<article class="method"><div class="card-heading"><span class="badge">'+H(m['version'])+' · 平台操作改编</span><h3>'+H(m['name'])+'</h3></div><p>'+H(m['purpose'])+'</p><div class="columns"><div><h4>输入</h4>'+lis(i['label']+(' · 必需'if i['required']else' · 可补')for i in m['inputs'])+'</div><div><h4>输出</h4>'+lis(o['label']for o in m['outputs'])+'</div></div><details><summary>展开 '+str(len(m['steps']))+' 个执行步骤</summary><ol class="method-steps">'
  for s in m['steps']:library+='<li><h4>'+H(s['title'])+'</h4><p>'+H(s['operation'])+'</p><p class="muted">检查：'+H('；'.join(s['checks']))+'</p><p class="muted">停止／待补：'+H(s['stop_condition'])+'</p></li>'
  library+='</ol></details><details><summary>适用条件、误用与质量检查</summary><h4>不能直接使用的情况</h4>'+lis(m['exclusions'])+'<h4>常见误用</h4>'+lis(m['failure_cases'])+'<h4>完成要求</h4>'+lis(m['quality_checks'])+'</details><details><summary>方法来源与改编说明</summary>'+lis(m['provenance']['adaptations'])+'<ul>'
  for s in m['provenance']['sources']:library+='<li><a href="'+H(s['url'])+'" target="_blank" rel="noopener">'+H(s['publisher']+' · '+s['title'])+' ↗</a><p>'+H(s['basis'])+'</p><small>'+H(s['locator'])+'</small></li>'
  library+='</ul></details></article>'
 process='<h2>方法怎样调动项目知识</h2><div class="chain"><span>定义问题</span><b>→</b><span>建立功能与接口模型</span><b>→</b><span>分析矛盾并设计验证</span></div><p>这是对嫦娥知识的研究性重构与目标场景推演，不代表原研发团队使用这三种方法。每个步骤保留中间产物、证据及版本。</p>'
 model=run['stages'][1]['output']
 process+='<div class="function-map" aria-label="目标功能链：假设模型">'+''.join('<div><small>'+H(f['id'])+'</small><strong>'+H(f['verb']+f['object'])+'</strong><span>'+H(f['output'])+'</span></div>'for f in model['functions'])+'</div><p class="muted">目标功能模型，未经企业现场核对；各环节对应的依据见功能分析步骤。</p>'
 tc=run['stages'][2]['steps'][1]['output'][0]
 process+='<div class="tradeoff"><div><small>希望改善</small><strong>'+H(tc['improved'])+'</strong></div><b>↔</b><div><small>可能恶化</small><strong>'+H(tc['worsened'])+'</strong></div></div><p class="muted">专利描述的构型取舍；迁移到企业仍为待验证假设。</p>'+refs(tc['evidence_ids'])
 for i,stage in enumerate(run['stages'],1):
  process+='<article class="stage"><h3>'+str(i)+' · '+H(stage['name'])+'</h3><p class="muted">'+str(len(stage['steps']))+' 个步骤 · 使用版本 '+H(stage['method_version'])+'</p>'
  for s in stage['steps']:process+='<details><summary>'+H(s['title'])+'</summary>'+value(s['output'])+refs(s['evidence_ids'])+'<p class="muted">'+H(s['check']['note'])+'</p></details>'
  process+='</article>'
 process+='<details><summary>三个方法如何交接输入与输出</summary>'+value(run['handoffs'])+'</details>'
 evidence='<h2>原文证据与调用记录</h2><p>文献陈述、平台解释和目标应用假设分别保留。以下资料是相关参照；原始文件的保存和可读取不等于专家核验或技术可直接迁移。</p>'
 for e in run['evidence']:
  url='/asset?'+urllib.parse.urlencode(dict(project=run['source_case']['project_id'],scope='project',source=e['source_id'],kind='original'))
  evidence+='<article class="evidence" id="ev-'+H(e['evidence_id'])+'"><span class="badge">'+H(e['evidence_id'])+'</span><h3>'+H(e['title'])+'</h3><p>'+H(e['locator'])+'</p><small>'+H({'paper_source_statement':'论文原文陈述','patent_claim_not_independent_validation':'专利文本中的方案陈述，未独立验证','published_ground_test_not_target_validation':'论文报告的地面试验，非企业目标验证'}[e['nature']])+'</small><details><summary>查看定位原文</summary><pre>'+H(e['text'])+'</pre></details><a href="'+H(url)+'">下载来源原件 ↗</a><details><summary>来源编号、指纹与读取范围</summary>'+value({k:v for k,v in e.items()if k!='text'})+'</details></article>'
 evidence+='<details><summary>真实 MCP 调用轨迹 · '+str(len(run['retrievals']))+' 次</summary><p>真实SDK检索 + 本轮编写的固定场景分析；重放不代表对任意需求自动推理。</p><ol>'
 for r in run['retrievals']:evidence+='<li><strong>'+H(r['tool'])+'</strong> · '+H(r['purpose'])+'<details><summary>调用参数与结果指纹</summary>'+value(dict(arguments=r['arguments'],response_sha256=r['response_sha256']))+'</details></li>'
 evidence+='</ol></details><details><summary>固定版本与执行检查</summary>'+value(dict(source_case=run['source_case'],method_versions=run['method_versions'],execution_mode=run['execution_mode'],validation=run['validation']))+'</details>'
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>创新方法与项目知识 · 双库联动</title><link rel="stylesheet" href="style.css?run='+H(rid)+'"><script src="app.js?run='+H(rid)+'" defer></script></head><body><header><a href="/?project=2025-00">← 资料后台</a><span>创新设计 · 方法与知识</span><button id="replay" data-project="2025-00">重放固定示例</button></header><main><p class="eyebrow">METHOD × KNOWLEDGE</p><h1>从嫦娥采样知识，走向企业创新研究</h1><p class="intro">模拟场景：工业颗粒材料分层取样设备研发</p><div class="stats"><span><b>3</b>种方法</span><span><b>16</b>个分析步骤</span><span><b>6</b>个证据块</span><span><b>3</b>个条件性方向</span></div><p id="message" role="status"></p><nav class="tabs" role="tablist" aria-label="阅读视图"><button role="tab" aria-controls="report" aria-selected="true">企业建议</button><button role="tab" aria-controls="methods" aria-selected="false">三种方法</button><button role="tab" aria-controls="process" aria-selected="false">联动过程</button><button role="tab" aria-controls="evidence" aria-selected="false">证据与运行</button></nav><section id="report" role="tabpanel">'+report+'</section><section id="methods" role="tabpanel">'+library+'</section><section id="process" role="tabpanel">'+process+'</section><section id="evidence" role="tabpanel">'+evidence+'</section><footer>固定研究演示 · '+H(rid)+'<br>方案尚待目标企业确认与试验；源项目事实和质量评分保持。</footer></main></body></html>'
def markdown(run):
 b=run['enterprise_output'];out=['# '+b['title'],'','模拟企业需求；平台AI研究分析；未开展目标设备试验。','',b['summary'],'','## 问题定义','',run['stages'][0]['output']['framing'],'','## 方法与知识联动','']
 for st in run['stages']:
  out+=['### '+st['name'],'']
  for s in st['steps']:out+=['- '+s['title']+'；依据：'+(', '.join(s['evidence_ids'])or'模拟需求本身')]
 out+=['','## 可讨论的方向','']
 for d in b['directions']:out+=['### '+d['id']+' '+d['title'],'','状态：'+d['status']+'；未工程验证。','',d['proposal'],'','需要确认：'+'；'.join(d['assumptions']),'','代价与风险：'+'；'.join(d['costs_and_risks']),'','依据：'+', '.join(d['evidence_ids'])+'；方法步骤：'+', '.join(d['method_step_ids']),'']
 out+=['## 需要企业回答的问题','']+['- '+q['question']for q in b['questions']]+['','## 验证计划','']
 for v in b['validation_plan']:out+=['### '+v['id'],'',v['hypothesis'],'','对照：'+v['comparison'],'','测量：'+'、'.join(v['measurements']),'','通过条件：'+v['acceptance'],'','停止条件：'+v['stop'],'']
 out+=['## 边界','']+['- '+s for s in b['limitations']]+['','## 证据索引','']
 for e in run['evidence']:out+=['- '+e['evidence_id']+' · '+e['title']+' · '+e['canonical_source_id']+' / '+e['source_id']+' / '+e['chunk_id']+' · '+e['locator']]
 out+=['','运行ID：'+run['run_id'],'','实际执行：'+str(len(run['retrievals']))+'次MCP读取；固定场景分析重放，不是通用自动推理。']
 return '\n'.join(out)+'\n'
