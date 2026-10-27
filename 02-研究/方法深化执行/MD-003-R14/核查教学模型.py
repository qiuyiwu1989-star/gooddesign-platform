"""Declared structure/lineage checks only. Does not infer physical/semantic sufficiency."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parent
class Reject(ValueError):pass
def check(d):
 u=d.get('upstream',{})
 if u.get('path'):
  source=P.parents[2]/u['path'];raw=source.read_bytes()
  if hashlib.sha256(raw).hexdigest()!=u.get('sha256'):raise Reject('upstream_sha_changed')
  if json.loads(raw)['problem_id']!=d['problem_id']:raise Reject('upstream_problem_mismatch')
 elif u.get('kind')!='independent_constructed_context' or u.get('problem_id')!=d['problem_id']:
  raise Reject('unbound_upstream')
 if d.get('mode')!='constructed_teaching_not_customer_evidence':raise Reject('unsupported_execution_scope')
 if d.get('customer_approved') or d.get('engineering_validated'):raise Reject('unsubstantiated_approval')
 fs=d['functions'];ids=[f['id']for f in fs]
 if len(ids)!=len(set(ids)):raise Reject('duplicate_function_id')
 needs={r['need_id']for r in d['coverage']};known=set(ids)|set(d['external_entities'])
 for f in fs:
  if not set(f['parent_need_ids'])<=needs:raise Reject('dangling_need')
  if f['verb_object'].startswith(('配置','安装','选用')):raise Reject('component_wording_requires_review')
 for c in d['coverage']:
  if not set(c['function_ids'])<=set(ids):raise Reject('dangling_coverage_function')
  if c['status']!='research_allocation_not_satisfaction':raise Reject('coverage_not_satisfaction')
 ii=[x['id']for x in d['interfaces']]
 if len(ii)!=len(set(ii)):raise Reject('duplicate_interface_id')
 for i in d['interfaces']:
  if i['origin']not in known or i['destination']not in known:raise Reject('dangling_interface_endpoint')
  if i.get('producer_unit')!=i.get('consumer_unit') and not i.get('conversion'):raise Reject('declared_unit_conflict')
  if i['threshold']is not None:raise Reject('unapproved_target_injected')
 for u in d['unknowns']:
  if u['value']is not None:raise Reject('unknown_filled')
 for s in d['scenarios']:
  if not set(s['function_ids'])<=set(ids)or not set(s['interface_ids'])<=set(ii):raise Reject('dangling_scenario')
 if d['scope'].startswith('workhead'):
  if not any(s['kind']=='stale_feedback_or_loss'for s in d['scenarios']):raise Reject('missing_recovery_scenario')
  if not any(i['origin']=='EXT-POWER'for i in d['interfaces']):raise Reject('declared_boundary_energy_missing')
 return {'status':'accepted_for_research_only','function_count':len(fs),'interface_count':len(ii),'unknown_count':len(d['unknowns']),'global_engineering_coverage':False,'semantic_sufficiency':'not_automatically_checked','approval':False}
if __name__=='__main__':
 base=json.loads((P/'教学包/01-功能与接口输入-v0.1.0.json').read_text());cases=[]
 def run(name,category,d,expected):
  ip=P/'教学包/检查输入'/(name+'.json');ip.parent.mkdir(exist_ok=True);ip.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
  try:r=check(d);actual='accepted'
  except Reject as e:r={'status':'rejected','reason':str(e)};actual=str(e)
  assert actual==expected,(name,actual,expected)
  cases.append({'id':name,'category':category,'input':str(ip.relative_to(P)),'input_sha256':hashlib.sha256(ip.read_bytes()).hexdigest(),'expected':expected,'actual':actual,'passed':True,'output':r})
 run('normal-reference-consistency','normal',base,'accepted')
 d=copy.deepcopy(base);d['scenarios']=[s for s in d['scenarios']if s['kind']!='stale_feedback_or_loss'];run('missing-recovery','missing_material',d,'missing_recovery_scenario')
 d=copy.deepcopy(base);d['mode']='certified_production_control';run('unsupported-engineering-mode','not_applicable',d,'unsupported_execution_scope')
 d=copy.deepcopy(base);d['functions'][1]['verb_object']='配置传感器';run('component-instead-of-function','boundary',d,'component_wording_requires_review')
 d=copy.deepcopy(base);d['interfaces'][1].update(producer_unit='mm',consumer_unit='m',conversion=None);run('declared-units-conflict','conflict',d,'declared_unit_conflict')
 d=copy.deepcopy(base);d['unknowns'][0]['value']=0;run('unknown-zero-injection','boundary',d,'unknown_filled')
 d=copy.deepcopy(base);d['external_entities'].remove('EXT-TREE');run('missing-physical-boundary','missing_material',d,'dangling_interface_endpoint')
 d=copy.deepcopy(base);d['problem_id']='OTHER';run('upstream-problem-mismatch','conflict',d,'upstream_problem_mismatch')
 # Different, purely informational task; preserve research-only state and no physical claim.
 d=copy.deepcopy(base);d['problem_id']='DOC-TEACH-001';d['scope']='document information handoff only';d['upstream']={'kind':'independent_constructed_context','problem_id':'DOC-TEACH-001','customer_approved':False};d['unknowns']=[{'id':'U-DOC1','text':'真实文档可读性、权限与保存能力','value':None,'origin':'platform_document_teaching'}];d['functions']=[{'id':'FD1','verb_object':'接收文档','parent_need_ids':['ND1']},{'id':'FD2','verb_object':'保存文档','parent_need_ids':['ND1']}];d['coverage']=[{'need_id':'ND1','function_ids':['FD1','FD2'],'status':'research_allocation_not_satisfaction'}];d['external_entities']=['EXT-USER','EXT-STORE'];d['interfaces']=[{'id':'ID1','origin':'EXT-USER','destination':'FD1','threshold':None},{'id':'ID2','origin':'FD1','destination':'FD2','threshold':None},{'id':'ID3','origin':'FD2','destination':'EXT-STORE','threshold':None}];d['scenarios']=[{'id':'SD1','kind':'declared_normal','function_ids':['FD1','FD2'],'interface_ids':['ID1','ID2','ID3']}]
 run('cross-context-document','transfer',d,'accepted')
 (P/'教学包/05-实际结构检查.json').write_text(json.dumps({'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'actual local checks of declared structure, not semantic or physical validation','cases':cases,'passed':len(cases),'engineering_validated':False},ensure_ascii=False,indent=2)+'\n')
 print('R14 checks',len(cases),'PASS')
