# coding: utf-8
"""Validate the field contract, provenance, links and generated HTML."""
from pathlib import Path
from html.parser import HTMLParser
import json
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
s=json.loads((P/'字段规范.json').read_text());d=json.loads((P/'原子字段档案.json').read_text());e=json.loads((P/'档案数据.json').read_text())
fields={f['key']:f for f in s['fields']};assert len(fields)==len(s['fields'])
S={x['id'] for x in e['sources']};C={x['id'] for x in e['claims']};R={r['id'] for r in d['records']};assert len(R)==len(d['records'])
entities={en['key']:{f['name'] for f in en['fields']} for en in s['entities']}
for r in d['records']:
 assert set(r['cells'])==entities[r['entity']]
 for n,c in r['cells'].items():
  key=r['entity']+'.'+n;assert key in fields
  v=c['value'];t=fields[key]['type']
  assert set(c['source_ids'])<=S and set(c['claim_ids'])<=C
  assert (v is None)==(c['value_state']!='known'),key
  if v is None:continue
  assert c['source_ids'] or c.get('derivation'),key
  if t=='integer':assert isinstance(v,int) and not isinstance(v,bool),key
  if t=='number':assert isinstance(v,(int,float)) and not isinstance(v,bool),key
  if t in ['string_list','ref_list']:assert isinstance(v,list),key
  if t=='ref_list':assert set(v)<=R|S|C,key
  if t=='boolean':assert isinstance(v,bool),key
  if t in ['string','text','enum','url','date','partial_date','ref']:assert isinstance(v,str),key
class H(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.links=[];self.case=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if a.get('href','').startswith('#'):self.links.append(a['href'][1:])
  if 'data-atomic'in a:self.case.append('atomic-'+a['data-atomic'])
h=H();h.feed((P/'档案.html').read_text());assert len(h.ids)==len(set(h.ids));assert set(h.links+h.case)<=set(h.ids)
for r in d['records']:
 for n in r['cells']:assert 'atomic-'+r['id']+'-'+n in h.ids
assert d['counts']['patent_project_confirmed'] is None
assert d['counts']['patent_records_found']==sum(r['entity']=='patent' for r in d['records'])
assert d['counts']['paper_records_found']==sum(r['entity']=='paper' for r in d['records'])
assert (P/'字段规范.json').read_bytes()==(ROOT/'04-知识库/项目档案标准-v1/原子字段字典-v3.json').read_bytes()
print(json.dumps({'result':'pass','fields':len(fields),'records':len(R),'cells':sum(len(r['cells']) for r in d['records']),'unique_html_ids':len(h.ids),'checks':['types','explicit_unknowns','source_claim_refs','entity_refs','all_cell_anchors','schema_case_roundtrip_anchors','count_semantics','schema_copy']},ensure_ascii=False))
