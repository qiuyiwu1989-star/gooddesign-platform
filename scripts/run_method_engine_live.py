"""Live model + case MCP + method MCP teaching run. Stops on failure; never substitutes fixtures."""
import argparse
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
from method_case_adapter import read_case


async def call(session,name,args):
    result=await session.call_tool(name,args)
    if result.isError:raise RuntimeError(name+': '+str(result.content))
    return result.structuredContent or json.loads(result.content[0].text)


async def run():
    dest=ROOT/'output/method-engine-ML003/live-chain'/('run-'+uuid.uuid4().hex)
    dest.mkdir(parents=True)
    task={'task_id':'LIVE-TEACH-CLAMP','revision':'t1','object':'bench clamp','desired_outcome':'hold a workpiece without damage',
          'boundary':'teaching concept and test planning only; customer load, material, geometry and damage criterion unknown',
          'stage':'frame','delivery_level':'concept',
          'source_policy':'Lunar sampling case is provided as a deliberately different environment; do not transfer its parameters or cite it as proof of clamp performance.'}
    evidence=[]
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/archive_mcp.py')])) as (r,w):
        async with ClientSession(r,w) as case:
            await case.initialize()
            sources=await call(case,'gd_list_sources',{'project_id':'2025-00','limit':20})
            source=next(x for x in sources['data'] if x.get('chunk_count',0)>0)
            evidence=(await read_case(case,'2025-00',source['id']))['evidence']
    env={**os.environ,'METHOD_ENGINE_DB':str(dest/'run.sqlite3')}
    artifacts=[];steps=[]
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env=env)
    async with stdio_client(params) as (r,w):
        async with ClientSession(r,w) as method:
            await method.initialize()
            created=await call(method,'method_run_create',{'task':task})
            revision=0
            for node in created['plan']['nodes']:
                rid=node['node_id'];print(rid+': model call',flush=True)
                try:
                    draft=await call(method,'method_propose_artifact',{'method_id':rid,'task':task,'artifacts':artifacts,'evidence':evidence,'max_repairs':1})
                except Exception as exc:
                    steps.append({'method':rid,'status':'model_or_protocol_error','error':type(exc).__name__+': '+str(exc)})
                    break
                row={'method':rid,'draft_status':draft['status'],'call_id':draft.get('call_id'),'check':draft.get('check')}
                if draft['status']=='blocked':
                    steps.append(row);break
                submitted=await call(method,'method_run_submit',{'run_id':created['run_id'],'expected_revision':revision,'key':'model-'+rid,
                    'method_id':rid,'artifact':draft['artifact'],'evidence':evidence})
                row['submission']=submitted;steps.append(row)
                if submitted.get('status')=='blocked':break
                revision=submitted['revision'];artifacts.append(draft['artifact'])
                (dest/'progress.json').write_text(json.dumps({'completed_nodes':len(artifacts),'steps':steps},ensure_ascii=False,indent=2)+'\n')
                print(rid+': recorded draft',flush=True)
            state=await call(method,'method_run_get',{'run_id':created['run_id']})
    report={'status':'six_drafts_recorded_pending_review' if len(artifacts)==6 else 'stopped_before_completion',
        'task':task,'run_id':created['run_id'],'steps':steps,'artifacts':artifacts,
        'evidence_refs':[{k:e.get(k) for k in ('project_id','source_id','source_revision','locator','text_sha256')} for e in evidence],
        'case_transferability':'not_established','expert_certified':False,'engineering_validated':False,
        'mode':'actual_model_calls_over_method_mcp_with_actual_case_mcp_retrieval','persisted_revision':state['revision']}
    (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(dest/'report.json')},ensure_ascii=False),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live',action='store_true',help='Explicitly allow up to twelve real model calls (six nodes, one repair each).')
    if not parser.parse_args().live:parser.error('--live is required; this command consumes real model quota')
    asyncio.run(run())
