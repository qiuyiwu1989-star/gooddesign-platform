"""Explicit live migration: reuse three unchanged actual drafts; regenerate comparison and downstream plans."""
import argparse
import asyncio
import json
import os
import sqlite3
import sys
import uuid
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT, Engine
from method_engine_contracts import CONTRACT_VERSION


async def call(session,name,args):
    result=await session.call_tool(name,args)
    if result.isError:raise ValueError(name+': '+str(result.content))
    return result.structuredContent or json.loads(result.content[0].text)


async def run(source):
    old=json.loads(source.read_text());task=old['task']
    with sqlite3.connect('file:'+str(source.parent/'run.sqlite3')+'?mode=ro',uri=True) as db:
        rows=[json.loads(r[0]) for r in db.execute('SELECT data FROM submissions WHERE run_id=? ORDER BY rowid',(old['run_id'],))]
    upstream=[r['artifact'] for r in rows if r['method'] in {'R48','R14','R17'}]
    if len(upstream)!=3:raise ValueError('three_original_model_drafts_required')
    evidence=list({e['id']:e for row in rows for e in row['evidence']}.values())
    dest=ROOT/'output/method-engine-ML003'/('v'+CONTRACT_VERSION)/('run-'+uuid.uuid4().hex);dest.mkdir(parents=True)
    env={**os.environ,'METHOD_ENGINE_DB':str(dest/'run.sqlite3')};steps=[];artifacts=list(upstream)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env=env)) as (r,w):
        async with ClientSession(r,w) as session:
            await session.initialize();created=await call(session,'method_run_create',{'task':task,'artifacts':artifacts,'evidence':evidence})
            if created.get('status')=='blocked':raise ValueError(str(created))
            revision=0
            for node in created['plan']['nodes']:
                rid=node['node_id'];print(rid+': actual model call',flush=True)
                draft=await call(session,'method_propose_artifact',{'method_id':rid,'task':task,'artifacts':artifacts,'evidence':evidence,'max_repairs':1})
                step={'method':rid,'draft':draft};steps.append(step)
                if draft['status']=='blocked':break
                saved=await call(session,'method_run_submit',{'run_id':created['run_id'],'expected_revision':revision,'key':'new-'+rid,'method_id':rid,'artifact':draft['artifact'],'evidence':evidence})
                step['submission']=saved
                if saved['status']=='blocked':break
                revision=saved['revision'];artifacts.append(draft['artifact'])
                print(rid+': recorded draft',flush=True)
    engine=Engine();checks=[];prior=[]
    for rid,artifact in zip(('R48','R14','R17','R36','R44','R42'),artifacts):
        checked=engine.check_output(rid,artifact,task,prior,evidence);checks.append({'method':rid,'check':checked});prior.append(artifact)
    report={'status':'six_artifacts_cross_checked_pending_domain_review' if len(artifacts)==6 and all(x['check']['status']!='blocked' for x in checks) else 'incomplete_or_blocked',
            'contract_version':CONTRACT_VERSION,'task':task,'run_id':created['run_id'],'source_report':str(source),
            'reused_prior_model_artifacts':[a['artifact_id'] for a in upstream],'new_model_steps':steps,'all_six_checks':checks,
            'artifacts':artifacts,'expert_certified':False,'engineering_validated':False}
    (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(str(dest/'report.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--source-report',type=Path,required=True);args=p.parse_args()
    if not args.live:raise ValueError('explicit_live_flag_required_model_quota')
    asyncio.run(run(args.source_report.resolve()))
