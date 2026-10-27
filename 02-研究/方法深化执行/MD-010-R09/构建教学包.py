"""Authored switching-event coding fixture; does not discover jobs from arbitrary interviews."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包';SP=B.parent/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'
SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70';assert hashlib.sha256(SP.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','version':'0.1.0','shared_sha256':SHA,'upstream_method_status':'first_batch_pending_revision_context_only'}
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2))
stories=[{'id':'CHOICE-A','actor_id':'OWNER-A','actor_role':'ACT-OWNER','role_scope':'constructed_payer_decision_not_operator_experience','kind':'constructed_choice_episode','situation':'负责人考虑是否由现有人工作业改用新设备；无真实经营数据。','alternative_before':'continue_manual','considered':['purchase_robot','continue_manual','defer_decision'],'notes':[{'id':'A1','stage':'trigger','text':'构造：负责人说排班越来越难，开始寻找其他办法。'},{'id':'A2','stage':'evaluation','text':'构造：演示吸引了负责人，但他追问故障时本地谁来处理。'},{'id':'A3','stage':'decision','text':'构造：没有明确支援安排，负责人暂缓购买并继续人工。'}],'decision':'defer_purchase','actual_use_results':[],'post_decision_outcome':None},
{'id':'CHOICE-B','actor_id':'OWNER-B','actor_role':'ACT-OWNER','role_scope':'constructed_payer_decision_not_operator_experience','kind':'constructed_choice_episode','situation':'另一负责人在不同服务条件下考虑试用；不是与A同工况对照。','alternative_before':'continue_manual','considered':['short_trial_rental','purchase_robot','continue_manual'],'notes':[{'id':'B1','stage':'trigger','text':'构造：负责人希望降低对临时排班的依赖。'},{'id':'B2','stage':'evaluation','text':'构造：供应方提出短期租用和本地支援，负责人认为退出代价较易判断。'},{'id':'B3','stage':'decision','text':'构造：负责人同意安排租用试用；试用尚未发生。'}],'decision':'plan_rental_trial','actual_use_results':[],'post_decision_outcome':None}]
raw={'schema':'constructed_switching_episode_fixture-1','binding':BIND,'material_status':'all_authored_not_interview_records','stories':stories,'customer_approved':False,'real_participants':0,'market_size':None}
# This is an authored analytic map, not a transcript classifier or original canonical JTBD algorithm.
coding=[{'story_id':'CHOICE-A','job_actor_role':'ACT-OWNER','functional_progress_hypothesis':'在可掌控异常处置负担的情况下维持作业安排','social_progress':None,'emotional_progress':'对异常后无人支援的担忧，仅在构造笔记层表达','forces':{'push':['A1'],'pull':['A2'],'anxiety':['A2','A3'],'habit_or_existing_arrangement':['A3']},'status':'conditional_research_hypothesis'},
{'story_id':'CHOICE-B','job_actor_role':'ACT-OWNER','functional_progress_hypothesis':'在退出与支援条件较可判断时试探新的作业方式','social_progress':None,'emotional_progress':None,'forces':{'push':['B1'],'pull':['B2'],'anxiety':['B2'],'habit_or_existing_arrangement':[]},'status':'conditional_research_hypothesis'}]
put('01-两个选择与放弃事件.json',raw)
base={'raw':raw,'coding':coding,'causal_generalization':None,'operator_experience_claim':None,'segment_size':None,'recommendation_to_buy':None}
def check(i):
 r=i['raw']
 if r.get('binding')!=BIND:raise ValueError('binding_mismatch')
 if r.get('material_status')!='all_authored_not_interview_records'or r.get('customer_approved')or r.get('real_participants')!=0:raise ValueError('constructed_story_promoted_to_field')
 if r.get('market_size')is not None or i.get('segment_size')is not None:raise ValueError('market_inference_not_supported')
 if i.get('causal_generalization')is not None or i.get('operator_experience_claim')is not None or i.get('recommendation_to_buy')is not None:raise ValueError('decision_or_role_overclaim')
 ss=r.get('stories',[])
 if not ss:return {'status':'needs_event_material','jobs':[],'reason':'no decision episode supplied'}
 if any(x.get('kind')!='constructed_choice_episode'for x in ss):return {'status':'not_a_choice_episode','jobs':[],'reason':'generic preference cannot reconstruct a decision'}
 if len({x['id']for x in ss})!=len(ss):raise ValueError('duplicate_episode_id')
 byid={x['id']:x for x in ss};noteids=set()
 for s in ss:
  if s['actor_role']!='ACT-OWNER' or s['role_scope']!='constructed_payer_decision_not_operator_experience':raise ValueError('actor_role_changed')
  if not s.get('decision')or not {'trigger','evaluation','decision'}<={n['stage']for n in s['notes']}:return {'status':'needs_timeline_reconstruction','jobs':[],'reason':'decision path incomplete'}
  if s.get('actual_use_results')or s.get('post_decision_outcome')is not None:raise ValueError('trial_outcome_invented')
  for n in s['notes']:
   if n['id']in noteids:raise ValueError('duplicate_note_id')
   noteids.add(n['id'])
 if {x['story_id']for x in i['coding']}!=set(byid)or len(i['coding'])!=len(byid):raise ValueError('episode_coding_coverage_changed')
 for c in i['coding']:
  s=byid[c['story_id']];own={n['id']for n in s['notes']}
  if c['job_actor_role']!=s['actor_role']:raise ValueError('payer_job_attributed_to_operator')
  if c['status']!='conditional_research_hypothesis':raise ValueError('job_confirmed_without_research')
  if set(c['forces'])!={'push','pull','anxiety','habit_or_existing_arrangement'}:raise ValueError('coding_dimensions_changed')
  if any(n not in own for refs in c['forces'].values()for n in refs):raise ValueError('cross_episode_or_dangling_note_reference')
 return {'status':'bounded_choice_coding_checked','episodes':len(ss),'job_hypotheses':i['coding'],'selected_new_product':None,'customer_needs_confirmed':[],'causal_claims':[],'market_estimate':None,'next_questions':['实际选择发生时有哪些替代方案与责任安排','操作方是否有不同任务与困难','除支援外还有哪些条件改变','试用后的实际行为与结果'],'warning':'two different constructed contexts do not identify causal effect or segment prevalence'}
result=check(base);put('02-情境进步与力量编码.json',{'input':base,'result':result,'coding_scheme_status':'platform authored four-bucket lens, not full original interview protocol or validated causal model'})
put('03-需求修订与后续访谈.json',{'binding':BIND,'old_product_guess':'只要增加功能就能促成采用','new_research_hypotheses':['异常处置责任可能影响改变现有方式','低退出代价的试探方式可能影响选择','操作者任务需要另行研究'],'why_not_fact':'all stories constructed; role/context differ; no real choices observed','interview_questions':['最近一次认真考虑改变方式发生在何时','从谁那里听说方案，比较了哪些替代方式','哪一刻决定暂缓或试用，谁参与决定','原方式有哪些好处和不能放弃的安排','购买者/操作者各自承担什么后果'],'excluded_inference':['not_market_size','not_roi','not_general_adoption_cause','not_customer_approval']})
cases=[]
def probe(name,kind,mut,expected):
 i=copy.deepcopy(base);mut(i)
 try:o=check(i);r=o['status']
 except ValueError as e:o={'error':str(e)};r='rejected'
 assert r==expected,(name,r)
 cases.append({'name':name,'class':kind,'input':i,'expected':expected,'actual':r,'output':o})
probe('normal-two-episodes','正常',lambda x:None,'bounded_choice_coding_checked')
probe('no-event-material','缺材料',lambda x:x['raw'].update(stories=[]),'needs_event_material')
probe('preference-not-choice','不适用',lambda x:x['raw']['stories'][0].update(kind='generic_preference'),'not_a_choice_episode')
probe('trial-plan-no-real-outcome','边界',lambda x:x['raw']['stories'][1].update(actual_use_results=['运行良好']),'rejected')
probe('payer-not-operator','冲突',lambda x:x['coding'][0].update(job_actor_role='ACT-OP'),'rejected')
probe('cross-event-reference','冲突',lambda x:x['coding'][0]['forces']['push'].append('B1'),'rejected')
probe('duplicate-story','边界',lambda x:x['raw']['stories'].append(x['raw']['stories'][0]),'rejected')
probe('no-market-size-from-story','边界',lambda x:x.update(segment_size=10000),'rejected')
probe('incomplete-timeline','缺材料',lambda x:x['raw']['stories'][0].update(notes=x['raw']['stories'][0]['notes'][:1]),'needs_timeline_reconstruction')
probe('shared-problem-binding','冲突',lambda x:x['raw']['binding'].update(problem_id='OTHER'),'rejected')
probe('no-real-participant-promotion','不适用',lambda x:x['raw'].update(real_participants=2),'rejected')
put('04-实际检查结果.json',{'executed':True,'passed':len(cases),'checks':cases,'real_interviews':0,'scope':'declared episode/role/reference/state checks, not automatic jobs or causal discovery'})
transfer={'scenario':'DOC-HANDOFF-TEACH-004','origin':'constructed_desktop','choice':'负责人暂不采用新资料工具','possible_progress':'减少重复追问而又保留责任可追查','alternative':'继续使用现有文件夹与邮件','unknown':'真实选择事件、使用者角色及后果','transfer':'重建改变/维持现状的具体选择，不能把功能偏好当采用原因','actual_findings':[]}
assert transfer['actual_findings']==[]
put('05-迁移桌面检查.json',transfer)
print(json.dumps({'method':'R09','checks':len(cases),'episodes':result['episodes'],'real_interviews':0,'market_estimate':None},ensure_ascii=False))
