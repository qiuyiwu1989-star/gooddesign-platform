# coding: utf-8
"""SDK acceptance for the first two published incremental research dossiers."""
import asyncio,json
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
def value(result):
 if result.isError:raise AssertionError(result)
 return json.loads(next(x.text for x in result.content if x.type=='text'))
async def main():
 checks=[]
 async with stdio_client(StdioServerParameters(command=str(ROOT/'.runtime/pipeline/bin/python'),args=[str(ROOT/'scripts/archive_mcp.py')],cwd=str(ROOT)))as(read,write):
  async with ClientSession(read,write)as session:
   await session.initialize()
   for pid in ['2015-02','2017-01']:
    overview=value(await session.call_tool('gd_project_overview',dict(project_id=pid)));assert not overview['baseline_only']
    guide=overview['reading_guide'];assert guide['status']=='available'
    assert guide['notes']['research_revision']==overview['publication_revision']and guide['notes']['project_id']==pid
    assert len(guide['notes']['modules'])==8 and not guide['manifest']['expert_reviewed']
    revision=overview['publication_revision'];records=value(await session.call_tool('gd_read_records',dict(project_id=pid,record_id='PROJECT',fields=['canonical_name'],revision=revision,limit=1)))
    cell=records['data'][0]['cells']['canonical_name'];assert cell['value']and cell['evidence']
    source=cell['evidence']['source_id'];blocks=value(await session.call_tool('gd_read_evidence',dict(project_id=pid,source_id=source,revision=revision,limit=2)))
    assert blocks['data'];version=value(await session.call_tool('gd_read_version',dict(project_id=pid,revision=revision,limit=2)));assert version['total']>0
    analysis=value(await session.call_tool('gd_read_interpretations',dict(project_id=pid,revision=revision,limit=2)));assert analysis['total']>=1
    checks.append(dict(project=pid,revision=revision,records=overview['record_count'],changes=version['total'],interpretations=analysis['total'],reading_guide=guide['notes']['version'],guide_modules=len(guide['notes']['modules']),evidence_source=source,status='passed'))
 print(json.dumps(dict(protocol='actual_stdio_sdk',checks=checks),ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
