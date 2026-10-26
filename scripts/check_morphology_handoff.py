"""ML-008 positive assembly -> real MCP gate; assembly reader is explicitly injected.
No model quota, no submission, no expert/engineering assertion.
"""
import asyncio,json,sys,os
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_workbench_morphology import inputs,assemble
ROOT=Path(__file__).resolve().parents[1]

async def run():
    sample=json.loads((ROOT/'output/method-workbench-check/ml008/restart-state.json').read_text())
    state,evidence=sample['state'],sample['evidence']
    source=json.loads((ROOT/'output/method-workbench-check/ml007/host-continuation.json').read_text())['artifacts']['R17']['payload']
    stamp,prior,fm=inputs(state,evidence)
    parts={f['id']:{'function_id':f['id'],'input_fingerprint':stamp,'call_id':'host-fixture-'+f['id'],
                   'options':[o for o in source['options'] if o['function_id']==f['id']][1:3],
                   'unknowns':['Host-derived fixture only, not real model output']} for f in fm['payload']['functions']}
    def fake(prompt,folder):
        return {'combinations':[{'id':'FIXTURE-C'+str(i),'option_ids':[p['options'][i]['id'] for p in parts.values()],'status':'unknown','reason':'injected fixture, not a model-generated recommendation'} for i in (0,1)],'unknowns':['fixture only']}
    out=assemble(state,evidence,parts,ROOT/'output/method-workbench-check/ml008/assembly-fixture',reader=fake)
    assert out['model_mode']=='injected_reader_not_real_model'
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env={**os.environ,'METHOD_ENGINE_DB':str(ROOT/'output/method-workbench-check/ml008/engine.sqlite')})
    async with stdio_client(params) as(r,w):
        async with ClientSession(r,w) as s:
            await s.initialize()
            r=await s.call_tool('method_check_artifact',{'method_id':'R17','task':state['task'],'artifact':out['artifact'],'inputs':prior,'evidence':evidence})
            assert not r.isError
            checked=r.structuredContent or json.loads(r.content[0].text)
            assert checked['status']!='blocked',checked
    print(json.dumps({'assembly_mode':'injected_reader_not_real_model','function_count':14,'options':28,'combinations':2,'real_MCP_check':checked['status'],'model_calls':0,'submitted':False,'expert_certified':False}))

if __name__=='__main__':asyncio.run(run())
