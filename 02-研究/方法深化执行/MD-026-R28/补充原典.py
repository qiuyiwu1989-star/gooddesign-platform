# -*- coding: utf-8 -*-
from pathlib import Path
import urllib.request,re,json,hashlib
from html import unescape
D=Path(__file__).parent
records=[]
for part in [1,2,3,6]:
 u=f'https://www.altshuller.ru/world/spa/ariz85v-{part}.asp'
 try:
  raw=urllib.request.urlopen(u,timeout=30).read(); charset=re.search(br'charset=([\w-]+)',raw[:2000],re.I);text=raw.decode(charset.group(1).decode() if charset else 'windows-1252',errors='replace');clean=unescape(re.sub('<[^>]+>',' ',text));clean=re.sub(r'\s+',' ',clean)
  p=D/'private-sources'/f'ARIZ-ES-P{part}.html';p.write_bytes(raw);p.with_suffix('.txt').write_text(clean);records.append({'id':f'ARIZ-ES-P{part}','url':u,'sha256':hashlib.sha256(raw).hexdigest(),'status':'acquired','read_scope':'selected numbered steps reviewed separately'})
 except Exception as e:records.append({'id':f'ARIZ-ES-P{part}','url':u,'status':'failed','error':str(e)})
(D/'补充来源记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
print(records)
