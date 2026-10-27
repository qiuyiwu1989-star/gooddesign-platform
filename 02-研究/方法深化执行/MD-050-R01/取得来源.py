# -*- coding: utf-8 -*-
from pathlib import Path
import urllib.request,hashlib,json,concurrent.futures,re,html,shutil
B=Path(__file__).resolve().parent.parent
S=[('MD-050-R01','VDI','https://www.vdi.de/en/home/vdi-standards/details/vdi-2221-blatt-1-design-of-technical-products-and-systems-model-of-product-design'),('MD-051-R04','NASA4','https://www.nasa.gov/reference/4-0-system-design-processes/'),('MD-052-R06','STAGEGATE','https://www.stage-gate.com/about/stage-gate-innovation-performance-framework/discovery-to-launch-process/'),('MD-053-WB01','NEU2019','https://neunews.neu.edu.cn/info/1002/849441.htm'),('MD-053-WB01','HEP2017','https://academic.hep.com.cn/br/CN/chapter/978-7-04-048177-8/chapter01'),('MD-054-WB02','HEPINTRO','https://xuanshu.hep.com.cn/front/book/findBookDetails?bookId=59cf87baba9eb884cf8238c4')]
def fetch(t):
 n,id,u=t;d=B/n;p=d/'private-sources'/(id+'.html')
 try:
  data=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=45).read();p.write_bytes(data);p.with_suffix('.txt').write_text(html.unescape(re.sub('<[^>]+>',' ',data.decode('utf8',errors='replace'))));return n,{'id':id,'url':u,'sha256':hashlib.sha256(data).hexdigest(),'status':'acquired_read_scope_separate'}
 except Exception as e:return n,{'id':id,'url':u,'status':'failed','error':str(e)}
rows=list(concurrent.futures.ThreadPoolExecutor(6).map(fetch,S))
for n in ['MD-050-R01','MD-051-R04','MD-052-R06','MD-053-WB01','MD-054-WB02']:
 d=B/n;(d/'.gitignore').write_text('private-sources/\n__pycache__/\n');(d/'来源取得记录.json').write_text(json.dumps([x[1]for x in rows if x[0]==n],ensure_ascii=False,indent=2))
print([(n,r['id'],r['status'])for n,r in rows])
