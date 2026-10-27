# -*- coding: utf-8 -*-
from pathlib import Path
import urllib.request,concurrent.futures,json,hashlib,html,re
D=Path(__file__).resolve().parent
S=[('GDS-PLAN','https://www.gov.uk/service-manual/user-research/plan-user-research-for-your-service',['R02','R03','R08','R09'],'Decide objectives;user groups;recruitment;rounds'),('GDS-CONTEXT','https://www.gov.uk/service-manual/user-research/contextual-research-and-observation',['R08'],'Plan/Design visits/Create discussion guide/Do research'),('GDS-INTERVIEW','https://www.gov.uk/service-manual/user-research/using-in-depth-interviews',['R09'],'Design interview;open neutral questions;real stories'),('HSE-TASK','https://www.hse.gov.uk/humanfactors/assets/docs/understanding-the-task.pdf',['R13'],'PDFp1-3 walk-through/HTA;selected not full method compendium'),('NASA-C','https://www.nasa.gov/reference/appendix-c-how-to-write-a-good-requirement/',['R48'],'C2/C3/C4 selected requirement writing, estimates and validation'),('CI-2021','https://www.christenseninstitute.org/wp-content/uploads/2021/03/Improvement_Imperative.pdf',['R09'],'PDFp9 Appendix Methodology only'),('NIST-MSA','https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc42.htm',['R07'],'Design considerations artifacts/operators/gauges/configurations')]
def get(z):
 id,url,methods,scope=z;p=D/'private-sources'/(id+('.pdf'if url.endswith('.pdf')else'.html'))
 try:
  data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45).read();p.write_bytes(data)
  if p.suffix=='.html':p.with_suffix('.txt').write_text(html.unescape(re.sub('<[^>]+>',' ',data.decode('utf8',errors='replace'))))
  return {'id':id,'url':url,'methods':methods,'selected_read_scope':scope,'sha256':hashlib.sha256(data).hexdigest(),'private_path':str(p.relative_to(D)),'status':'acquired_selected_read','retrieved':'2026-10-28','full_original_system_claimed':False}
 except Exception as ex:return {'id':id,'url':url,'methods':methods,'status':'failed','error':str(ex),'selected_read_scope':'none'}
r=list(concurrent.futures.ThreadPoolExecutor(7).map(get,S));(D/'新补证记录.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print([(x['id'],x['status'])for x in r])
