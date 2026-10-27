from pathlib import Path
import urllib.request,hashlib,json,io
from pypdf import PdfReader
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[3]
DIR=Path(__file__).resolve().parent
class P(HTMLParser):
 def __init__(self):super().__init__();self.text=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.text.append(d.strip())
urls=[('MIT-CONCEPT','https://appinventor.mit.edu/explore/sites/all/files/teachingappcreation/unit4/DesignUnit4.pdf'),('MIT-DLAB','https://ocw.mit.edu/courses/ec-720j-d-lab-ii-design-spring-2010/pages/projects/ideas/'),('DS-NOBUILD','https://dschool.stanford.edu/tools/no-build-hack'),('NASA-V','https://www.nasa.gov/reference/5-3-product-verification/'),('NASA-VAL','https://www.nasa.gov/reference/5-4-product-validation/')]
p=DIR/'private-sources';p.mkdir(exist_ok=True);(DIR/'.gitignore').write_text('private-sources/\n__pycache__/\n')
rows=[]
for sid,u in urls:
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as f:raw=f.read();final=f.url
  ext='pdf'if raw.startswith(b'%PDF')else'html';rp=p/(sid+'.'+ext);rp.write_bytes(raw)
  if ext=='pdf':
   d=PdfReader(io.BytesIO(raw));text='\n'.join(f'[PDF page {i+1}]\n'+(x.extract_text()or'')for i,x in enumerate(d.pages))
  else:q=P();q.feed(raw.decode('utf-8',errors='replace'));text='\n'.join(q.text)
  tp=p/(sid+'.txt');tp.write_text(text)
  rows.append({'id':sid,'url':u,'final_url':final,'raw_path':str(rp.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'status':'acquired_not_fulltext_review','chars':len(text)})
 except Exception as e:rows.append({'id':sid,'url':u,'status':'failed','error':str(e)})
(DIR/'来源取得记录.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False,indent=2))
