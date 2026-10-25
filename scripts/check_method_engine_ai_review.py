"""Actual AI semantic review of corrected live draft, explicitly not expert approval."""
import asyncio
import json
import sqlite3
import sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT


async def main():
    base=ROOT/'output/method-engine-ML003'
    source=sorted((base/'live-revision').glob('*/report.json'),key=lambda f:f.stat().st_mtime)[-1]
    corrected=json.loads(source.read_text())
    if corrected['status']!='corrected_draft_pending_review':raise ValueError('no_corrected_draft')
    with sqlite3.connect(source.parent/'run.sqlite3') as db:
        task,plan=db.execute('SELECT task,plan FROM runs WHERE id=?',(corrected['run_id'],)).fetchone()
    task,plan=json.loads(task),json.loads(plan)
    args={'method_id':'R42','task':task,'artifact':corrected['proposal']['artifact'],
          'inputs':plan['inputs_snapshot']['artifacts'],'evidence':plan['inputs_snapshot']['evidence']}
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')])) as (r,w):
        async with ClientSession(r,w) as session:
            await session.initialize();result=await session.call_tool('method_review_artifact',args)
            if result.isError:raise ValueError(str(result.content))
            output=result.structuredContent or json.loads(result.content[0].text)
    assert output['expert_certified'] is False
    (base/'adversarial-review.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':output['status'],'expert_certified':False}))


if __name__=='__main__':asyncio.run(main())
