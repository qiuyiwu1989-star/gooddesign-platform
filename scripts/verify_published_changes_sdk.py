"""Read-only actual stdio MCP verification of every changed fact field in current versions."""
import argparse,asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
import project_pipeline as pp,research_workflow as rw
ROOT=pp.ROOT
def value(result):
 if result.isError:raise ValueError('MCP tool rejected verification call')
 return json.loads(next(x.text for x in result.content if x.type=='text'))
async def verify(pids):
 rows=[]
 async with stdio_client(StdioServerParameters(command=str(ROOT/'.runtime/pipeline/bin/python'),args=[str(ROOT/'scripts/archive_mcp.py')],cwd=str(ROOT)))as(reader,writer):
  async with ClientSession(reader,writer)as session:
   await session.initialize()
   for pid in pids:
    p=pp.project(pp.LIB,pid);revision='research-%06d'%rw.current(p)['revision'];folder,_=rw.check_version(p,revision);changes=pp.load(folder/'changes.json')['changes'];dataset_sha=pp.sha((folder/'档案.json').read_bytes())
    for change in changes:
     if change.get('content_nature')!='source_statement':continue
     rid,field=change['record_id'],change['field'];records=value(await session.call_tool('gd_read_records',dict(project_id=pid,record_id=rid,fields=[field],revision=revision,limit=1)));cell=records['data'][0]['cells'][field];e=cell['evidence'];blocks=pp.load(pp.safe(p,e['chunks_path']));assert pp.sha(pp.safe(p,e['chunks_path']).read_bytes())==e['chunks_sha256'];offset=next(i for i,x in enumerate(blocks)if x['id']==e['chunk_id'])
     response=value(await session.call_tool('gd_read_evidence',dict(project_id=pid,source_id=e['source_id'],revision=revision,chunks_sha256=e['chunks_sha256'],offset=offset,limit=1)));actual=response['data'][0];assert actual['id']==e['chunk_id']and e['quote']in actual['text']and cell['value']==change['after'];rows.append(dict(project_id=pid,revision=revision,record_id=rid,field=field,source_id=e['source_id'],chunk_id=e['chunk_id'],chunks_sha256=e['chunks_sha256'],quote_sha256=pp.sha(e['quote'].encode()),status='exact_changed_field_verified'))
    assert pp.sha((folder/'档案.json').read_bytes())==dataset_sha,'version changed during verification'
 return {'protocol':'actual_stdio_sdk','scope':'changed_source_statement_fields_only_not_full_dataset_or_quality','checks':rows}
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('projects',nargs='+');args=ap.parse_args();print(json.dumps(asyncio.run(verify(args.projects)),ensure_ascii=False,indent=2))
