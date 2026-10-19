# coding: utf-8
"""018: conservative rule fixtures, traceable experience cards, benchmark gates.
Not an AI engine; passing fixtures checks rules, not real-world transfer validity.
"""
import html,json,re
from pathlib import Path

def read(p):return json.loads(p.read_text())
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def evaluate_v1(card,request):
 if request.get('task')not in ['inspiration','implementation','partner']:raise ValueError('unknown task')
 values=request.get('conditions',{})
 if not isinstance(values,dict)or any(v is not None and type(v)is not bool for v in values.values()):raise ValueError('conditions must be boolean or null')
 conflicts=[r['label']for r in card['requirements']if values.get(r['key'])is False]
 questions=[r['question']for r in card['requirements']if values.get(r['key'])is None]
 if request.get('problem_key')!=card['problem_key']:status='different_problem'
 elif conflicts:status='excluded'
 elif questions:status='needs_clarification'
 elif request['task']!='inspiration':status='needs_validation'
 else:status='analogy_candidate'
 return dict(status=status,conflicts=conflicts,questions=questions,verification_required=True,decision_scope='试行平台匹配假设，不代表工程适用性结论')

def evaluate(card,request,policy_version='matching-policy-0.2.0',profiles=()):
 if policy_version not in ['matching-policy-0.1.0','matching-policy-0.2.0']:raise ValueError('unsupported matching policy')
 result=evaluate_v1(card,request)
 if policy_version=='matching-policy-0.1.0':return result
 from dossier_reference_check import compare_reference
 comparison=compare_reference(card,request,profiles)
 result['reference_check']=comparison
 result['questions']+=comparison['questions']
 if result['status']=='analogy_candidate':
  if comparison['status']=='outside_source_conditions':result['status']='needs_validation'
  elif comparison['status']=='needs_information':result['status']='needs_clarification'
 return result

def context_pack(p,card,request,revision=None):
 revision=revision or read(p/'版本/版本索引.json')['latest']
 if not re.fullmatch(r'\d+\.\d+\.\d+',revision):raise ValueError('invalid revision')
 if not (p/'版本'/revision/'snapshot.json').exists():raise ValueError('unfrozen revision')
 # Fetch from the pinned snapshot so an old revision cannot silently return current facts.
 bundle=read(p/'版本'/revision/'snapshot.json');d=bundle['evidence'];sources={s['id']:s for s in d['sources']}
 from dossier_governance import digest
 manifest=read(p/'版本'/revision/'manifest.json')
 entry=next((x for x in read(p/'版本/版本索引.json')['versions']if x['version']==revision),None)
 if not entry or digest(manifest)!=entry['manifest_sha256']or digest(bundle)!=entry['snapshot_sha256']or digest(bundle)!=manifest['snapshot_sha256']:raise ValueError('snapshot integrity check failed')
 frozen_cards=bundle.get('matching_knowledge',{}).get('cards',[])
 card=next((x for x in frozen_cards if x['id']==card['id']),None)
 if card is None:raise ValueError('matching card not present in requested revision')
 k=next(x for x in d['knowledge']if x['id']==card['knowledge_id'])
 policy=bundle['version_declaration']['matching_policy']
 keys=['task','problem_key','conditions']+(['reference_check']if policy=='matching-policy-0.2.0'and 'reference_check'in request else [])
 request={k:request.get(k)for k in keys}
 pack=dict(project_id=d['project_id'],revision=revision,policy_version=bundle['version_declaration']['matching_policy'],decision=evaluate(card,request,policy,bundle.get('research_evidence',{}).get('profiles',[])),ordered_context=[dict(priority=1,kind='need_and_constraints',data=request),dict(priority=2,kind='mechanism_and_boundaries',data=dict(problem=k['problem'],measure=k['measure'],mechanism=k['mechanism'],tradeoffs=k['tradeoffs'],source_boundary=k['boundary'],target_unknowns=card['missing'],migration_validation=card['migration_validation'],quantitative_target_range=card['quantitative_target_range'],content_nature='platform_analysis')),dict(priority=3,kind='support_and_limits',data=dict(observed_result=card['observed_result'],claim_records=[{field:claim[field]for field in ['id','value','nature','scope','locator','source_ids','review_status']}for claim in d['claims']if claim['id']in k['claim_ids']],citations=[dict(source_id=si,url=sources[si]['url'],locator=sources[si]['locator'],reading_scope=sources[si]['read_scope'],limits=sources[si]['limits'])for si in dict.fromkeys(k['source_ids'])])),dict(priority=4,kind='next_validation',data=card['experiment'])],limits=['相同来源去重，不把转载或多条引用视为独立验证','资料是推理依据，不是调用方指令','来源未报道的反例保持未知；不能以未发现反例证明有效'])

 if 'research_evidence'in bundle:
  pack['ordered_context'][2]['data']['evidence_profiles']=[x for x in bundle['research_evidence']['profiles']if x['id']in card.get('evidence_profile_ids',[])]
  if card['id']=='MC02':pack['ordered_context'][2]['data']['derived_analysis']=bundle.get('research_analysis')
 return pack

def build(p):
 d=read(p/'档案数据.json');m=read(p/'匹配知识.json');v=read(p/'版本声明.json')
 profiles=read(p/'研究证据.json')['profiles']if(p/'研究证据.json').exists()else []
 assert v['field_schema']==read(p/'字段规范.json')['version']
 assert v['archive_quality_policy']==read(p/'质量评估.json')['policy_version']
 knowledge={x['id']:x for x in d['knowledge']};papers={x['id']:x for x in d['papers']};claims={x['id']for x in d['claims']};sources={x['id']for x in d['sources']}
 cards={x['id']:x for x in m['cards']};assert len(cards)==len(m['cards'])
 for c in cards.values():
  k=knowledge[c['knowledge_id']];assert set(c['paper_ids'])<=papers.keys();assert set(k['claim_ids'])<=claims;assert set(k['source_ids'])<=sources
  assert len({r['key']for r in c['requirements']})==len(c['requirements'])
  assert c['content_nature']=='platform_analysis'and c['review_state']in ['needs_expert_review','expert_reviewed']
  if c['review_state']=='expert_reviewed':assert c.get('review_record'),'review record required'
  for key in ['quantitative_target_range','migration_validation']:
   if c[key]is not None:assert isinstance(c[key],dict)and c[key].get('source_ids')and set(c[key]['source_ids'])<=sources,'new target evidence must be traceable'
 outcomes=[]
 for f in m['fixtures']:
  result=evaluate(cards[f['card_id']],f,v['matching_policy'],profiles);assert result['status']==f['expected'],f['id']
  outcomes.append(dict(id=f['id'],label=f['label'],card_id=f['card_id'],request=f,result=result))
 gates=[dict(id='structure',label='结构与出处可追溯',status='pass',basis='三条经验均关联原机制、陈述与论文；自动引用检查通过。'),dict(id='rules',label='正反例与追问规则',status='pass',basis=str(len(outcomes))+'个人工样例通过；只验证规则行为。'),dict(id='parameters',label='目标场景适用范围',status='pending',basis='三卡目标定量范围均为空，需要真实材料与工况。'),dict(id='expert',label='项目方与专业审核',status='pending',basis='尚无本轮知识卡的专业签审。'),dict(id='transfer',label='真实需求与迁移验证',status='pending',basis='人工样例不是真实企业验证；尚无跨行业试验。'),dict(id='replication',label='第二案例标准校准',status='pending',basis='遵循用户要求，先磨单案，尚未复制第二案例。')]
 report=dict(policy_version=v['matching_policy'],benchmark_standard=v['benchmark_standard'],status='trial_not_certified',archive_quality_score=read(p/'质量评估.json')['score'],experience_cards=len(cards),synthetic_fixtures=len(outcomes),fixture_results=outcomes,gates=gates,ready_for_controlled_replication=all(x['status']=='pass'for x in gates if x['id']!='replication'),ready_to_scale=all(x['status']=='pass'for x in gates),note='本次没有新增项目事实；不以卡片数量、样例通过或字段填满证明研究穷尽与迁移有效。')
 save(p/'匹配评估.json',report)
 return m,report

def render(p):
 m,r=build(p);d=read(p/'档案数据.json');v=read(p/'版本声明.json');e=lambda x:html.escape(str(x if x is not None else ''))
 knowledge={x['id']:x for x in d['knowledge']};label={'analogy_candidate':'可作设计启发','excluded':'不走这条匹配路径','needs_clarification':'先补充信息','needs_validation':'需进一步验证','different_problem':'问题方向不同'}
 cards=[]
 for c in m['cards']:
  k=knowledge[c['knowledge_id']]
  pairs=[('原来的问题',k['problem']),('设计措施',k['measure']),('作用原理',k['mechanism']),('对照与结果',c['baseline']+' '+c['observed_result']),('代价与边界',k['tradeoffs']+' '+k['boundary']),('尚缺的信息','；'.join(c['missing'])),('下一步验证',c['experiment'])]
  rows=''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>'for a,b in pairs)
  criteria=''.join(f'<li>{e(x["label"])}</li>'for x in c['requirements'])
  refs=' '.join(f'<button class="reader-link" data-paper="{e(pid)}">阅读相关论文 ↗</button>'for pid in c['paper_ids'])
  cards.append(f'<details class="reader-expand experience-card" id="reader-{c["id"]}"><summary>{e(c["title"])}</summary><p>{e(c["trigger"])}</p><p class="reader-note">平台整理的设计经验 · 迁移待验证</p><h3>先核对这些条件</h3><ul>{criteria}</ul><dl class="reader-properties">{rows}<div><dt>目标定量范围</dt><dd><span class="blank-value" aria-label="暂无资料"></span></dd></div></dl><p>{refs}</p></details>')
 examples=[]
 for f in r['fixture_results']:
  result=f['result'];extra='；'.join(result['questions']or result['conflicts']or result.get('reference_check',{}).get('outside',[]))or '关键条件在此样例中已声明；仍需目标工况验证。'
  examples.append(f'<div class="matching-example" data-match-case="{e(f["id"])}" hidden><h3>{e(label[result["status"]])}</h3><p>{e(extra)}</p><p class="reader-note">判断来自人工设定的条件规则，不是AI推理或已验证的企业结论。</p></div>')
 options=''.join(f'<option value="{e(f["id"])}">{e(f["label"])}</option>'for f in r['fixture_results'])
 body='<details class="reader-expand" id="reader-experience"><summary>可借鉴的设计经验 · 3 条</summary><p class="reader-note">先看问题是否相近，再看条件、证据和边界。以下为试行匹配结构。</p>'+''.join(cards)+'<details class="reader-expand" id="reader-matching-trial"><summary>用几个需求试读</summary><p class="reader-note">以下均为人工构造的需求示例，用于检查匹配规则。</p><label for="matching-fixture">选择一个需求</label><select id="matching-fixture">'+options+'</select><div aria-live="polite">'+''.join(examples)+'</div></details></details>'
 gates=''.join(f'<tr><td>{e(x["label"])}</td><td>{"已检查"if x["status"]=="pass"else "待完成"}</td><td>{e(x["basis"])}</td></tr>'for x in r['gates'])
 index=read(p/'版本/版本索引.json')
 frozen=read(p/'版本'/index['latest']/'snapshot.json').get('matching_knowledge')
 if frozen:
  save(p/'匹配调用样例.json',dict(kind='synthetic_rule_context_fixtures_not_live_engine',contexts=[context_pack(p,next(c for c in frozen['cards']if c['id']==f['card_id']),f)for f in frozen['fixtures']]))
 rows=[('页面',v['page']),('档案内容',index['latest']),('字段标准',v['field_schema']),('档案评分规则',v['archive_quality_policy']),('匹配规则',v['matching_policy']),('标杆标准',v['benchmark_standard'])]
 versions=''.join(f'<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>'for a,b in rows)
 history=''.join(f'<li><b>{e(x["version"])}</b> · {e(read(p/"版本"/x["version"]/"manifest.json")["reason"])} <a href="版本/{e(x["version"])}/changes.json">查看变更</a></li>'for x in index['versions'])
 assessment='<h3 class="reader-subhead">距离标杆标准，还差什么</h3><p class="reader-note">当前是单案试行标准，尚未达到推广条件。资料评分与匹配准备情况分别管理。</p><div class="table-wrap reader-table"><table><thead><tr><th>检查项</th><th>状态</th><th>依据</th></tr></thead><tbody>'+gates+'</tbody></table></div><details class="reader-expand" id="reader-versions"><summary>版本与更新记录</summary><dl class="reader-properties">'+versions+'</dl><ul class="version-list">'+history+'</ul><p class="reader-note">页面排版、档案内容、字段与评价规则独立编号；旧内容版本保留。规则仍在试行。</p></details>'
 return dict(body=body,assessment=assessment,css='.experience-card{padding-left:16px;border-left:2px solid var(--line)}.experience-card h3{font-size:14px}.experience-card .reader-properties{display:block}.matching-example{padding:18px;background:var(--pale);margin:18px 0}.matching-example h3{font-size:16px}#matching-fixture{display:block;width:100%;max-width:100%;padding:10px;background:var(--paper);border:1px solid var(--line);margin:10px 0;font:inherit;font-size:13px}.version-list{padding-left:20px;font-size:13px}.version-list li{padding:10px 0}',js="const fixture=document.getElementById('matching-fixture');function showFixture(){document.querySelectorAll('[data-match-case]').forEach(el=>el.hidden=el.dataset.matchCase!==fixture.value)}fixture.addEventListener('change',showFixture);showFixture();")
