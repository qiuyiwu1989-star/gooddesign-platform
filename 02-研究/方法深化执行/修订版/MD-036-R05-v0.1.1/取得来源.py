# -*- coding: utf-8 -*-
from pathlib import Path
import urllib.request,hashlib,json,re
P=Path(__file__).parent;B=P.parent
items=[('MD-036-R05','VDI','https://www.vdi.de/mitgliedschaft/vdi-richtlinien/programme-zu-vdi-richtlinien/vdi-2206','html'),('MD-037-R47','LEI','https://www.lean.org/lexicon-terms/set-based-concurrent-engineering/','html'),('MD-037-R47','SOBEK','https://www.researchgate.net/profile/Jeffrey-Liker/publication/248139929_Toyota%27s_Principles_of_Set-Based_Concurrent_Engineering/links/54d0dfb60cf20323c21a0069/Toyotas-Principles-of-Set-Based-Concurrent-Engineering.pdf','pdf')]
for name,sid,url,ext in items:
 d=B/name;p=d/'private-sources'/f'{sid}.{ext}';record={'id':sid,'url':url,'date':'2026-10-27'}
 try:
  raw=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30).read();p.write_bytes(raw);record.update(status='acquired',sha256=hashlib.sha256(raw).hexdigest())
  if ext=='html':p.with_suffix('.txt').write_text(re.sub('<[^>]*>',' ',raw.decode(errors='replace')))
 except Exception as e:record.update(status='failed',error=str(e))
 (d/f'取得记录-{sid}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));print(record)
for n in ['MD-036-R05','MD-037-R47']:(B/n/'.gitignore').write_text('private-sources/\n__pycache__/\n')
