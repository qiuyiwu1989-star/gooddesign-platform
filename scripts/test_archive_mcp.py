# coding: utf-8
"""Real SDK client smoke/evaluation against stdio subprocess; no writes."""
import asyncio,json,sys
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
ROOT=Path(__file__).resolve().parents[1]
async def main():
 params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/archive_mcp.py')])
 results=[]
 async with stdio_client(params)as(r,w):
  async with ClientSession(r,w)as session:
   init=await session.initialize();listed=await session.list_tools();assert len(listed.tools)==11;assert all(t.annotations.readOnlyHint for t in listed.tools)
   async def call(name,args):
    value=await session.call_tool(name,args);assert not value.isError,(name,value);data=value.structuredContent
    if data is None:data=json.loads(value.content[0].text)
    results.append(dict(tool=name,status='ok'));return data
   search=await call('gd_search_projects',dict(query='嫦娥',limit=3));assert any(x['id']=='2025-00'for x in search['data'])
   overview=await call('gd_project_overview',dict(project_id='2025-00'));assert overview['source_count']==172
   records=await call('gd_read_records',dict(project_id='2025-00',record_id='A03',fields=['method','doi'],limit=1));assert len(records['data'])==1
   sources=await call('gd_list_sources',dict(project_id='2025-00',limit=2));assert len(sources['data'])==2 and sources['next_offset']==2
   resolved=await call('gd_resolve_citation',dict(project_id='2025-00',citation_id='S09'));assert resolved['source_ids']
   raw=await call('gd_read_evidence',dict(project_id='2025-00',source_id=resolved['source_ids'][0],limit=1));assert len(raw['data'])<=1
   interp=await call('gd_read_interpretations',dict(project_id='2025-00',limit=2))
   ver=await call('gd_read_version',dict(project_id='2025-00',limit=2))
   if overview['publication_revision']!='research-000000':
    c=await call('gd_read_records',dict(project_id='2025-00',record_id='A03',fields=['method'],revision=overview['publication_revision'],limit=1));sid=c['data'][0]['cells']['method']['evidence']['source_id'];await call('gd_read_evidence',dict(project_id='2025-00',source_id=sid,revision=overview['publication_revision'],limit=1))
   if overview['publication_revision']!='research-000000':
    import xml.etree.ElementTree as ET
    v='research-000001'
    a=await call('gd_read_records',dict(project_id='2025-00',record_id='A03',fields=['doi','method','authors'],revision=v,limit=1));ac=a['data'][0]['cells']
    p=await call('gd_read_records',dict(project_id='2025-00',record_id='P04',fields=['publication_holder','inventors'],revision=v,limit=1));pc=p['data'][0]['cells']
    patents=await call('gd_read_records',dict(project_id='2025-00',entity='patent',fields=['title'],revision=v,limit=2))
    external=await call('gd_resolve_citation',dict(project_id='2025-00',citation_id='S19'))
    version=await call('gd_read_version',dict(project_id='2025-00',revision=v,limit=2))
    answers=['2025-00',ac['doi']['value'],ac['method']['evidence']['source_id'],ac['method']['evidence']['chunk_id'],pc['publication_holder']['value'],str(len(pc['inventors']['value'])),str(len(ac['authors']['value'])),str(patents['total']),external['scope'],str(version['total'])]
    expected=[qa.findtext('answer')for qa in ET.parse(ROOT/'tests/evaluations/archive038.xml').getroot()]
    assert answers==expected,(answers,expected)
    results.append(dict(evaluation='archive038.xml',verified_answers=len(answers),note='确定性SDK检索验证；未声称LLM自主回答通过'))
   method=await call('gd_search_methods',dict(query='TRIZ'));assert method['data'][0]['method_id']=='IM-CA-001'
   steps=await call('gd_read_method',dict(method_id='IM-CA-001',level='steps',limit=2));assert len(steps['data'])==2 and steps['next_offset']==2
   linked=await call('gd_read_innovation_run',dict(section='overview'));assert linked['data']['task']['scenario_type']=='simulated'
   for name,args in [('gd_list_sources',dict(project_id='2025-00',limit=99)),('gd_read_evidence',dict(project_id='2025-00',source_id='../../secret')),('gd_read_records',dict(project_id='../other'))]:
    value=await session.call_tool(name,args);assert value.isError;results.append(dict(tool=name,status='invalid_input_rejected'))
 print(json.dumps(dict(protocol=init.protocolVersion,tools=len(listed.tools),checks=results,scope='真实SDK握手/工具调用；非LLM自主检索效果评估'),ensure_ascii=False,indent=2))
if __name__=='__main__':asyncio.run(main())
