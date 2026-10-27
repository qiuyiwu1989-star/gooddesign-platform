from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request,io
from pypdf import PdfReader
P=Path(__file__).resolve().parent;B=P.parent
URLS=[
('MD-011-R10','MIT-WORKING1986','https://dspace.mit.edu/bitstreams/26c4a314-0386-4ec3-a024-9237ea08cede/download'),
('MD-011-R10','MIT-OLD1988','https://web.mit.edu/evhippel/www-old/papers/Lead%20Users%20Eric%20von%20Hippel%20and%20Glen%20Urban%20-%201988.pdf'),
('MD-013-R12','QFDI-AHP-TUTORIAL','https://www.qfdi.org/ahp-tutorial'),
('MD-013-R12','QFDI-WHAT','https://www.qfdi.org/what-is-qfd'),
('MD-013-R12','QFDI-MEMBERSHIP2013','https://static1.squarespace.com/static/5eb315d2b0e6914ba0419e47/t/5eb87c450e4d61663a0a7eb6/1589148741728/mazur_2013_qfd_for_membership_organizations.pdf'),
('MD-013-R12','ISO16355-CATALOG','https://www.iso.org/standard/74103.html'),
('MD-011-R10','MIT-HANDBOOK','https://web.mit.edu/evhippel/www-old/Lead%20User%20Project%20Handbook%20%28Full%20Version%29.pdf'),
('MD-011-R10','MIT-1988','https://web.mit.edu/evhippel/papers/Lead%20Users%20Eric%20von%20Hippel%20and%20Glen%20Urban%20-%201988.pdf'),
('MD-011-R10','INFORMS-1986','https://pubsonline.informs.org/doi/abs/10.1287/mnsc.32.7.791'),
('MD-011-R10','MIT-2026','https://ocw.mit.edu/courses/res-15-009-lead-user-innovation-handbook-spring-2026/'),
('MD-012-R11','JSSD-2014','https://www.jstage.jst.go.jp/article/jssdj/61/1/61_1_27/_pdf/-char/en'),
('MD-012-R11','KANO-1984','https://www.jstage.jst.go.jp/article/quality/14/2/14_KJ00002952366/_article'),
('MD-012-R11','GITLAB-PRACTICE','https://handbook.gitlab.com/handbook/upstream-studios/experience-research/kano-model/'),
('MD-013-R12','QFDI-FACTS','https://www.qfdi.org/qfd-quick-facts'),
('MD-013-R12','QFDI-AHP','https://www.qfdi.org/ahp'),
]
def fetch(row):
 folder,sid,url=row;p=B/folder/'private-sources';p.mkdir(exist_ok=True);r={'id':sid,'url':url,'date':'2026-10-27','fulltext_reviewed':False}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=23)as f:data=f.read(10*1024*1024);r.update(final_url=f.url,http_status=f.status)
  pdf=data.startswith(b'%PDF');f=p/(sid+('.pdf'if pdf else'.html'));f.write_bytes(data);r.update(raw=str(f.relative_to(B/folder)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),status='machine_acquired_unreviewed')
  if pdf:
   doc=PdfReader(io.BytesIO(data));r['pdf_pages']=len(doc.pages);(p/(sid+'.txt')).write_text('\n'.join(f'[PDF page {i+1}]\n'+(x.extract_text()or'')for i,x in enumerate(doc.pages)))
 except Exception as e:r.update(status='failed',error=str(e)[:200])
 return folder,r
if __name__=='__main__':
 grouped={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=6)as pool:
  for folder,r in pool.map(fetch,URLS):grouped.setdefault(folder,[]).append(r);print(folder,r['id'],r['status'],r.get('pdf_pages',''))
 for folder,rows in grouped.items():(B/folder/'来源取得记录.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
