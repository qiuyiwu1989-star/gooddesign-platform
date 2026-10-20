# coding: utf-8
"""027: reconcile catalogue, resolve static URLs and enforce the preview export scope."""
import json,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[1];PUB=ROOT/'output/inno-preview';SITE=PUB/'inno'
class References(HTMLParser):
 def __init__(self):super().__init__();self.urls=[]
 def handle_starttag(self,tag,attrs):
  for key,value in attrs:
   if key in ['src','href']and value:self.urls.append(value)
def check():
 rows=json.loads((SITE/'catalog.json').read_text());assert len(rows)==len({r['id']for r in rows})==560
 assert sum(r['research']for r in rows)==1
 files=list(SITE.rglob('*'));assert not any(p.suffix.lower()in ['.pdf','.docx','.md','.csv']for p in files)
 assert {p.name for p in SITE.rglob('*.json')}=={'catalog.json','build-report.json'}
 checked=0
 for file in SITE.rglob('*.html'):
  parser=References();parser.feed(file.read_text())
  for value in parser.urls:
   url=urlsplit(value)
   if url.scheme or url.netloc or value.startswith('#'):continue
   target=(PUB/unquote(url.path).lstrip('/'))if url.path.startswith('/')else file.parent/unquote(url.path)
   assert target.resolve().is_relative_to(PUB.resolve()),(file,value)
   assert target.exists(),(str(file),value)
   if target.is_dir():assert (target/'index.html').exists(),(str(file),value)
   checked+=1
 for row in rows:
  page=SITE/'projects'/row['id']/'index.html';assert page.exists();text=page.read_text()
  for label in ['项目档案','资料与解读','档案评估']:assert label in text
  if not row['research']:
   assert '尚未评价'in text
   if row['summary']:assert '原库字段摘录'in text
 report=dict(status='pass',projects=560,html_pages=len(list(SITE.rglob('*.html'))),local_urls_checked=checked,research_dossiers=1,raw_private_files_exported=False)
 print(json.dumps(report,ensure_ascii=False));return report
if __name__=='__main__':check()
