# -*- coding: utf-8 -*-
from pathlib import Path
import concurrent.futures,hashlib,io,json,urllib.request
from html.parser import HTMLParser
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent.parent
class T(HTMLParser):
 def __init__(self):super().__init__();self.out=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style','noscript']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style','noscript']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.out.append(d.strip())
items=[('MD-026-R28','ARIZ-RU','https://altshuller.ru/triz/ariz85v.asp'),('MD-026-R28','ARIZ-ES','https://www.altshuller.ru/world/spa/ariz85v.asp'),('MD-027-R29','MATRIZ-TESE','https://wiki.matriz.org/docs/triz/trends-of-engineering-systems-evolution-tese-5919/'),('MD-027-R29','TSET-STUDY','https://citeseerx.ist.psu.edu/document?doi=a38206fd647e621ba1f5758e39ba4d3cddbf7dd7&repid=rep1&type=pdf'),('MD-027-R29','TESE-REVIEW','https://www.sciencedirect.com/science/article/pii/S036083522200821X'),('MD-028-R18','BOHN-2004','https://pmc.ncbi.nlm.nih.gov/articles/PMC521129/'),('MD-028-R18','BIOMIMICRY','https://toolbox.biomimicry.org/methods/abstract/'),('MD-029-R49','GERO-2004','https://johngero.com/publications/2004/04GeroKannengDesignStud.pdf'),('MD-029-R49','GERO-INDEX','https://www.johngero.com/publications/2004.html')]
def get(row):
 folder,sid,url=row;d=BASE/folder;(d/'.gitignore').write_text('private-sources/\n__pycache__/\n');p=d/'private-sources'
 r={'id':sid,'url':url,'retrieved_date':'2026-10-27','scope':'acquisition_only_until_selected_sections_reviewed'}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as f:raw=f.read(15*1024*1024+1);r['final_url']=f.url;ct=f.headers.get('content-type','')
  if len(raw)>15*1024*1024:raise ValueError('source_size_limit')
  pdf=raw.startswith(b'%PDF');rp=p/(sid+('.pdf'if pdf else'.html'));rp.write_bytes(raw)
  if pdf:
   doc=PdfReader(io.BytesIO(raw));r['pages']=len(doc.pages);text='\n'.join(f'[PDF page {i+1}]\n'+(x.extract_text()or'')for i,x in enumerate(doc.pages))
  else:
   # Altshuller Russian legacy pages declare Windows-1251; use headers/meta rather than corrupting text.
   import re
   enc=re.search(br'charset[=\s\"\x27]+([\w-]+)',raw[:6000],re.I)
   encoding=enc.group(1).decode('ascii')if enc else'utf-8';r['encoding']=encoding
   h=T();h.feed(raw.decode(encoding,errors='replace'));text='\n'.join(h.out)
  tp=p/(sid+'.txt');tp.write_text(text);r.update(status='acquired',raw=str(rp.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),text=str(tp.relative_to(ROOT)),text_sha256=hashlib.sha256(text.encode()).hexdigest(),chars=len(text))
  if any(z in text[:1500].lower()for z in ['checking your browser','access denied','verify you are human','javascript is required']):r['status']='interstitial_not_source'
 except Exception as e:r.update(status='failed',error=str(e))
 return folder,r
records={}
with concurrent.futures.ThreadPoolExecutor(max_workers=7)as pool:
 for f,r in pool.map(get,items):records.setdefault(f,[]).append(r)
for f,rs in records.items():(BASE/f/'来源取得记录.json').write_text(json.dumps(rs,ensure_ascii=False,indent=2))
print(json.dumps([{r['id']:{'status':r['status'],'pages':r.get('pages'),'chars':r.get('chars')}}for rs in records.values()for r in rs],ensure_ascii=False))
