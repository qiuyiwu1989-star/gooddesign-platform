from pathlib import Path
import json,copy
P=Path(__file__).resolve().parent
REG={'FM':'main','FR':'auxiliary','FC':'auxiliary','FS':'auxiliary'}
DEPS=[['FR','FM','reference_support'],['FC','FM','continuity_support'],['FS','FM','abnormal_recovery_support']]
base={'id':'WB05-FUNCTION-TEACH-001','origin':'platform_function_dependency_fixture_not_author_rulebook','functions':[{'id':'FM','role':'main','action':'produce controlled action','owner_role':'working_head_research'},{'id':'FR','role':'auxiliary','action':'maintain reference','owner_role':'reference_research'},{'id':'FC','role':'auxiliary','action':'clear interfering residue','owner_role':'service_research'},{'id':'FS','role':'auxiliary','action':'stop and support recovery','owner_role':'control_research'}],'dependencies':DEPS,'necessary_in_constructed_task':list(REG),'takeovers':[],'resource_costs':None,'customer_approved':False,'engineering_validated':False}
def check(d):
 if d.get('origin')!=base['origin']or d.get('customer_approved')is not False or d.get('engineering_validated')is not False:raise ValueError('scope/approval')
 if d.get('dependencies')!=DEPS or d.get('necessary_in_constructed_task')!=list(REG):raise ValueError('necessity/support graph erased')
 fs=d.get('functions');ts=d.get('takeovers')
 if type(fs)is not list or type(ts)is not list:raise ValueError('explicit function/takeover lists required')
 ids=[f.get('id')for f in fs]
 if len(ids)!=len(set(ids))or not set(ids)<=set(REG):raise ValueError('function identities')
 for f in fs:
  if f.get('role')!=REG[f['id']]or any(type(f.get(k))is not str or not f[k].strip()for k in ['action','owner_role']):raise ValueError('role/meaning/responsibility missing')
 missing=set(REG)-set(ids);covered=set();queue=[]
 for t in ts:
  if t.get('function_id')not in missing or t['function_id']in covered:raise ValueError('takeover does not cover unique removed function')
  if type(t.get('new_owner_role'))is not str or not t['new_owner_role'].strip():raise ValueError('takeover role missing')
  if t.get('evidence')!='proposed_not_validated'or t.get('user_burden')!='unknown':raise ValueError('takeover or burden evidence invented')
  covered.add(t['function_id']);queue.append(t)
 uncovered=sorted(missing-covered)
 return {'status':'necessary_function_lost'if uncovered else'takeover_still_unknown'if queue else'declared_support_preserved_only','uncovered':uncovered,'responsibility_changes':queue,'optimization_benefit':None,'engineering_pass':False,'cost':None,'limit':'auxiliary is a classification, not permission to delete necessary support'}
cases=[]
def add(n,d,e):
 r=check(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常主辅支撑',base,'declared_support_preserved_only')
x=copy.deepcopy(base);x['functions']=[f for f in x['functions']if f['id']!='FC'];add('删辅助清洁损失必要作用',x,'necessary_function_lost')
x['takeovers']=[{'function_id':'FC','new_owner_role':'operator_research_role','evidence':'proposed_not_validated','user_burden':'unknown'}];add('转交人工仍未知且责任变化',x,'takeover_still_unknown')
x=copy.deepcopy(base);x['functions'][2]['owner_role']='';
try:check(x);raise AssertionError('missing owner accepted')
except ValueError as e:cases.append({'name':'缺责任资料','actual':'rejected','reason':str(e),'passed':True})
for n,mut in [('把辅助改可删除不适用',lambda d:d['functions'][2].update(role='optional')),('删支撑边界',lambda d:d.update(dependencies=[])),('伪成本节省冲突',lambda d:d.update(engineering_validated=True))]:
 x=copy.deepcopy(base);mut(x)
 try:check(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x['id']='DOC-FUNCTION-TEACH';x['functions'][0]['action']='deliver correct version';x['functions'][2]['action']='remove stale version ambiguity';add('资料交接不同情境支撑',x,'declared_support_preserved_only')
for n,d in [('01-作用必要支撑输入.json',base),('02-优化前后责任实际检查.json',{'cases':cases,'count':len(cases),'resource_ledger':'quantities/shifted labor unknown; cannot rank or call deletion beneficial','meaning_scope':'necessity is an explicit teaching assumption, not customer confirmation'})]:(P/'教学包'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');print(len(cases),'passed')
