"""Build/check a fixed teaching requirements draft; not the production R48 solver."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 if isinstance(x,dict):x['package_version']='0.1.1'
 p=P/n;p.write_text(json.dumps(x,ensure_ascii=False,indent=2));return p
SP=P/'00-共享教学输入-v0.1.0.json'
assert sha(SP)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70','shared teaching input changed'
S=json.loads(SP.read_text())
E=B.parent/'MD-002-R08-v0.1.1/教学包/03-竞争解释与修订.json'
EV=json.loads(E.read_text())
import runpy
RP=E.parent/'01-构造事件原件.json';CP=E.parent/'02-编码与去重.json'
RAW=json.loads(RP.read_text());CODING=json.loads(CP.read_text())
validate_r08=runpy.run_path(str(B/'校验R08闭包.py'))['validate']
SHARED_EXPECT={'problem_id':S['problem_id'],'version':S['version'],'sha256':sha(SP)}
CLOSURE=validate_r08(EV,RAW,CODING,SHARED_EXPECT,SP,RP,CP)

binding={'problem_id':S['problem_id'],'version':S['version'],'sha256':sha(SP)}
evidence_binding={'path':'../../MD-002-R08-v0.1.1/教学包/03-竞争解释与修订.json','sha256':sha(E),'scope':'constructed_coding_not_field_evidence'}
issues=[{'id':'Q-T01','type':'ambiguous_success','question':'边界指什么对象与量？如何在目标条件测量？','need_id':'N-T01','owner_role':'客户/技术共同确认','due':'before_requirement_baseline','estimate':None,'reason_no_estimate':'无目标树体或测量材料，不能形成有依据估计'}, {'id':'Q-T02','type':'missing_context','question':'异常、停止、恢复与转交人工分别是什么情境？','need_id':'N-T02','owner_role':'现场研究与操作方','due':'before_baseline','estimate':None}, {'id':'Q-T03','type':'possible_solution_bias','question':'需要知道哪些状态，不先指定传感器或界面形式？','need_id':'N-T03','owner_role':'操作方与系统设计','due':'before_architecture_commitment','estimate':None}, {'id':'Q-T04','type':'causal_overclaim','question':'撤回消除所有暂停即解决残留的单因表述，调查竞争条件。','need_id':'N-T04','owner_role':'用户研究','due':'next_observation_round','estimate':None}]
save('01-问题拆解与待确认.json',{'source_binding':binding,'evidence_binding':evidence_binding,'initial_sentence':'构造教学委托：希望机器更智能、更快，停下来以后不要老清理。','initial_sentence_provenance':'authored_teaching_prompt_not_user_quote','issues':issues,'assumptions':['存在边界作用与恢复任务，仅作为研究切入','尚无材料、市场和验收目标，不能定基线'],'withdrawn_platform_hypothesis_ids':CLOSURE['retired_hypotheses'],'withdrawal_scope':'仅构造集上的强必要条件被反例推翻，不代表真实现场因果已知'})
candidates=[
 {'id':'RQ-T01','need_id':'N-T01','text':'待明确作用边界对象与目标条件后，形成可测且可追溯的边界控制要求。','kind':'incomplete_requirement_candidate','metric_proposal':'作用位置/边界偏差等候选，须先与组织边界关系校核','unit':None,'target':None,'direction':None,'acceptance':None,'verification_proposal':'现场定义与测量可行性研究；后续才选分析/试验/检查等方式','verification_status':'proposed_not_executed','basis_ids':['N-T01'],'customer_approved':False,'mandatory':'not_customer_decided'},
 {'id':'RQ-T02','need_id':'N-T02','text':'待异常类别与状态定义后，形成停止、恢复或人工交接的结果要求。','kind':'incomplete_requirement_candidate','metric_proposal':'异常检测/停止/恢复各段的可观察事件与时序，尚未选定','unit':None,'target':None,'direction':None,'acceptance':None,'verification_proposal':'任务分段与异常场景桌面研究，不预设自动恢复优于人工交接','verification_status':'proposed_not_executed','basis_ids':['N-T02'],'customer_approved':False,'mandatory':'not_customer_decided'},
 {'id':'RQ-T03','need_id':'N-T03','text':'待操作决策所需状态及数据时效定义后，形成可用信息要求。','kind':'incomplete_requirement_candidate','metric_proposal':'状态识别、数据时效、理解错误等候选指标','unit':None,'target':None,'direction':None,'acceptance':None,'verification_proposal':'先做操作任务观察与理解测试，再决定正式确认方法','verification_status':'proposed_not_executed','basis_ids':['N-T03'],'customer_approved':False,'mandatory':'not_customer_decided'},
 {'id':'RQ-T04','need_id':'N-T04','text':'待完整作业记录取得后，形成清理维护与交接的任务及服务要求。','kind':'incomplete_requirement_candidate','metric_proposal':'恢复负担分段、维护资源与等待；定义尚待观察','unit':None,'target':None,'direction':None,'acceptance':None,'verification_proposal':'R08记录现状；R50研究前后台责任；不从本构造样本估计收益','verification_status':'proposed_not_executed','basis_ids':['N-T04'],'customer_approved':False,'mandatory':'not_customer_decided'}]
draft={'schema':'fixed_requirements_research_draft-1','problem_id':'TAP-TEACH-001','draft_version':'0.1.0','source_binding':binding,'evidence_binding':evidence_binding,'customer_approved':False,'engineering_validated':False,'baseline_status':'not_baselined','actors':S['roles'],'source_needs':S['needs'],'unknowns':S['unknowns'],'candidates':candidates,'retired_hypotheses':CLOSURE['retired_hypotheses'],'accepted_causal_findings':[],'next_action':'derive_research_functions_only_with_all_unknowns','r08_lineage_check':CLOSURE,'source_scope':'all scenario inputs and events constructed; primary method literature does not establish customer facts'}
def check(d):
 if d.get('package_version')!='0.1.1'or d.get('r08_lineage_check')!=CLOSURE:raise ValueError('package_or_lineage_result_changed')
 if d.get('source_binding')!=binding or d.get('evidence_binding')!=evidence_binding:raise ValueError('binding_mismatch')
 if d.get('problem_id')!=S['problem_id']:raise ValueError('problem_identity_mismatch')
 if d.get('customer_approved')is not False or d.get('engineering_validated')is not False or d.get('baseline_status')!='not_baselined':raise ValueError('unauthorized_status_promotion')
 if d.get('source_needs')!=S['needs'] or d.get('unknowns')!=S['unknowns']:raise ValueError('source_need_or_unknown_changed')
 if d.get('actors')!=S['roles']:raise ValueError('actor_identity_or_provenance_changed')
 ids=set();coverage=set();allowed={r['id']for r in S['needs']}
 for r in d.get('candidates',[]):
  if not isinstance(r.get('text'),str)or not r['text'].strip()or r.get('kind')!='incomplete_requirement_candidate':raise ValueError('invalid_candidate_shape')
  if r['id']in ids:raise ValueError('duplicate_requirement_id')
  ids.add(r['id']);coverage.add(r['need_id'])
  if r['need_id']not in allowed or not r.get('basis_ids')or any(x not in allowed for x in r['basis_ids']):raise ValueError('dangling_need_or_basis')
  if r['need_id']not in r['basis_ids']:raise ValueError('need_basis_mismatch')
  if any(r.get(k)is not None for k in ['unit','target','direction','acceptance']):raise ValueError('unsupported_numeric_or_acceptance_completion')
  if r.get('customer_approved')is not False or r.get('mandatory')!='not_customer_decided' or r.get('verification_status')!='proposed_not_executed':raise ValueError('candidate_status_promotion')
 if coverage!=allowed:raise ValueError('unallocated_research_need')
 if d.get('retired_hypotheses')!=CLOSURE['retired_hypotheses']or d.get('accepted_causal_findings')!=[]:raise ValueError('rejected_cause_promoted')
 return {'status':'research_draft_structure_and_declared_fidelity_passed','requirement_candidates':len(ids),'all_incomplete':True,'ready_for_customer_baseline':False,'permitted_next_action':'function_research_with_unknowns','does_not_check':['arbitrary_text_semantic_correctness','customer_truth','physical_feasibility','actual_measurability','safety']}
save('02-要求候选与双向追溯.json',draft)
save('03-交接与变更影响.json',{'source_binding':binding,'evidence_binding':evidence_binding,'trace':[{'need_id':n['id'],'candidate_ids':[r['id']for r in candidates if r['need_id']==n['id']],'source_status':n['kind'],'allocated_to':'R14研究分解或R50服务研究，尚无实际功能交付批准'}for n in S['needs']],'change_scenario':{'proposed_change':'将“消除暂停”改为“识别不同工况下残留和恢复负担”','changed_type':'platform_explanatory_hypothesis_not_customer_baseline','basis':'R08固定构造集H-T01被NOTE-T04反例否定','potentially_affected_artifacts':['问题解释','作用分解范围','概念生成目标','试验观察条件'],'actual_downstream_files_modified':[],'rebuild_rule':'下游已有产物如依赖旧原因解释，应人工核影响后按新版本重建；共享v0.1.0不得悄改'}})
cases=[]
def run(name,category,d,expected):
 try:out=check(d);actual='accepted_for_bounded_research'
 except ValueError as e:out={'error':str(e)};actual='rejected'
 assert actual==expected,(name,actual,expected)
 cases.append({'name':name,'category':category,'expected':expected,'actual':actual,'result':out,'input_sha256':hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
run('normal-unknowns-retained','正常',draft,'accepted_for_bounded_research')
a=copy.deepcopy(draft);a['candidates']=a['candidates'][:-1];run('missing-one-need','缺材料',a,'rejected')
a=copy.deepcopy(draft);a['customer_approved']=True;run('not-a-customer-baseline','不适用',a,'rejected')
a=copy.deepcopy(draft);a['candidates'][0]['target']=0;run('zero-is-not-unknown','边界',a,'rejected')
for name,mut in [('conflicting-version',lambda a:a['source_binding'].update(version='0.2.0')),('actor-provenance-loss',lambda a:a['actors'][0].update(status='interviewed')),('dangling-basis',lambda a:a['candidates'][0].update(basis_ids=['NO-SUCH-ID'])),('inferred-direction',lambda a:a['candidates'][0].update(direction='le')),('accepted-causal-overclaim',lambda a:a['accepted_causal_findings'].append('H-T01')),('duplicate-candidate',lambda a:a['candidates'].append(a['candidates'][0]))]:
 a=copy.deepcopy(draft);mut(a);run(name,'冲突或来源边界',a,'rejected')
save('04-实际检查结果.json',{'runner':'构建教学包.py check()','executed':True,'scope':'fixed declared structure, source closure and status checks; no engine/MCP change','tests':cases,'passed':len(cases),'failed':0})
transfer={'scenario_id':'DOC-HANDOFF-TEACH-001','scope':'constructed_desktop_transfer','prompt':'让资料交接更可靠','classification':[{'text':'更可靠','kind':'vague_desired_outcome','not_a_baselined_requirement':True},{'text':'必须用某品牌数据库','kind':'unjustified_solution_constraint','disposition':'ask rationale; do not treat as user need'},{'text':'交接时能核对资料版本','kind':'proposed_result_need','target':None,'customer_approved':False}],'transfer_result':'可沿用来源→愿望/约束/要求候选→未知→验证问题的分层，但不得迁用割胶指标或工况','real_user_research':False}
assert all(x.get('customer_approved')is not True for x in transfer['classification'])
save('05-另场景迁移检查.json',transfer)
print(json.dumps({'result':check(draft),'executed_tests':len(cases),'transfer':'classification desk check passed'},ensure_ascii=False))

# Independent-form regression mutations for previously accepted cross-package attacks.
closure_tests=[]
def attack(name,which,mutate,expected):
 a,b,c=copy.deepcopy(EV),copy.deepcopy(RAW),copy.deepcopy(CODING)
 target={'ex':a,'raw':b,'coding':c}[which];mutate(target)
 try:
  result=validate_r08(a,b,c,SHARED_EXPECT,SP,RP,CP);actual='accepted'
 except ValueError as e:result={'error':str(e)};actual='rejected'
 assert actual==expected,(name,actual)
 closure_tests.append({'name':name,'expected':expected,'actual':actual,'result':result})
attack('normal-source-closed','ex',lambda x:None,'accepted')
attack('previous-cross-problem-accepted-now-rejected','ex',lambda x:x['source_binding'].update(problem_id='OTHER-PROBLEM'),'rejected')
attack('wrong-problem-version','ex',lambda x:x['source_binding'].update(version='0.2.0'),'rejected')
attack('wrong-shared-sha','ex',lambda x:x['source_binding'].update(sha256='0'*64),'rejected')
attack('wrong-shared-path','ex',lambda x:x['source_binding'].update(path='../../../MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'),'rejected')
attack('missing-withdrawal-id','ex',lambda x:x.update(hypotheses=[h for h in x['hypotheses']if h['id']!='H-T01']),'rejected')
attack('duplicate-withdrawal-id','ex',lambda x:x['hypotheses'].append(x['hypotheses'][0]),'rejected')
attack('withdrawal-status-unknown','ex',lambda x:x['hypotheses'][0].update(status='unknown'),'rejected')
attack('dangling-counterevidence','ex',lambda x:x['hypotheses'][0].update(counter_note_ids=['MISSING-NOTE']),'rejected')
attack('withdrawal-no-counterevidence','ex',lambda x:x['hypotheses'][0].update(counter_note_ids=[]),'rejected')
attack('counterevidence-insufficient','ex',lambda x:x['hypotheses'][0].update(counter_note_ids=['NOTE-T05']),'rejected')
attack('raw-other-problem','raw',lambda x:x['source_binding'].update(problem_id='OTHER'),'rejected')
attack('coding-source-other-version','coding',lambda x:x['source_binding'].update(version='0.2.0'),'rejected')
attack('wrong-bound-record-sha','ex',lambda x:x['artifact_bindings']['raw_records'].update(sha256='0'*64),'rejected')
attack('unconfirmed-alternative-promoted','ex',lambda x:x['hypotheses'][1].update(status='confirmed'),'rejected')
for label,mutate in [('r48-extra-retired-id',lambda x:x['retired_hypotheses'].append('GHOST')),('r48-retired-id-omitted',lambda x:x.update(retired_hypotheses=[])),('r48-lineage-decision-tampered',lambda x:x['r08_lineage_check'].update(retired_hypotheses=['GHOST'])),('r48-package-version-missing',lambda x:x.pop('package_version'))]:
 v=copy.deepcopy(draft);mutate(v)
 try:check(v);actual='accepted';r={}
 except ValueError as err:actual='rejected';r={'error':str(err)}
 assert actual=='rejected',label
 closure_tests.append({'name':label,'expected':'rejected','actual':actual,'result':r})
save('06-v0.1.1跨包闭包检查.json',{'executed':True,'checks':closure_tests,'passed':len(closure_tests),'closure_result':CLOSURE,'does_not_prove':'arbitrary language entailment or real-world causes'})
print(json.dumps({'package':'0.1.1','shared_input':'0.1.0','new_closure_checks':len(closure_tests),'closed_withdrawal':CLOSURE['retired_hypotheses']},ensure_ascii=False))
