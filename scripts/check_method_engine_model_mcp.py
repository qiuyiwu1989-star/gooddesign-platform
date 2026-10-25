"""Explicit live model-over-MCP smoke test; no domain quality certification."""
import asyncio
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
sys.path.insert(0,str(ROOT/'tests'))
from method_engine_fixtures import teaching_task


async def main():
    async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')])) as (r,w):
        async with ClientSession(r,w) as session:
            init=await session.initialize()
            response=await session.call_tool('method_propose_artifact',{'method_id':'R48','task':teaching_task(),'max_repairs':1})
            if response.isError:raise ValueError(str(response.content))
            result=response.structuredContent or json.loads(response.content[0].text)
            assert result['status'] in {'blocked','draft_requires_semantic_and_domain_review'}
            assert result['model_mode']=='real_codex_model' and result['expert_certified'] is False
            report={'status':'live_model_protocol_call_completed','protocol':init.protocolVersion,
                    'result':result,'expert_quality':'not_assessed','note':'模型草稿可能被检查器拒绝；协议成功不等于专家级。'}
            (ROOT/'output/method-engine-ML003/live-model-mcp.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps({'status':result['status'],'call_id':result['call_id'],'expert_certified':False}))


if __name__=='__main__':asyncio.run(main())
