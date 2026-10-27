# -*- coding: utf-8 -*-
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request,json,hashlib,re
P=Path(__file__).parent
items=[('NIST-CCD','https://www.itl.nist.gov/div898/handbook/pri/section3/pri3361.htm'),('NIST-QUAD','https://www.itl.nist.gov/div898/handbook/pri/section5/pri5514.htm'),('NIST-TAGUCHI','https://www.itl.nist.gov/div898/handbook/pri/section5/pri56.htm'),('NASA-DECISION','https://www.nasa.gov/reference/6-8-decision-analysis/'),('HSE-MACH','https://www.hse.gov.uk/work-equipment-machinery/introduction.htm')]
def get(x):
 sid,url=x;r={'id':sid,'url':url,'retrieved_date':'2026-10-28','read_scope':'selected public body passages only; see manuscript citations'}
 try:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=18).read();p=P/'private-sources'/(sid+'.html');p.write_bytes(raw);p.with_suffix('.txt').write_text(re.sub('<[^>]+>',' ',raw.decode(errors='replace')));r.update(status='acquired',raw_sha256=hashlib.sha256(raw).hexdigest())
 except Exception as e:r.update(status='failed',error=str(e),fallback='web tool selected body read recorded separately; do not claim raw acquisition')
 return r
with ThreadPoolExecutor(max_workers=5)as pool:r=list(pool.map(get,items))
(P/'定向补证记录.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print([(x['id'],x['status'])for x in r])
