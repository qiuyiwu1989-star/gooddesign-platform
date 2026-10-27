from pathlib import Path
import hashlib,io,json,urllib.request
from html.parser import HTMLParser
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent.parent
class T(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
items=[('MD-014-R13','HSE-WORKLOAD','https://www.hse.gov.uk/humanfactors/topics/workload.htm'),('MD-014-R13','HSE-INTRO','https://www.hse.gov.uk/humanfactors/introduction.htm'),('MD-015-R15','WVDOT-FAST','https://transportation.wv.gov/highways/engineering/files/WVVEMANUAL.pdf'),('MD-015-R15','USBR-VE','https://www.usbr.gov/dso-dec/vp/pdf/VPHandbook-7February2008.pdf'),('MD-015-R15','USBR-SAVE','https://usbr.gov/dso-dec/vp/pdf/vmstd.pdf'),('MD-015-R15','FHWA-VE','https://www.fhwa.dot.gov/ve/veproc.cfm'),('MD-016-R16','HSE-HSG245','https://www.hse.gov.uk/pubns/hsg245.pdf'),('MD-016-R16','HSE-CAUSE','https://www.hse.gov.uk/foi/internalops/og/ogprocedures/investigation/coreobjectives.htm')]
records={}
for folder,sid,url in items:
 d=BASE/folder;d.mkdir(exist_ok=True);(d/'.gitignore').write_text('private-sources/\n__pycache__/\n');p=d/'private-sources';p.mkdir(exist_ok=True)
 r={'id':sid,'url':url,'retrieved_date':'2026-10-27','acquisition_is_not_fulltext_review':True}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as f:raw=f.read(12*1024*1024+1);r['final_url']=f.url
  if len(raw)>12*1024*1024:raise ValueError('too_large')
  pdf=raw.startswith(b'%PDF');ext='pdf'if pdf else'html';rawpath=p/(sid+'.'+ext);rawpath.write_bytes(raw)
  if pdf:
   doc=PdfReader(io.BytesIO(raw));r['pages']=len(doc.pages);txt='\n'.join(f'[PDF page {i+1}]\n'+(x.extract_text()or'')for i,x in enumerate(doc.pages))
  else:h=T();h.feed(raw.decode('utf-8',errors='replace'));txt='\n'.join(h.parts)
  tp=p/(sid+'.txt');tp.write_text(txt);r.update(status='acquired',raw_path=str(rawpath.relative_to(ROOT)),raw_sha256=hashlib.sha256(raw).hexdigest(),text_sha256=hashlib.sha256(txt.encode()).hexdigest(),text_path=str(tp.relative_to(ROOT)),chars=len(txt))
 except Exception as e:r.update(status='failed',error=str(e))
 records.setdefault(folder,[]).append(r)
for folder,rr in records.items():(BASE/folder/'来源取得记录.json').write_text(json.dumps(rr,ensure_ascii=False,indent=2))
print(json.dumps([{x['id']:x['status']}for rr in records.values()for x in rr],ensure_ascii=False))
