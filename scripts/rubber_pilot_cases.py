import asyncio,json,sys
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_engine import ROOT
from method_case_adapter import normalize
from rubber_pilot_mcp import call
async def run():
 out=ROOT/'output/rubber-tapping-pilot';private=out/'private';private.mkdir(exist_ok=True);rows=[];evidence=[]
 async with stdio_client(StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/archive_mcp.py')])) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize()
   for pid in ['2025-00','2024-06','2024-s07','2025-03','2018-c01']:
    row={'project_id':pid}
    for name,args in [('gd_project_overview',{'project_id':pid}),('gd_read_records',{'project_id':pid,'limit':3}),('gd_list_sources',{'project_id':pid,'limit':20})]:
     try:row[name]=await call(s,name,args)
     except Exception as exc:row[name]={'error':str(exc)}
    for source in row.get('gd_list_sources',{}).get('data',[]):
     if not source.get('chunk_count'):continue
     try:
      raw=await call(s,'gd_read_evidence',{'project_id':pid,'source_id':source['id'],'limit':3})
      normalized=normalize(pid,source['id'],raw,max_chars=2000)
      if normalized['status']=='needs_text_revision_choice':row.setdefault('needs_revision_choice',[]).append(raw);continue
      evidence.extend(normalized['evidence']);row.setdefault('read_sources',[]).append(source['id'])
      (private/(pid+'-'+source['id']+'.json')).write_text(json.dumps(raw,ensure_ascii=False,indent=2))
     except Exception as exc:row.setdefault('read_errors',[]).append(str(exc))
     if len(row.get('read_sources',[]))>=2:break
    rows.append(row);print(pid+': '+str(len(row.get('read_sources',[])))+' sources',flush=True)
 (private/'case-records.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 (private/'case-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
 (out/'case-retrieval-audit.json').write_text(json.dumps({'method':'actual_stdio_MCP','projects':[{'project_id':x['project_id'],'revision':x.get('gd_project_overview',{}).get('publication_revision'),'read_sources':x.get('read_sources',[]),'record_count':x.get('gd_project_overview',{}).get('record_count'),'errors':x.get('read_errors',[])} for x in rows],'evidence_refs':[{k:v for k,v in e.items() if k!='text'} for e in evidence],'expert_reviewed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(run())
