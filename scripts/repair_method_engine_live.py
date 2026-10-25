"""Recheck old teaching run, keep it unchanged, and create a new single-node revision run."""
import asyncio
import json
import os
import sqlite3
import sys
import uuid
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import Engine, ROOT


async def call(session,name,args):
    result=await session.call_tool(name,args)
    if result.isError:raise ValueError(str(result.content))
    return result.structuredContent or json.loads(result.content[0].text)


async def main():
    base=ROOT/'output/method-engine-ML003'
    source=sorted((base/'live-chain').glob('*/report.json'),key=lambda p:p.stat().st_mtime)[-1]
    old=json.loads(source.read_text());engine=Engine()
    with sqlite3.connect(source.parent/'run.sqlite3') as db:
        rows=[json.loads(x[0]) for x in db.execute('SELECT data FROM submissions ORDER BY rowid')]
    ev={e['id']:e for row in rows for e in row['evidence']}
    evidence=list(ev.values());checks={r['method']:engine.check_artifact(r['method'],r['artifact'],evidence,old['task']) for r in rows}
    (source.parent/'post-review-recheck.json').write_text(json.dumps({'status':'requires_revision' if any(x['status']=='blocked' for x in checks.values()) else 'current_checks_passed','checks':checks,'expert_certified':False},ensure_ascii=False,indent=2)+'\n')
    inputs=[x['artifact'] for x in rows if x['method']!='R42']
    dest=base/'live-revision'/('run-'+uuid.uuid4().hex);dest.mkdir(parents=True)
    env={**os.environ,'METHOD_ENGINE_DB':str(dest/'run.sqlite3')}
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env=env)) as (r,w):
        async with ClientSession(r,w) as session:
            await session.initialize()
            created=await call(session,'method_run_create',{'task':old['task'],'target':'R42','artifacts':inputs,'evidence':evidence})
            if created['status']=='blocked':raise ValueError(json.dumps(created))
            proposal=await call(session,'method_propose_artifact',{'method_id':'R42','task':old['task'],'artifacts':inputs,'evidence':evidence,'max_repairs':1})
            saved=None
            if proposal['status']!='blocked':
                saved=await call(session,'method_run_submit',{'run_id':created['run_id'],'expected_revision':0,'key':'corrected-R42','method_id':'R42','artifact':proposal['artifact'],'evidence':evidence})
    report={'status':'corrected_draft_pending_review' if saved and saved.get('status')!='blocked' else 'correction_blocked',
            'previous_report':str(source),'old_run_unchanged':True,'run_id':created['run_id'],'reused_artifact_ids':[a['artifact_id'] for a in inputs],
            'proposal':proposal,'submission':saved,'expert_certified':False,'engineering_validated':False}
    (dest/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'report':str(dest/'report.json')}))


if __name__=='__main__':asyncio.run(main())
