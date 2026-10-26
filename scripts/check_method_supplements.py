"""ML-012 structural, selection and real MCP checks. Not semantic/expert certification."""
import asyncio
import copy
import json
import os
import sys
import tempfile
from pathlib import Path
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from method_library_catalog import catalog,read,SUPPLEMENT,ROOT
from method_workbench_server import Store

def checks():
 rows=catalog()['methods'];assert len(rows)==64
 assert len({x['research_id'] for x in rows})==64 and len({x['method_id'] for x in rows})==64
 ids={x['research_id'] for x in rows}
 for rid in ['R49','R50','R51','R52']:
  d=read(rid);assert d['review_status']=='not_expert_reviewed'
  assert set(d['sections'])=={'identity','problem','principle','applicability','interpretation','example','pitfalls','validation','adaptation','gaps'}
  inputs={x['key'] for x in d['inputs']};steps={x['step_id'] for x in d['steps']};sources={x['source_id'] for x in d['sources']};produced=set(inputs)
  for s in d['steps']:
   assert set(s['depends_on'])<=steps and set(s['source_refs'])<=sources
   assert set(s['input_refs'])<=produced
   assert all(s[k] for k in ['operation','decision','output_description','checks','stop_condition'])
   produced.add(s['output_key'])
  assert all(x['target_research_id'] in ids for x in d['relations'])
  assert all(x['url'].startswith('https://') and x['locator'] and x['read_scope'] for x in d['sources'])
 assert read('R49')['source_readiness']=='limited_excerpt_only'
 assert '不能伪算EVSI' in read('R52')['sections']['applicability']
 folder=ROOT/'output/method-workbench-check/ml012';folder.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(dir=folder) as tmp:
  store=Store(Path(tmp)/'d.sqlite');store.seed();d=copy.deepcopy(store.get('RUBBER-20261026')['data']);d.update(id='SUPPLEMENT-TEST',expected_revision=0,selected_methods=['R49','R50','R51','R52'])
  saved=store.save(d);assert saved['data']['selected_methods']==['R49','R50','R51','R52']
 print('Structure/provenance, 64 unique IDs, source-gap boundary and saved selection passed')

async def mcp_checks():
 params=StdioServerParameters(command=sys.executable,args=[str(ROOT/'scripts/method_engine_library_mcp.py')],env={**os.environ,'METHOD_ENGINE_DB':str(ROOT/'output/method-workbench-private/engine.sqlite')})
 async with stdio_client(params) as (r,w):
  async with ClientSession(r,w) as s:
   await s.initialize();tools=(await s.list_tools()).tools;assert len(tools)==22
   for rid in ['R49','R50','R51','R52']:
    result=await s.call_tool('method_supplement_get',{'method_id':rid});assert not result.isError
    text=str(result.content);assert 'execution_available' in text and 'false' in text
   for q in ['FBS','服务蓝图','STPA','VOI']:
    r=await s.call_tool('method_supplement_search',{'query':q});assert not r.isError
   result=await s.call_tool('method_get',{'method_id':'R17','view':'overview'});assert not result.isError
 print('Actual stdio 22 tools: four supplement reads/searches plus original R17; model calls=0')
if __name__=='__main__':checks();asyncio.run(mcp_checks())
