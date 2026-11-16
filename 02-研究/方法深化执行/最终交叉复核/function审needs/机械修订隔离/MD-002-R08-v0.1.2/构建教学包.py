"""Fixed authored coding fixture. Does not infer meaning from arbitrary transcripts."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包';P.mkdir(exist_ok=True)
SHARED=B.parent/'MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 if isinstance(x,dict):x['package_version']='0.1.1'
 p=P/n;p.write_text(json.dumps(x,ensure_ascii=False,indent=2));return p
assert sha(SHARED)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70','shared teaching input changed'
source={'problem_id':'TAP-TEACH-001','version':'0.1.0','path':'../../MD-001-R48-v0.1.1/教学包/00-共享教学输入-v0.1.0.json','sha256':sha(SHARED)}
records=[
 {'id':'NOTE-T01','event_id':'EV-T01','session':'S-T01','actor':'ACT-OP','kind':'constructed_observation','text':'构造记录：一次暂停之后看到残留，操作者停机并清理；没有记录材料状态。','pause_before':True,'residue_observed':True,'independent_observation':True},
 {'id':'NOTE-T02','event_id':'EV-T01','session':'S-T01','actor':'ACT-OP','kind':'constructed_participant_statement','text':'构造原话：上次停过以后又要清理。此话描述EV-T01，不是第二次事件。','independent_observation':False},
 {'id':'NOTE-T03','event_id':'EV-T01','session':'S-T01','actor':'ACT-OP','kind':'constructed_researcher_paraphrase','text':'构造研究笔记：暂停可能使残留增加；这是对EV-T01的解释。','independent_observation':False},
 {'id':'NOTE-T04','event_id':'EV-T02','session':'S-T02','actor':'ACT-OP','kind':'constructed_observation','text':'构造记录：本段连续作业未记录暂停，也观察到残留；材料和表面条件未记录。','pause_before':False,'residue_observed':True,'independent_observation':True},
 {'id':'NOTE-T05','event_id':'EV-T03','session':'S-T03','actor':'ACT-OP','kind':'constructed_observation','text':'构造记录：另一段暂停之后未观察到明显残留；其他工况是否相同未知。','pause_before':True,'residue_observed':False,'independent_observation':True},
 {'id':'NOTE-T06','event_id':None,'session':'S-T04','actor':'ACT-OWNER','kind':'constructed_general_opinion','text':'构造原话：总之维护很麻烦。未指向可定位的具体事件。','independent_observation':False}
]
raw={'schema':'fixed_constructed_observation_fixture-1','source_binding':source,'all_records_constructed':True,'field_research_conducted':False,'real_participants':0,'consent_status':'not_applicable_no_real_participants','records':records}
save('01-构造事件原件.json',raw)
def check(d):
 if type(d.get('package_version'))is not str or d['package_version']!='0.1.1':raise ValueError('standalone_artifact_package_version_mismatch')
 if d.get('source_binding')!=source:raise ValueError('shared_context_binding_changed')
 if not d.get('all_records_constructed')or d.get('field_research_conducted')or d.get('real_participants')!=0:raise ValueError('teaching_promoted_to_field_evidence')
 if not isinstance(d.get('records'),list)or not d['records']:raise ValueError('missing_event_records')
 seen=set();groups={}
 for r in d['records']:
  if r.get('actor')not in {'ACT-OP','ACT-OWNER'}:raise ValueError('unknown_actor')
  if r['id']in seen:raise ValueError('duplicate_note_id')
  seen.add(r['id'])
  if r.get('independent_observation'):
   if r.get('kind')!='constructed_observation' or not r.get('event_id'):raise ValueError('non_event_counted_as_observation')
   if not all(isinstance(r.get(k),bool) for k in ['pause_before','residue_observed']):raise ValueError('unknown_filled_or_missing_condition')
  if r.get('event_id'):
   groups.setdefault(r['event_id'],[]).append(r)
 for ev,notes in groups.items():
  obs=[r for r in notes if r.get('independent_observation')]
  if len({(r['pause_before'],r['residue_observed'])for r in obs})>1:raise ValueError('conflicting_same_event_observations')
  if len({r['actor']for r in notes})>1:raise ValueError('unresolved_actor_identity')
 independent=[notes[0]['event_id']for notes in groups.values()if any(n.get('independent_observation')for n in notes)]
 return {'note_count':len(d['records']),'independent_constructed_event_count':len(independent),'independent_events':independent,'source_representations_for_EV_T01':len(groups.get('EV-T01',[])),'generic_opinions_not_counted':sum(r['event_id']is None for r in d['records']),'customer_findings':[],'status':'fixed_fixture_structure_checked_not_field_validated'}
count=check(raw);save('02-编码与去重.json',{'source_binding':source,'coding_is_authored_fixture_not_automatic_transcript_analysis':True,'coding':[{'note_id':r['id'],'event_id':r['event_id'],'evidence_layer':r['kind'],'may_support_causal_claim':False}for r in records],'count_result':count,'codebook':{'event':'one bounded occurrence; multiple notes may represent it','observation':'what a constructed note explicitly encodes','statement':'what a teaching participant is authored to say','interpretation':'research explanation; not observation','need_hypothesis':'proposed issue worth studying, not customer-approved requirement'}})
hyp=[{'id':'H-T01','proposition':'在本构造记录中，残留只会在暂停后出现','scope':'fixed_fixture_only','status':'rejected_in_fixture','support_note_ids':['NOTE-T01'],'counter_note_ids':['NOTE-T04'],'reason':'EV-T02的构造字段为未暂停且有残留，违反必要条件；不能据此推断真实现场因果。'}, {'id':'H-T02','proposition':'暂停在目标现场可能增加残留概率','scope':'real_world_question','status':'unknown','support_note_ids':['NOTE-T01'],'counter_note_ids':['NOTE-T04','NOTE-T05'],'reason':'极小构造集、非同工况比较，无真实取样；不能估计概率或因果。'}, {'id':'H-T03','proposition':'材料状态或表面条件可能影响残留及恢复','scope':'real_world_question','status':'unknown','support_note_ids':[],'counter_note_ids':[],'reason':'三个构造事件都未包含这些条件；只能形成下一轮观察问题。'}]
save('03-竞争解释与修订.json',{'source_binding':source,'hypotheses':hyp,'authored_coding_disagreement':{'not_actual_two_person_coding':True,'view_A':'将NOTE-T01/02/03当三次独立支持并据此选“消除暂停”','view_B':'三条同属EV-T01且分属观察/原话/解释，不得三计；EV-T02削弱单因解释','resolution':'以事件为单位去重，撤回H-T01在教学集中的成立主张；保留H-T02/H-T03待现场研究。'},'need_revision':{'old_teaching_idea':'通过消除所有暂停解决残留','new_teaching_question':'哪些作业/材料/停放条件与残留及恢复负担有关？','relation_to_shared_needs':'N-T02/N-T04继续保留研究假设；本包未更改共享v0.1.0或批准新阈值'}})
cases=[]
def run(name,category,d,expected):
 try:out=check(d);actual='accepted_for_bounded_research'
 except ValueError as e:out={'error':str(e)};actual='rejected'
 assert actual==expected,(name,actual,expected)
 cases.append({'name':name,'category':category,'expected':expected,'actual':actual,'result':out,'input_sha256':hashlib.sha256(json.dumps(d,sort_keys=True,ensure_ascii=False).encode()).hexdigest()})
run('normal-six-notes-three-events','正常',raw,'accepted_for_bounded_research')
a=copy.deepcopy(raw);del a['source_binding'];run('missing-context-binding','缺材料',a,'rejected')
a=copy.deepcopy(raw);a['field_research_conducted']=True;run('fixture-is-not-field-research','不适用',a,'rejected')
a=copy.deepcopy(raw);a['records']=raw['records'][:3];run('three-representations-one-event','边界',a,'accepted_for_bounded_research');assert cases[-1]['result']['independent_constructed_event_count']==1
for label,mut in [('same-event-contradiction',lambda a:a['records'].append({**a['records'][0],'id':'NOTE-X','pause_before':False})),('general-opinion-not-event',lambda a:a['records'][-1].update(independent_observation=True)),('duplicate-note-id',lambda a:a['records'].append(a['records'][0])),('unknown-condition-not-default-false',lambda a:a['records'][0].update(pause_before=None)),('source-version-mismatch',lambda a:a['source_binding'].update(version='0.2.0')),('empty-records',lambda a:a.update(records=[])),('unknown-actor',lambda a:a['records'][0].update(actor='NO-ACTOR'))]:
 a=copy.deepcopy(raw);mut(a);run(label,'冲突或边界',a,'rejected')
save('04-实际检查结果.json',{'runner':'构建教学包.py check()','executed':True,'scope':'fixed declared structure/event identity/promotion guards, not semantic inference','tests':cases,'passed':len(cases),'failed':0})
transfer={'scenario_id':'DOC-HANDOFF-TEACH-001','scope':'constructed_desk_transfer_no_user_test','events':[{'id':'DOC-E1','notes':['D1-observed-transfer','D2-same-transfer-paraphrase']},{'id':'DOC-E2','notes':['D3-different-transfer']}],'result':{'representations':3,'independent_events':2},'what_transfers':'event/representation distinction, observation/interpretation separation and revision history','what_does_not':'rubber-related conditions, causal explanation, field frequency, thresholds','unresolved':'真实资料交接流程、参与者与材料权利、观察窗口仍未取得'}
assert len(transfer['events'])==2 and sum(len(e['notes'])for e in transfer['events'])==3
save('05-另场景迁移检查.json',transfer)
print(json.dumps({'events':count,'executed_tests':len(cases),'transfer':'3 representations / 2 events checked'},ensure_ascii=False))

# v0.1.1 artifact provenance closure. Source problem input remains v0.1.0.
raw_path=P/'01-构造事件原件.json';coding_path=P/'02-编码与去重.json';ex_path=P/'03-竞争解释与修订.json'
coding=json.loads(coding_path.read_text());coding['artifact_bindings']={'raw_records':{'path':raw_path.name,'sha256':sha(raw_path)}};save(coding_path.name,coding)
ex=json.loads(ex_path.read_text());ex['artifact_bindings']={'raw_records':{'path':raw_path.name,'sha256':sha(raw_path)},'coding':{'path':coding_path.name,'sha256':sha(coding_path)}};save(ex_path.name,ex)
