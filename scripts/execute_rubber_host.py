"""Real deterministic MCP execution of Host Agent-authored rubber research artifacts."""
import asyncio,json,sys,os,copy
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT,digest
from rubber_pilot_mcp import call
async def run():
 out=ROOT/'output/rubber-tapping-pilot'
 if (out/'engine-report.json').exists():raise ValueError('existing_research_run_create_new_version_instead_of_overwriting')
 private=out/'private';task=json.loads((out/'task.json').read_text());artifacts=json.loads((out/'Agent推理产物.json').read_text())['artifacts'];intake=json.loads((out/'需求包.json').read_text())
 assert digest(intake)==task['demand_packet_sha256']
 evidence=json.loads((private/'research-evidence.json').read_text());cases=json.loads((private/'case-evidence.json').read_text());ids={'case-479a7157f5e4d5eecce6c304','case-0205da2905f4ccacbbb38094','case-a81a5bd5f1f2e791d5e1371c','case-0290060f5fbcac9f3803c823','case-c1dd39efa2c949b7b81a8a58'};evidence += [e for e in cases if e['id'] in ids]
 assert len(evidence)==13
 params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env={**os.environ,'METHOD_ENGINE_DB':str(private/'host-run.sqlite3')});checks=[];prior=[]
 async with stdio_client(params) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize();matched=await call(s,'method_match',{'task':task});plan=await call(s,'method_plan',{'task':task});created=await call(s,'method_run_create',{'task':task,'evidence':evidence});rev=0
   if created['status']=='blocked':raise ValueError(str(created))
   for rid,a in artifacts.items():
    ready=await call(s,'method_check_inputs',{'method_id':rid,'task':task,'artifacts':prior,'evidence':evidence})
    checked=await call(s,'method_check_artifact',{'method_id':rid,'artifact':a,'task':task,'inputs':prior,'evidence':evidence})
    if checked['status']=='blocked' or ready['status']=='blocked':raise ValueError(str({'rid':rid,'ready':ready,'checked':checked}))
    saved=await call(s,'method_run_submit',{'run_id':created['run_id'],'expected_revision':rev,'key':'host-'+rid,'method_id':rid,'artifact':a,'evidence':evidence})
    if saved['status']=='blocked':raise ValueError(str(saved))
    rev=saved['revision'];checks.append({'method':rid,'input_status':ready['status'],'check':checked,'submission':saved});prior.append(a)
   bad=copy.deepcopy(artifacts['R36']);bad['payload']['criteria'][0]['requirement_ids']=[]
   negative=await call(s,'method_check_artifact',{'method_id':'R36','artifact':bad,'task':task,'inputs':[artifacts[k] for k in ['R48','R14','R17']],'evidence':evidence})
   assert negative['status']=='blocked'
   gate=await call(s,'method_quality_report',{'packet':{'level':'concept'}});assert gate['status']=='blocked' and not gate['expert_certified']
 async with stdio_client(params) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize();restored=await call(s,'method_run_get',{'run_id':created['run_id']});assert restored['revision']==6
 report={'status':'six_host_agent_artifacts_recorded_and_restored_pending_review','mode':'Host_Agent_reasoning_plus_real_method_MCP_not_backend_model_generation','task':task,'run_id':created['run_id'],'demand_packet_sha256':digest(intake),'rule_match':matched,'reference_plan':plan,'checks':checks,'omitted_hard_constraint_negative':negative,'quality_gate':gate,'restart_revision':restored['revision'],'backend_model_attempt':{'status':'failed_429_then_180s_timeout','call_id':'match-51584e09ea9842f29d592f8db62239b0','automatic_model_steps_completed':0},'case_evidence_count':5,'public_research_note_count':8,'expert_certified':False,'engineering_validated':False}
 (out/'engine-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report['status'])
if __name__=='__main__':asyncio.run(run())
