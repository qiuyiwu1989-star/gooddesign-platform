"""ML-005: read-only case discovery and explicit real method-engine calls."""
import asyncio,json,sys,os
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
async def call(s,n,a):
 r=await s.call_tool(n,a)
 if r.isError:raise ValueError(str(r.content))
 return r.structuredContent or json.loads(r.content[0].text)
async def run():
 out=ROOT/'output/rubber-tapping-pilot';out.mkdir(exist_ok=True)
 results={}
 async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/archive_mcp.py')])) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for q in ['采样','柔性','机器人','刀具','采摘']:
    results[q]=await call(s,'gd_search_projects',{'query':q,'limit':10})
   (out/'case-discovery.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
 print('case discovery saved',flush=True)
if __name__=='__main__':asyncio.run(run())
