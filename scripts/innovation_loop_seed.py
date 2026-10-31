"""Explicitly seed isolated proposal tasks, never source project archives."""
from innovation_loop_store import LoopStore
from innovation_loop_tasks import IDS,load_task

def seed(store=None):
 s=store or LoopStore();saved=[]
 for ident in IDS:
  task=load_task(ident);rq=task['requirement'];s.put('requirement',rq)
  for route in task['routes']:
   s.put('route',route)
   claim={'schema_version':'0.1.0','id':route['id']+'-CLAIM','revision':1,'route_ref':{'id':route['id'],'revision':route['revision']},'text':route['mechanism'],'nature':'hypothesized','basis':'既有平台研究整理后的待验证路线；不是客户确认或性能事实','source_refs':task['source_refs']}
   s.put('claim',claim)
  for action in task['actions']:s.put('action',action)
  saved.append({'task_id':ident,'requirement_id':rq['id'],'status':'proposal_not_customer_confirmed'})
 return saved
if __name__=='__main__':
 import json
 print(json.dumps(seed(),ensure_ascii=False,indent=2))
