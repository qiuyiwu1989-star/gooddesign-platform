"""Purpose/representation teaching fixture, not generic prototype adequacy judgment."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包'
SP=B.parent/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'
SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70';assert hashlib.sha256(SP.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','version':'0.1.0','shared_sha256':SHA,'upstream_method_status':'first_batch_pending_revision_context_only'}
# Fixed authored capabilities are not accepted from caller input.
CAPABILITIES={'P-PAPER-LABEL':{'state_meaning'},'P-GEOMETRY-MOCK':{'proxy_surface_geometry'},'P-ANIMATION':{'visual_impression'}}
CLAIM_NEEDS={'state_meaning':{'need':'N-T03','required':'state_meaning'},'internal_boundary_accuracy':{'need':'N-T01','required':'real_tissue_relation'},'system_safety':{'need':'N-T02','required':'validated_safety_case'}}
def put(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2))
plan={'schema':'design_thinking_purpose_fixture-1','binding':BIND,'origin':'constructed_teaching_plan','learning_claim':'state_meaning','source_need':'N-T03','prototype':'P-PAPER-LABEL','declared_variable':'label','variants':[{'id':'V-A','label':'继续','shape':'same_card','position':'same_position'},{'id':'V-B','label':'恢复','shape':'same_card','position':'same_position'}],'real_users':0,'observations':[],'results':[],'customer_approved':False,'engineering_validated':False,'threshold':None,'mode_history':[{'mode':'Empathize','status':'real_context_missing'},{'mode':'Define','status':'provisional_question'},{'mode':'Ideate','status':'two_authored_label_variants'},{'mode':'Prototype','status':'representation_plan_not_built'},{'mode':'Test','status':'planned_not_executed'}]}
def check(i):
 if i.get('binding')!=BIND:raise ValueError('binding_changed')
 if i.get('origin')!='constructed_teaching_plan'or i.get('real_users')!=0 or i.get('observations')or i.get('results')or i.get('customer_approved')or i.get('engineering_validated'):raise ValueError('unearned_learning_or_engineering_claim')
 if i.get('threshold')is not None:raise ValueError('threshold_invented')
 claim=i.get('learning_claim');proto=i.get('prototype')
 if claim not in CLAIM_NEEDS or proto not in CAPABILITIES:raise ValueError('unsupported_fixed_claim_or_prototype')
 if i.get('source_need')!=CLAIM_NEEDS[claim]['need']:raise ValueError('need_claim_mapping_mismatch')
 if i.get('declared_variable')!='label':raise ValueError('unsupported_variable_for_this_fixture')
 vs=i.get('variants',[])
 if len(vs)!=2 or {v.get('id')for v in vs}!={'V-A','V-B'}:raise ValueError('variant_identity_or_count_invalid')
 if any(set(v)!={'id','label','shape','position'}for v in vs):raise ValueError('variant_fields_changed')
 if any(not isinstance(v['label'],str)or not v['label'].strip()for v in vs):raise ValueError('label_missing')
 changed={k for k in ['label','shape','position']if vs[0][k]!=vs[1][k]}
 if changed!={'label'}:raise ValueError('comparison_does_not_isolate_declared_variable')
 if any(v['shape']!='same_card'or v['position']!='same_position'for v in vs):raise ValueError('control_definition_changed')
 if i.get('mode_history')!=plan['mode_history']:raise ValueError('mode_or_execution_status_changed')
 fits=CLAIM_NEEDS[claim]['required']in CAPABILITIES[proto]
 return {'binding':BIND,'learning_claim':claim,'prototype':proto,'declared_capability_match':fits,'match_scope':'fixed authored representation assumptions only; real adequacy not demonstrated','next_action':'plan_contextual_comprehension_observation'if fits else'return_to_research_question_or_representation','allowed_learning':'state_meaning_if_actual_task_research_later'if fits else None,'actual_findings':[],'actual_user_tests':0,'physical_performance':None,'status':'plan_only_not_ready_for_use_validation'}
put('01-学习目的与表示输入.json',plan)
a=check(plan)
b=copy.deepcopy(plan);b.update(learning_claim='internal_boundary_accuracy',source_need='N-T01',prototype='P-GEOMETRY-MOCK');other=check(b)
put('02-不同学习问题的模式与能力.json',{'state_question':a,'mechanism_question_input':b,'mechanism_question':other,'why_return':'代理表面几何不能自己证明真实组织边界；纸面理解也不能证明控制延迟或机械安全。','framework_note':'five modes are research practices, not mandatory one-pass stages','proposed_records_when_executed':['task','context','role','prototype_version','raw_observation','participant_words','intervention','interpretation','alternative_explanation']})
put('03-原型观察与修订空表.json',{'observations':[],'interpretations':[],'revisions':[],'invalidity_branches':['task_not_understood','representation_cannot_express_phenomenon','measurement_or_recording_failure','context_mismatch'],'generic_like_dislike_not_task_evidence':True})
cases=[]
def probe(name,kind,mut,expected):
 i=copy.deepcopy(plan);mut(i)
 try:o=check(i);r='matched_plan'if o['declared_capability_match']else'unmatched_return'
 except ValueError as e:o={'error':str(e)};r='rejected'
 assert r==expected,(name,r)
 cases.append({'name':name,'class':kind,'expected':expected,'actual':r,'input':i,'output':o})
probe('normal-label-understanding-plan','正常',lambda x:None,'matched_plan')
probe('missing-variant','缺材料',lambda x:x['variants'].pop(),'rejected')
probe('animation-is-not-comprehension','不适用',lambda x:x.update(prototype='P-ANIMATION'),'unmatched_return')
probe('identical-variants-no-comparison','边界',lambda x:x['variants'][1].update(label=x['variants'][0]['label']),'rejected')
probe('two-variables-changed','冲突',lambda x:x['variants'][1].update(position='other_position'),'rejected')
probe('proxy-not-internal-boundary','不适用',lambda x:x.update(learning_claim='internal_boundary_accuracy',source_need='N-T01',prototype='P-GEOMETRY-MOCK'),'unmatched_return')
probe('cannot-relabel-need-to-pass','冲突',lambda x:x.update(learning_claim='internal_boundary_accuracy'),'rejected')
probe('cannot-invent-users','边界',lambda x:x.update(real_users=5),'rejected')
probe('cannot-invent-positive-feedback','冲突',lambda x:x['results'].append('用户喜欢因此安全'),'rejected')
probe('history-not-completed-work','冲突',lambda x:x['mode_history'][-1].update(status='completed'),'rejected')
put('04-实际检查结果.json',{'executed':True,'passed':len(cases),'checks':cases,'real_user_tests':0,'scope':'fixed learning purpose/control-variable/capability-declaration checks only'})
transfer={'scenario':'DOC-HANDOFF-TEACH-003','origin':'constructed_desktop','question':'版本标记能否被识别','representation':'两张只改变版本标记文字的纸面资料卡','can_research_later':'人是否理解资料版本','cannot_claim':'数据库并发一致性、权限或真实协作效率已验证','observations':[],'next_mode_if_meaning_unclear':'return to understand context and define terminology'}
assert transfer['observations']==[]
put('05-迁移桌面检查.json',transfer)
print(json.dumps({'method':'R03','checks':len(cases),'state_plan':a['declared_capability_match'],'real_boundary_plan':other['declared_capability_match'],'actual_user_tests':0},ensure_ascii=False))
