"""ML-008 actual SDK additive-entrypoint checks; no model calls."""
import asyncio
import json
import os
import sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]

async def run():
    saved=json.loads((ROOT/'output/method-workbench-check/ml007/workspace-execution.json').read_text())
    env={**os.environ,'METHOD_ENGINE_DB':str(ROOT/'output/method-workbench-private/engine.sqlite')}
    params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_incremental_mcp.py')],env=env)
    async with stdio_client(params) as (r,w):
        async with ClientSession(r,w) as session:
            await session.initialize()
            tools=(await session.list_tools()).tools
            names={t.name for t in tools}
            assert len(names)==20 and {'method_generate_function_options','method_assemble_function_options','method_run_submit'}<=names
            for tool in tools:
                if tool.name in ('method_generate_function_options','method_assemble_function_options'):
                    assert tool.annotations.readOnlyHint is False and tool.annotations.openWorldHint is True
            args={'run_id':saved['state']['run_id'],'function_id':'NOT-A-FUNCTION','evidence':saved['evidence']}
            invalid=await session.call_tool('method_generate_function_options',args)
            assert invalid.isError and '功能ID不在当前' in str(invalid.content)
            missing=await session.call_tool('method_assemble_function_options',{'run_id':saved['state']['run_id'],'parts':{},'evidence':saved['evidence']})
            assert missing.isError and '片段缺失' in str(missing.content)
    print(json.dumps({'transport':'real_stdio_SDK','tool_count':20,'additive_tools':2,'old_tools_preserved':18,'invalid_function_blocked_before_model':True,'missing_parts_blocked_before_model':True,'model_calls':0},ensure_ascii=False))

if __name__=='__main__':asyncio.run(run())
