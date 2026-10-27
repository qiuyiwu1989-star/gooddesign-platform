import asyncio,json
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[3]
def value(r):
 assert not r.isError;return json.loads(next(x.text for x in r.content if x.type=='text'))
async def main():
 async with stdio_client(StdioServerParameters(command=str(ROOT/'.runtime/pipeline/bin/python'),args=[str(ROOT/'scripts/archive_mcp.py')],cwd=str(ROOT)))as(rd,wr):
  async with ClientSession(rd,wr)as s:
   await s.initialize();ts=await s.list_tools();assert 'gd_search_project_fields'in[t.name for t in ts.tools]
   r=value(await s.call_tool('gd_search_project_fields',dict(query='112476225',project_ids=['2025-04'],limit=5)));assert r['total'] and not r['issues'];hit=r['data'][0];assert hit['revision']=='research-000004'
   records=value(await s.call_tool('gd_read_records',dict(project_id=hit['project_id'],record_id=hit['record_id'],fields=[hit['field']],revision=hit['revision'],limit=1)));assert records['data'][0]['cells'][hit['field']]['value']==hit['value']
   e=hit['evidence'];evidence=value(await s.call_tool('gd_read_evidence',dict(project_id=hit['project_id'],source_id=e['source_id'],revision=hit['revision'],chunks_sha256=e['chunks_sha256'],limit=1)));assert evidence['data']
   bad=await s.call_tool('gd_search_project_fields',dict(query=' '));assert bad.isError
   print(json.dumps(dict(protocol='actual_stdio_sdk',tool_count=len(ts.tools),search=r,record_verified=True,evidence_verified=True,invalid_query_rejected=True),ensure_ascii=False,indent=2))
asyncio.run(main())
