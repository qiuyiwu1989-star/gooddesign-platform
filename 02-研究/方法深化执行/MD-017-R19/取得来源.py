from pathlib import Path
import urllib.request,hashlib,json
from html.parser import HTMLParser
B=Path(__file__).resolve().parent.parent
items={'MD-017-R19':[('DH-PROTOCOL','https://www.designheuristics.com/wp-content/uploads/2014/06/Design-Heuristics-Idea-Development-Protocol-and-Materials.pdf'),('DH-RESEARCH','https://dalyresearch.engin.umich.edu/wp-content/uploads/sites/237/2018/02/Yilmaz-Daly-Seifert-Gonzalez-Evidence-based-design-heuristics-for-idea-generation.pdf')], 'MD-018-R20':[('CK-2003','https://www.designsociety.org/download-publication/24204/a_new_approach_of_innovative_design_an_introduction_to_c-k_theory')], 'MD-019-R21':[('MATRIZ-TOOLS','https://wiki.matriz.org/docs/triz/problem-solving-tools-5890/')], 'MD-020-R22':[('MATRIZ-EC','https://wiki.matriz.org/docs/triz/problem-solving-tools-5890/contradictions/engineering-contradiction-5995/') ]}
class T(HTMLParser):
 def __init__(self):super().__init__();self.a=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style']:self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.a.append(d.strip())
if __name__=='__main__':
 for task,rr in items.items():
  d=B/task;(d/'.gitignore').write_text('private-sources/\n__pycache__/\n');out=[]
  for sid,u in rr:
   e={'id':sid,'url':u,'date':'2026-10-27'}
   try:
    with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=25)as f:raw=f.read();e['final_url']=f.url
    pdf=raw.startswith(b'%PDF-');p=d/'private-sources'/(sid+('.pdf'if pdf else'.html'));p.write_bytes(raw)
    if pdf:
     from pypdf import PdfReader
     doc=PdfReader(p);e['pages']=len(doc.pages);text='\n'.join('[PDF page '+str(i+1)+']\n'+(pg.extract_text()or'')for i,pg in enumerate(doc.pages))
    else:
     t=T();t.feed(raw.decode('utf-8','replace'));text='\n'.join(t.a)
    tp=p.with_suffix('.txt');tp.write_text(text);e.update(raw_file=str(p.relative_to(d)),raw_sha256=hashlib.sha256(raw).hexdigest(),text_file=str(tp.relative_to(d)),text_sha256=hashlib.sha256(tp.read_bytes()).hexdigest(),status='acquired_selected_review_needed')
   except Exception as err:e.update(status='failed',error=str(err))
   out.append(e)
  (d/'来源取得记录.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(task,[(x['id'],x['status'])for x in out])
