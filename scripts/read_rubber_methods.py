import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
from rubber_pilot_mcp import call
async def run():
 out=ROOT/'output/rubber-tapping-pilot';rows={}
 async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_mcp.py')])) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for rid in ['R48','R14','R17','R36','R44','R42','WB03','R41']:
    rows[rid]=await call(s,'method_get',{'method_id':rid,'view':'full'})
 (out/'private/method-content.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('8 method dossiers read through MCP')
if __name__=='__main__':asyncio.run(run())
