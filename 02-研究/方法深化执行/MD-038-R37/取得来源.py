# -*- coding: utf-8 -*-
from pathlib import Path
import urllib.request,hashlib,json,concurrent.futures,re,html
B=Path(__file__).resolve().parent.parent
S=[('MD-038-R37','NASA-DECISION','https://www.nasa.gov/reference/6-8-decision-analysis/'),('MD-039-R38','NIST-EXAMPLE','https://www.itl.nist.gov/div898/handbook/pri/section4/pri471.htm'),('MD-039-R38','NIST-MODELCHECK','https://www.itl.nist.gov/div898/handbook/pri/section4/pri44.htm'),('MD-039-R38','CERAMIC','https://www.itl.nist.gov/div898/handbook/datasets/CERAMIC.DAT'),('MD-040-R39','NIST-TAGUCHI','https://www.itl.nist.gov/div898/handbook/pri/section5/pri56.htm'),('MD-041-R40','GSFC-HDBK-8004','https://standards.nasa.gov/sites/default/files/standards/GSFC/Baseline/0/GSFC-HDBK-8004_Approved_0.pdf')]
def fetch(t):
 n,id,u=t;d=B/n;p=d/'private-sources'/(id+('.pdf'if u.endswith('.pdf')else'.dat'if u.endswith('.DAT')else'.html'))
 data=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=50).read();p.write_bytes(data)
 if p.suffix=='.html':p.with_suffix('.txt').write_text(html.unescape(re.sub('<[^>]+>',' ',data.decode('utf8',errors='replace'))))
 return n,{'id':id,'url':u,'private_path':str(p.relative_to(d)),'sha256':hashlib.sha256(data).hexdigest(),'access_date':'2026-10-27'}
rows=list(concurrent.futures.ThreadPoolExecutor(6).map(fetch,S))
for n in set(x[0]for x in rows):
 d=B/n;(d/'.gitignore').write_text('private-sources/\n__pycache__/\n');(d/'来源取得记录.json').write_text(json.dumps([x[1]for x in rows if x[0]==n],ensure_ascii=False,indent=2))
print('acquired',len(rows))
