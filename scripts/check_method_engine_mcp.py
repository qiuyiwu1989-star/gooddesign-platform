"""Actual two-server SDK interoperability test; authored artifacts are not generated expert results."""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
from method_engine_contracts import CONTRACT_VERSION
from method_case_adapter import read_case
sys.path.insert(0, str(ROOT/'tests'))
from method_engine_fixtures import teaching_task, teaching_artifacts


async def call(session, name, args):
    result = await session.call_tool(name, args)
    if result.isError: raise ValueError(name+': '+str(result.content))
    return result.structuredContent or json.loads(result.content[0].text)


async def run():
    checks, evidence = [], []
    def check(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})
        if not ok: raise ValueError(name)
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/archive_mcp.py')])) as (r,w):
        async with ClientSession(r,w) as case:
            init = await case.initialize()
            sources = await call(case,'gd_list_sources',{'project_id':'2025-00','limit':20})
            selected = next(x for x in sources['data'] if x.get('chunk_count',0)>0)
            normalized = await read_case(case,'2025-00',selected['id'])
            evidence = normalized['evidence']
            check('actual_case_mcp_frozen_evidence',bool(evidence) and all(x['source_revision'] and x['locator'] for x in evidence))
    with tempfile.TemporaryDirectory(prefix='method-mcp-',dir=ROOT/'output') as temp:
        env={**os.environ,'METHOD_ENGINE_DB':str(Path(temp)/'runs.db')}
        params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')],env=env)
        async with stdio_client(params) as (r,w):
            async with ClientSession(r,w) as method:
                method_init=await method.initialize()
                names={x.name for x in (await method.list_tools()).tools}
                check('method_tools_discovered',len(names)==18)
                resources=await method.list_resources()
                check('host_workflow_resource',any(str(x.uri)=='method://workflow' for x in resources.resources))
                prepared=await call(method,'method_prepare_application_request',{'request':{'task_id':'APP-TEST','title':'hold safely','scenario_type':'simulated','needs':['hold a part']},'object_name':'clamp','boundary':'teaching only'})
                app_run=await call(method,'method_run_create',{'task':prepared['task']})
                envelope=await call(method,'method_application_result',{'run_id':app_run['run_id']})
                check('application_request_result_bridge',envelope['source_request']['sha256']==prepared['source_request_sha256'] and not envelope['writeback_performed'])
                task=teaching_task();artifacts=teaching_artifacts()
                matched=await call(method,'method_match',{'task':task})
                check('explicit_match',matched['recommended']==['R48'])
                blocked=await call(method,'method_plan',{'task':{}})
                check('missing_context_blocked',blocked['status']=='blocked')
                run=await call(method,'method_run_create',{'task':task})
                check('six_node_plan',len(run['plan']['nodes'])==6)
                revision=0
                for rid,artifact in artifacts.items():
                    checked=await call(method,'method_check_artifact',{'method_id':rid,'artifact':artifact,'evidence':evidence,'task':task})
                    check('artifact_'+rid,checked['status']!='blocked')
                    result=await call(method,'method_run_submit',{'run_id':run['run_id'],'expected_revision':revision,'key':'submit-'+rid,'method_id':rid,'artifact':artifact,'evidence':evidence})
                    revision=result['revision']
                check('all_artifacts_recorded',revision==6)
                rejected=await call(method,'method_quality_report',{'packet':{'level':'concept'}})
                check('no_expert_certification_without_review',rejected['status']=='blocked' and not rejected['expert_certified'])
        async with stdio_client(params) as (r,w):
            async with ClientSession(r,w) as resumed:
                await resumed.initialize()
                state=await call(resumed,'method_run_get',{'run_id':run['run_id']})
                check('server_restart_persistence',state['revision']==6 and len(state['submissions'])==6)
    report={'status':'passed','contract_version':CONTRACT_VERSION,'checks':checks,'method_tool_count':len(names),'case_protocol':init.protocolVersion,'method_protocol':method_init.protocolVersion,
            'source_refs':[{k:e.get(k) for k in ('project_id','source_id','source_revision','source_sha256','chunk_id','locator','text_sha256','truncated')} for e in evidence],
            'analysis_mode':'authored_teaching_fixture_not_general_llm_inference','expert_certified':False,
            'scope':'actual_stdio_mcp_retrieval_and_execution_contracts_not_engineering_validation'}
    dest=ROOT/'output/method-engine-ML003'/('v'+CONTRACT_VERSION);dest.mkdir(parents=True,exist_ok=True)
    (dest/'mcp-integration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','checks':len(checks),'report':str(dest/'mcp-integration.json')},ensure_ascii=False))


if __name__=='__main__':asyncio.run(run())
