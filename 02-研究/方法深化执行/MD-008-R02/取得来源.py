from pathlib import Path
import hashlib,json,urllib.request
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parent.parent
SOURCES={
'MD-008-R02':[('DC-FRAME','https://www.designcouncil.org.uk/resources/framework-for-innovation/'),('DC-DD','https://www.designcouncil.org.uk/resources/the-double-diamond/')],
'MD-009-R03':[('DS-BOOTLEG','https://dschool.stanford.edu/tools/design-thinking-bootleg'),('DS-PDF','https://dschool.sfo3.digitaloceanspaces.com/documents/dschool_bootleg_deck_2018_final_sm2-6.pdf')],
'MD-010-R09':[('CI-JOBS','https://www.christenseninstitute.org/theory/jobs-to-be-done/')]
}
class T(HTMLParser):
 def __init__(self):super().__init__();self.a=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.a.append(d.strip())
if __name__=='__main__':
 for task,rows in SOURCES.items():
  b=ROOT/task;p=b/'private-sources';p.mkdir(exist_ok=True);(b/'.gitignore').write_text('private-sources/\n__pycache__/\n')
  out=[]
  for sid,u in rows:
   with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as f:raw=f.read();final=f.url
   ext='pdf'if raw.startswith(b'%PDF-')else'html';rp=p/(sid+'.'+ext);rp.write_bytes(raw)
   if ext=='pdf':
    from pypdf import PdfReader
    doc=PdfReader(rp);text='\n'.join('[PDF page '+str(i+1)+']\n'+(pg.extract_text()or'')for i,pg in enumerate(doc.pages))
   else:
    parser=T();parser.feed(raw.decode('utf-8','replace'));text='\n'.join(parser.a)
   tp=p/(sid+'.txt');tp.write_text(text)
   out.append({'id':sid,'url':u,'final_url':final,'date':'2026-10-27','raw_file':'private-sources/'+rp.name,'raw_sha256':hashlib.sha256(raw).hexdigest(),'text_file':'private-sources/'+tp.name,'text_sha256':hashlib.sha256(tp.read_bytes()).hexdigest(),'status':'acquired_selected_review_required'})
  (b/'来源取得记录.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(task,len(out))
