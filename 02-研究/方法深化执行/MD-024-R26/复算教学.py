from pathlib import Path
import json,copy
P=Path(__file__).resolve().parent
def check(d):
 if d['customer_approved']is not False:raise ValueError('research only')
 fs=d['original_functions'];ps=d['redistribution'];ids={x['id']for x in fs}
 if len(ids)!=len(fs)or {x['function_id']for x in ps}!=ids or len(ps)!=len(fs):return {'status':'incomplete_function_closure'}
 unresolved=[]
 for x in ps:
  if x['route']not in ['A','B','C']:raise ValueError('unknown trimming route')
  if x['route']=='A':
   if x.get('object_removed')is not True:unresolved.append({'function':x['function_id'],'reason':'object not established removed; cannot just delete useful function'})
  elif not x.get('new_carrier')or x.get('takeover_evidence')!='independent_constructed_assumption':unresolved.append({'function':x['function_id'],'reason':'takeover not evidenced even for teaching assumption'})
  if x.get('engineering_validated')is not False:raise ValueError('no real engineering evidence in this packet')
 return {'status':'unresolved_function_queue'if unresolved else'redistribution_research_candidate','unresolved':unresolved,'physical_takeover_validated':False,'required_next':['force/time/interface coverage','failure and maintenance','burden transfer']}
base={'id':'R26-FIXTURE-TEACH-001','customer_approved':False,'removed_component':'dedicated release actuator (hypothetical)','original_functions':[{'id':'F01','action':'withdraw moving contact'},{'id':'F02','action':'report return state'},{'id':'F03','action':'keep withdrawal after primary power loss'}],'redistribution':[{'function_id':'F01','route':'C','new_carrier':'existing preload element','takeover_evidence':'independent_constructed_assumption','engineering_validated':False},{'function_id':'F02','route':'C','new_carrier':None,'takeover_evidence':'unknown','engineering_validated':False},{'function_id':'F03','route':'B','new_carrier':'moving member self-return behavior','takeover_evidence':'unknown','engineering_validated':False}]}
cases=[]
def add(n,d,e):
 r=check(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
x=copy.deepcopy(base)
for a in x['redistribution']:a.update(new_carrier='declared teaching carrier',takeover_evidence='independent_constructed_assumption')
add('正常构造分派仍非工程通过',x,'redistribution_research_candidate')
add('缺接管证据',base,'unresolved_function_queue')
x=copy.deepcopy(base);x['redistribution'][0].update(route='A',object_removed=False);add('对象仍需不适用A',x,'unresolved_function_queue')
x=copy.deepcopy(base);x['redistribution'].pop();add('删末项边界',x,'incomplete_function_closure')
x=copy.deepcopy(base);x['redistribution'][2].update(route='A',object_removed=False);add('失能作用被删除冲突',x,'unresolved_function_queue')
x={'id':'DOC-ROUTER-TEACH-001','customer_approved':False,'removed_component':'separate notification relay','original_functions':[{'id':'FD01','action':'notify recipient'},{'id':'FD02','action':'retain delivery receipt'}],'redistribution':[{'function_id':'FD01','route':'C','new_carrier':'existing event service','takeover_evidence':'independent_constructed_assumption','engineering_validated':False},{'function_id':'FD02','route':'C','new_carrier':None,'takeover_evidence':'unknown','engineering_validated':False}]};add('信息服务迁移仍有回执缺口',x,'unresolved_function_queue')
(P/'教学包/01-部件作用输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n')
(P/'教学包/02-三路径及实际检查.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'complete declared useful-function IDs and explicit takeover hypotheses only; no semantic or physical proof'},ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
