"""ML-005 actual method MCP pilot. Human-curated demand brief + five real model steps."""
import asyncio,json,sys,os
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT,Engine,digest
from rubber_pilot_mcp import call
async def run():
 out=ROOT/'output/rubber-tapping-pilot';private=out/'private';task=json.loads((out/'task.json').read_text());brief=json.loads((out/'需求简报-作者整理.json').read_text());evidence=json.loads((private/'research-evidence.json').read_text());cases=json.loads((private/'case-evidence.json').read_text())
 selected={'case-479a7157f5e4d5eecce6c304','case-0205da2905f4ccacbbb38094','case-a81a5bd5f1f2e791d5e1371c','case-0290060f5fbcac9f3803c823','case-c1dd39efa2c949b7b81a8a58'}
 evidence += [e for e in cases if e['id'] in selected]
 if len(evidence)!=13:raise ValueError('expected_8_research_notes_and_5_case_excerpts')
 env={**os.environ,'METHOD_ENGINE_DB':str(private/'pilot.sqlite3')};artifacts=[];steps=[]
 if (out/'engine-report.json').exists():raise ValueError('existing_run_do_not_overwrite')
 async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env=env)) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   match=await call(s,'method_semantic_match',{'request_text':task['desired_outcome'],'context':{'research_demands':[r['text'] for r in brief['payload']['requirements']],'boundary':task['boundary']}})
   (out/'method-match.json').write_text(json.dumps(match,ensure_ascii=False,indent=2));print('real model method match saved',flush=True)
   created=await call(s,'method_run_create',{'task':task,'evidence':evidence})
   if created.get('status')=='blocked':raise ValueError(str(created))
   revision=0
   for node in created['plan']['nodes']:
    rid=node['node_id'];print(rid+': starting',flush=True)
    draft={'status':'author_curated_demand_not_model_generated','artifact':brief} if rid=='R48' else await call(s,'method_propose_artifact',{'method_id':rid,'task':task,'artifacts':artifacts,'evidence':evidence,'max_repairs':1})
    row={'method':rid,'draft':draft};steps.append(row)
    if draft['status']=='blocked':break
    saved=await call(s,'method_run_submit',{'run_id':created['run_id'],'expected_revision':revision,'key':'pilot-'+rid,'method_id':rid,'artifact':draft['artifact'],'evidence':evidence});row['submission']=saved
    if saved['status']=='blocked':break
    revision=saved['revision'];artifacts.append(draft['artifact'])
    (out/'engine-progress.json').write_text(json.dumps({'run_id':created['run_id'],'recorded':len(artifacts),'steps':steps},ensure_ascii=False,indent=2))
    print(rid+': recorded',flush=True)
 checks=[];prior=[]
 for rid,a in zip(('R48','R14','R17','R36','R44','R42'),artifacts):checks.append({'method':rid,'check':Engine().check_output(rid,a,task,prior,evidence)});prior.append(a)
 report={'status':'six_artifacts_recorded_pending_review' if len(artifacts)==6 else 'stopped_before_completion','run_id':created['run_id'],'task':task,'demand_packet_sha256':task['demand_packet_sha256'],'matching_proposal_separate_from_reference_execution_chain':True,'R48_origin':'author_curated_research_not_customer_confirmed','steps':steps,'all_six_checks':checks,'artifacts':artifacts,'evidence_ids':[e['id'] for e in evidence],'expert_certified':False,'engineering_validated':False,'case_transferability':'hypotheses_not_validated'}
 (out/'engine-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(report['status'],flush=True)
if __name__=='__main__':asyncio.run(run())
