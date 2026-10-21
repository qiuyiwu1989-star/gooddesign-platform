# coding: utf-8
"""041: readable research brief, three-stage story, contextual evidence; frozen runs stay immutable."""
import html,json,urllib.parse
import innovation_methods as im
from workspace_ui import CSS,nav
H=lambda x:html.escape(str(x),quote=True)
def lis(rows):return '<ul>'+''.join('<li>'+H(x)+'</li>'for x in rows)+'</ul>'
def value(v):return '<pre>'+H(json.dumps(v,ensure_ascii=False,indent=2))+'</pre>'
def refs(ids):return '<div class="refs">'+''.join('<button data-evidence="'+H(e)+'">查看依据 <span aria-hidden="true">↗</span></button>'for e in dict.fromkeys(ids))+'</div>'
def evidence_card(e,project):
 url='/asset?'+urllib.parse.urlencode(dict(project=project,scope='project',source=e['source_id'],kind='original'))
 labels={'paper_source_statement':'论文原文','patent_claim_not_independent_validation':'专利方案陈述 · 未独立验证','published_ground_test_not_target_validation':'地面试验报告 · 非目标企业验证'}
 return '<article class="evidence" id="ev-'+H(e['evidence_id'])+'"><span class="badge">'+H(labels[e['nature']])+'</span><h3>'+H(e['title'])+'</h3><p class="muted">'+H(e['locator'])+'</p><details class="original"><summary>阅读定位原文</summary><div class="source-text">'+H(e['text'])+'</div></details><a class="source-download" href="'+H(url)+'">下载来源原件 ↓</a><details class="technical"><summary>来源编号与校验信息</summary>'+value({k:v for k,v in e.items()if k!='text'})+'</details></article>'
def render(run):
 def refs(ids):
  rows={e['evidence_id']:e for e in run['evidence']};return '<div class="refs">'+''.join('<button data-evidence="'+H(e)+'" aria-label="'+H(rows[e]['title']+'，'+rows[e]['locator'])+'">'+H(('专利'if 'patent' in rows[e]['nature']else'论文')+' · '+rows[e]['title'][:12])+('…'if len(rows[e]['title'])>12 else'')+' ↗</button>'for e in dict.fromkeys(ids))+'</div>'
 rid=run['run_id'];brief=run['enterprise_output'];pid=run['source_case']['project_id'];methods=[im.read_method(m['method_id'],m['version'],'full')['data']for m in run['method_versions']]
 report='<div class="report-heading"><span class="section-kicker">研究建议</span><h2>把“取到样品”和“保留信息”分开考虑</h2><p class="lead">'+H(brief['summary'])+'</p></div><div class="directions">'
 for i,d in enumerate(brief['directions'],1):
  report+='<details class="direction" id="direction-'+H(d['id'])+'"><summary><span class="num">%02d</span><span><strong>'%i+H(d['title'])+'</strong><span class="summary-note">'+H('已排除：与已知约束冲突'if d['status']=='excluded'else '可讨论方向 · 待企业确认与试验')+'</span></span><span class="chevron" aria-hidden="true">＋</span></summary><div class="detail-body"><p>'+H(d['proposal'])+'</p><div class="columns"><div><h4>需要先确认</h4>'+lis(d['assumptions'])+'</div><div><h4>代价与风险</h4>'+lis(d['costs_and_risks'])+'</div></div>'+refs(d['evidence_ids'])+'<a class="text-link" href="#process" data-stage="2">看这个方向如何形成 →</a><details class="technical"><summary>字段关联</summary>'+value(dict(method_steps=d['method_step_ids'],knowledge_ids=d['source_knowledge_ids'],validation=d['validation_id']))+'</details></div></details>'
 report+='</div><div class="next-action"><span class="section-kicker">下一步</span><h3>先确认企业条件，再选一个方向做验证</h3><p>'+H(brief['next_decision'])+'</p><div class="next-links"><button data-open="questions">需要企业回答的 '+str(len(brief['questions']))+' 个问题 →</button><button data-open="tests">查看 '+str(len(brief['validation_plan']))+' 项验证计划 →</button></div></div>'
 report+='<details class="reading-block" id="questions"><summary>向企业确认的问题 <span>'+str(len(brief['questions']))+' 项</span></summary><ol class="questions">'+''.join('<li>'+H(q['question'])+'</li>'for q in brief['questions'])+'</ol></details><details class="reading-block" id="tests"><summary>验证计划 <span>尚未试验</span></summary>'
 for v in brief['validation_plan']:
  report+='<details class="test"><summary>'+H(v['hypothesis'])+'</summary><dl><dt>怎么比较</dt><dd>'+H(v['comparison'])+'</dd><dt>测量什么</dt><dd>'+H('、'.join(v['measurements']))+'</dd><dt>通过标准</dt><dd>'+H(v['acceptance'])+'</dd><dt>何时停止</dt><dd>'+H(v['stop'])+'</dd></dl></details>'
 report+='</details><details class="reading-block"><summary>建议的使用范围</summary>'+lis(brief['limitations'])+'</details>'
 # A short narrative for each stage is shown before technical step artifacts.
 framing=run['stages'][0]['output'];model=run['stages'][1]['output'];tc=run['stages'][2]['steps'][1]['output'][0]
 summaries=[('先明确什么叫“做好了”',framing['framing']),('把问题放回完整作业链','不只研究取样头。沿进样、收集、保护、封口和转送检查作用关系，寻找信息丢失和失效的接口。'),('找出改善一项会付出什么代价',tc['target_statement'])]
 process='<div class="report-heading"><span class="section-kicker">分析过程</span><h2>先定义问题，再找功能与取舍</h2><p>这三种方法是本轮研究采用的分析路径，不代表嫦娥原研发团队的方法使用记录。</p></div><div class="stage-picker" role="tablist" aria-label="分析步骤">'+''.join('<button role="tab" id="stage-tab-'+str(i)+'" aria-controls="stage-'+str(i)+'" aria-selected="'+str(i==0).lower()+'" tabindex="'+('0'if i==0 else'-1')+'"><small>0'+str(i+1)+'</small><strong>'+H(m['name'])+'</strong><span>'+H(['明确目标与边界','看清作用与接口','分析取舍与验证'][i])+'</span></button>'for i,m in enumerate(methods))+'</div>'
 for i,(stage,m)in enumerate(zip(run['stages'],methods)):
  process+='<div id="stage-'+str(i)+'" role="tabpanel" aria-labelledby="stage-tab-'+str(i)+'"'+(' hidden'if i else'')+'><h3>'+H(summaries[i][0])+'</h3><p>'+H(summaries[i][1])+'</p>'
  if i==0:
   process+='<dl class="brief"><dt>研究对象</dt><dd>'+H(framing['object'])+'</dd><dt>系统范围</dt><dd>'+H(framing['boundary'])+'</dd><dt>怎样衡量</dt><dd>'+lis(v['name']+'：阈值待企业确认'for v in framing['requirements'])+'</dd></dl>'
  if i==1:
   process+='<div class="function-map" aria-label="目标功能链：假设模型">'+''.join('<div><strong>'+H(f['verb']+f['object'])+'</strong><span>'+H(f['output'])+'</span></div>'for f in model['functions'])+'</div><p class="muted">目标功能模型，尚待企业现场核对。</p>'
  if i==2:
   process+='<div class="tradeoff"><div><small>希望改善</small><strong>'+H(tc['improved'])+'</strong></div><b aria-hidden="true">↔</b><div><small>可能付出的代价</small><strong>'+H(tc['worsened'])+'</strong></div></div><p class="muted">只有企业构型与颗粒路径确有相同耦合，才进一步研究这一取舍。</p>'+refs(tc['evidence_ids'])
  process+='<details class="reading-block method"><summary>'+H(m['name'])+' · 查看方法与 '+str(len(m['steps']))+' 个执行步骤</summary><p>'+H(m['purpose'])+'</p><div class="columns"><div><h4>需要的输入</h4>'+lis(x['label']for x in m['inputs'])+'</div><div><h4>得到的产物</h4>'+lis(x['label']for x in m['outputs'])+'</div></div><ol class="method-steps">'
  for s,applied in zip(m['steps'],stage['steps']):
   process+='<li><h4>'+H(s['title'])+'</h4><p>'+H(s['operation'])+'</p><details><summary>检查与停止条件</summary><p>'+H('；'.join(s['checks']))+'</p><p>'+H(s['stop_condition'])+'</p></details>'+refs(applied['evidence_ids'])+'<details class="technical"><summary>本次执行的结构化记录</summary>'+value(applied['output'])+'</details></li>'
  process+='</ol><details><summary>适用边界与质量检查</summary>'+lis(m['exclusions'])+lis(m['failure_cases'])+lis(m['quality_checks'])+'</details><details><summary>方法来源与改编说明</summary>'+lis(m['provenance']['adaptations'])+'<ul>'
  for s in m['provenance']['sources']:process+='<li><a href="'+H(s['url'])+'" target="_blank" rel="noopener">'+H(s['publisher']+' · '+s['title'])+' ↗</a><p>'+H(s['basis'])+'</p></li>'
  process+='</ul></details></details></div>'
 evidence='<div class="report-heading"><span class="section-kicker">参考资料</span><h2>回到原文，核对每一项判断</h2><p>论文陈述、专利方案和地面试验分别标注。它们支持研究参照，不能直接证明企业应用效果。</p></div>'+''.join(evidence_card(e,pid)for e in run['evidence'])
 technical='<details id="run-details" class="reading-block"><summary>版本、调用与运行工具</summary><p>真实 SDK 读取双库；分析为本轮编写的固定场景研究。重新读取会生成独立记录，不会对新需求自动推理。</p><button id="replay" data-project="'+H(pid)+'">重新读取并生成记录</button><p id="message" role="status"></p><details><summary>调用轨迹 · '+str(len(run['retrievals']))+' 次</summary><ol>'
 for r in run['retrievals']:technical+='<li>'+H(r['purpose'])+'<details><summary>调用参数</summary>'+value(dict(tool=r['tool'],arguments=r['arguments'],response_sha256=r['response_sha256']))+'</details></li>'
 technical+='</ol></details><details><summary>版本与校验信息</summary>'+value(dict(run_id=rid,source_case=run['source_case'],method_versions=run['method_versions'],execution_mode=run['execution_mode'],validation=run['validation']))+'</details></details>'
 tabs=[('report','企业建议'),('process','分析过程'),('evidence','参考资料')]
 return '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="inno-view-version" content="6.0.0"><title>采样设备创新研究 · 创新设计</title><link rel="icon" href="data:,"><link rel="stylesheet" href="style.css?run='+H(rid)+'"><style>'+CSS+'</style><script src="app.js?run='+H(rid)+'" defer></script></head><body>'+nav('research',pid)+'<main id="workspace-content"><div class="page-heading"><div><p class="eyebrow">创新研究 / 嫦娥知识应用示例</p><h1>颗粒材料分层取样设备</h1><p class="intro">从嫦娥采样系统中寻找可借鉴的设计思路。</p></div><span class="badge">模拟企业需求 · AI 研究</span></div><div class="context-note"><span>当前阶段：概念探索</span><p>还需企业补充材料、工况与验收要求；建议均待试验验证。</p></div><nav class="tabs" role="tablist" aria-label="阅读视图">'+''.join('<button role="tab" id="tab-'+key+'" aria-controls="'+key+'" aria-selected="'+str(i==0).lower()+'" tabindex="'+('0'if i==0 else'-1')+'">'+name+'</button>'for i,(key,name)in enumerate(tabs))+'</nav>'+''.join('<section id="'+key+'" role="tabpanel" aria-labelledby="tab-'+key+'">'+content+'</section>'for key,content in [('report',report),('process',process),('evidence',evidence)])+technical+'<footer>项目事实、AI 分析与目标应用分开保存。<span class="offline-note" hidden>离线阅读版；下载原件和重新读取需要本地后台。</span></footer></main><dialog id="evidence-dialog" aria-labelledby="evidence-dialog-title"><div class="dialog-top"><h2 id="evidence-dialog-title">建议的原文依据</h2><button id="close-evidence" aria-label="关闭原文依据">关闭 ×</button></div><div id="evidence-context"></div><div id="evidence-body"></div></dialog><noscript><style>[role=tabpanel][hidden]{display:block!important}.tabs,.stage-picker,#replay,.refs,[data-open]{display:none!important}</style></noscript></body></html>'
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
