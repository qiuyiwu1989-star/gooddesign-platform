"""ML-006 actual stdio MCP bridge; deterministic tools only, no model quota."""
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
    script = 'archive_mcp.py' if action == 'case_search' else 'method_engine_mcp.py'
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
            elif action == 'create_run':
                result = await call('method_run_create', {'task': request['task'], 'target': 'R42'})
            elif action == 'get_run':
                result = await call('method_run_get', {'run_id': request['run_id']})
            else:
                raise ValueError('未知桥接动作')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
