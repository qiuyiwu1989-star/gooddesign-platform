"""ML-006 actual stdio MCP bridge; deterministic reads and explicit single-node model generation."""
import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]


async def main():
    request = json.load(sys.stdin)
    action = request['action']
    script = 'archive_mcp.py' if action in ('case_search','case_sources','case_evidence') else 'method_engine_mcp.py'
    env = dict(os.environ)
    if script == 'method_engine_mcp.py':
        env['METHOD_ENGINE_DB'] = request['db']
    async with stdio_client(StdioServerParameters(command=sys.executable, args=[str(ROOT / 'scripts' / script)], env=env)) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            async def call(name, args):
                result = await session.call_tool(name, args)
                if result.isError:
                    raise ValueError('MCP工具返回错误')
                return result.structuredContent or json.loads(result.content[0].text)
            if action == 'case_search':
                result = await call('gd_search_projects', {'query': request['query'], 'limit': 12})
            elif action == 'case_sources':
                result = await call('gd_list_sources', {'project_id': request['project_id'], 'limit': 20})
            elif action == 'case_evidence':
                response = await call('gd_read_evidence', {'project_id': request['project_id'], 'source_id': request['source_id'], 'offset': 0, 'limit': 1, **({'chunks_sha256':request['chunks_sha256']} if request.get('chunks_sha256') else {})})
                from method_case_adapter import normalize
                result = normalize(request['project_id'], request['source_id'], response)
            elif action in ('propose','submit'):
                from method_workbench_execution import alignment
                state = await call('method_run_get', {'run_id': request['run_id']})
                prior = [x['artifact'] for x in state['submissions']]
                done = {x['method'] for x in state['submissions']}
                node = next((n for n in state['plan']['nodes'] if n['node_id'] not in done), None)
                if not node or node['node_id'] != request['method'] or state['revision'] != request['expected_revision']:
                    raise ValueError('运行版本或当前步骤已改变，请刷新')
                method, task, evidence = request['method'], state['task'], request.get('evidence', [])
                if action == 'propose':
                    from method_engine_contracts import META
                    relevant = [a for a in prior if a['type'] in META[method]['requires']]
                    result = await call('method_propose_artifact', {'method_id': method, 'task': task, 'artifacts': relevant, 'evidence': evidence, 'max_repairs': 0})
                    if result.get('artifact'):
                        issues = alignment(task, method, result['artifact'])
                        if issues:
                            result['status'] = 'blocked'
                            result['baseline_issues'] = issues
                else:
                    artifact = request['artifact']
                    issues = alignment(task, method, artifact)
                    if issues:
                        result = {'status': 'blocked', 'issues': issues}
                    else:
                        checked = await call('method_check_artifact', {'method_id': method, 'task': task, 'artifact': artifact, 'inputs': prior, 'evidence': evidence})
                        if checked['status'] == 'blocked':
                            result = checked
                        else:
                            result = await call('method_run_submit', {'run_id': request['run_id'], 'expected_revision': state['revision'], 'key': request['key'], 'method_id': method, 'artifact': artifact, 'evidence': evidence})
                            result['submission_scope'] = 'research_artifact_not_semantic_or_expert_approval'
            elif action == 'create_run':
                result = await call('method_run_create', {'task': request['task'], 'target': 'R42'})
            elif action == 'get_run':
                result = await call('method_run_get', {'run_id': request['run_id']})
                result['quality_gate'] = await call('method_quality_report', {'packet': {'level':'concept'}})
            else:
                raise ValueError('未知桥接动作')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
