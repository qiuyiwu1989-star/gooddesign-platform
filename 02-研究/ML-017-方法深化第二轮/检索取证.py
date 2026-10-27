"""Public source acquisition only; HTTP success is not a read/quality judgment."""
import concurrent.futures,hashlib,io,json,re,time,urllib.request
from pathlib import Path
from html.parser import HTMLParser
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/method-deepening-ML017/private-sources'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  if t in ('script','style','noscript'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style','noscript'):self.skip=max(0,self.skip-1)
 def handle_data(self,d):
  if not self.skip and d.strip():self.parts.append(d.strip())
old=json.loads((ROOT/'02-研究/ML-014-逐法深度研究/研究总索引.json').read_text())
refs={}
for m in old['methods']:
 for u in m['new_primary_sources']:refs.setdefault(u,[]).append(m['research_id'])
extra={
'https://www.johngero.com/publications/Progress/13GeroKannengiesserDesignTheoryChapter.pdf':['R49'],
'https://www.mit.edu/people/evhippel/Lead%20User%20Project%20Handbook%20%28Full%20Version%29.pdf':['R10'],
'https://standards.nasa.gov/sites/default/files/standards/GSFC/Baseline/0/GSFC-HDBK-8004_Approved_0.pdf':['R40'],
'https://www.hse.gov.uk/pubns/hsg245.pdf':['R16'],
'https://www.flighttestsafety.org/images/STPA_Handbook.pdf':['R51'],
'https://www.wipo.int/edocs/pubdocs/en/wipo_pub_946.pdf':['R46'],
'https://ansyshelp.ansys.com/public/Views/Secured/Granta/v251/en/Selector/sel_edu/what_is_performance_index.html':['R33'],
'https://johngero.com/publications/Progress/13GeroKannengiesserDesignTheoryChapter.pdf':['R49'],
'https://www.johngero.com/publications/2004/04GeroKannengDesignStud.pdf':['R49'],
'https://cfpub.epa.gov/si/si_public_record_report.cfm?dirEntryId=155087':['R43'],

'https://cs.gmu.edu/~jgero/publications/2003/03oGeroKannengoCAADRIA03.pdf':['R49'],
'https://psas.scripts.mit.edu/home/books-and-handbooks/':['R51'],
'https://sunnyday.mit.edu/STPA-Handbook.pdf':['R51'],
'https://www.me.neu.edu.cn/2016/0603/c3401a56936/pagem.htm':['WB01','WB04','WB11'],
'https://www.itl.nist.gov/div898/handbook/pri/section4/pri471.htm':['R38','R39'],
'https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/':['R48'],
'https://www.nist.gov/artificial-intelligence/ai-research/tevv-athlon-framework-evaluating-ai-systems':['EVALUATION'],
'https://www.designcouncil.org.uk/our-resources/the-double-diamond/':['R02'],
'https://ocw.mit.edu/courses/res-15-009-lead-user-innovation-handbook-spring-2026/':['R10'],
}
for u,ids in extra.items():refs.setdefault(u,[]).extend(x for x in ids if x not in refs.get(u,[]))
def fetch(item):
 u,ids=item;sid=hashlib.sha256(u.encode()).hexdigest()[:14];r={'id':sid,'url':u,'methods':ids,'retrieved_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'read_status':'machine_acquisition_only_not_evidence_review'}
 try:
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0 (method research; public source verification)'})
  with urllib.request.urlopen(req,timeout=18) as f:
   raw=f.read(12*1024*1024+1);r.update(http_status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type',''))
  if len(raw)>12*1024*1024:raise ValueError('source size exceeds acquisition limit')
  pdf=raw.startswith(b'%PDF-');ext='.pdf' if pdf else '.html';p=OUT/(sid+ext);p.write_bytes(raw)
  r.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),raw=str(p.relative_to(ROOT)))
  if pdf:
   reader=PdfReader(io.BytesIO(raw));r['pages']=len(reader.pages);text='\n'.join(f'\n[PDF page {i+1}]\n'+(p.extract_text()or'') for i,p in enumerate(reader.pages))
  else:
   h=Text();h.feed(raw.decode('utf-8',errors='replace'));text='\n'.join(h.parts)
   title=re.search(r'<title[^>]*>(.*?)</title>',raw.decode('utf-8',errors='replace'),re.S|re.I);r['title']=re.sub(r'\s+',' ',title.group(1)).strip() if title else text[:100]
  tp=OUT/(sid+'.txt');tp.write_text(text);r.update(text=str(tp.relative_to(ROOT)),text_chars=len(text),status='acquired_unreviewed')
  if any(x in text.lower()[:1800] for x in ['php2shell mitigations','access denied','verify you are human','just a moment']):r['status']='interstitial_not_source_content'
 except Exception as e:r.update(status='acquisition_failed',error=type(e).__name__+': '+str(e)[:220])
 return r
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  rows=list(pool.map(fetch,refs.items()))
 p=OUT.parent/'来源取得清单.json';p.write_text(json.dumps({'scope':'public acquisition; not full-text scholarly review or permission to republish','sources':rows},ensure_ascii=False,indent=2))
 from collections import Counter
 print(json.dumps({'sources':len(rows),'status':dict(Counter(x['status'] for x in rows))},ensure_ascii=False))
