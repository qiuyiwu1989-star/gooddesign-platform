import json,hashlib,zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
from method_engine import ROOT,digest
OUT=ROOT/'output/rubber-tapping-pilot'
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=set()
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id'in d:self.ids.add(d['id'])
  for k in ('href','src'):
   if k in d:self.links.append(d[k])
errors=[]
for p in OUT.glob('*.html'):
 parser=Links();parser.feed(p.read_text())
 for link in parser.links:
  url=urlsplit(link)
  if url.scheme or url.netloc:continue
  target=p.parent/unquote(url.path) if url.path else p
  if not target.exists():errors.append(str(p.name)+': '+link)
  elif url.fragment and target==p and url.fragment not in parser.ids:errors.append('missing_anchor:'+link)
intake=json.loads((OUT/'需求包.json').read_text());report=json.loads((OUT/'engine-report.json').read_text());artifacts=json.loads((OUT/'Agent推理产物.json').read_text())['artifacts']
assert digest(intake)==report['demand_packet_sha256']
assert {r['id'] for r in intake['requirements']}=={r['id'] for r in artifacts['R48']['payload']['requirements']}
assert {r['id'] for r in intake['requirements']}=={r['requirement_id'] for r in artifacts['R42']['payload']['matrix']}
assert report['restart_revision']==6 and all(x['check']['status']!='blocked' for x in report['checks'])
assert not artifacts['R36']['payload']['recommendations']
assert report['omitted_hard_constraint_negative']['status']=='blocked'
assert report['quality_gate']['status']=='blocked' and not report['expert_certified']
with zipfile.ZipFile(OUT/'交付包.zip') as z:
 manifest=json.loads(z.read('文件指纹.json'))
 assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in manifest.items())
 assert not any('private/' in n or n.endswith('.sqlite3') for n in z.namelist())
result={'status':'passed' if not errors else 'failed','local_link_errors':errors,'need_ids_preserved':15,'artifact_checks':6,'restart_revision':6,'recommendations':[],'negative_case':'blocked','quality_gate':'blocked','zip_hashes':'passed','expert_certified':False,'model_backend':'429_timeout_not_success'}
(OUT/'交付检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False));assert not errors
