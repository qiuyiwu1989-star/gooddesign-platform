from pathlib import Path
import re,json
p=Path(__file__).resolve().parents[1]/'original-app/public';errors=[];pages=list(p.rglob('*.html'))
for f in pages:
 s=f.read_text()
 if s.count('id="gd-shell"')!=1:errors.append([str(f),'shell count'])
 for path in re.findall(r'href="(/[^"?#]*)',s):
  target=p/path.lstrip('/')
  if not target.exists():errors.append([str(f.relative_to(p)),path])
 for asset in ['/design/system.css','/design/shell.js']:
  if asset not in s:errors.append([str(f),'missing '+asset])
# All generated data references must resolve.
for x in json.loads((p/'design/projects.json').read_text()):
 for r in x['resources']:
  assert (p/r['path']).exists()
assert not errors, str(errors[:30])
print(f'{len(pages)} pages: unique shared shell, design assets and absolute local links passed')
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
navs=set();missing=[]
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k not in ['src','href'] or not v or v.startswith(('#','//','data:','javascript:','mailto:','tel:')):continue
   u=urlsplit(v)
   if u.scheme or '${' in v:continue
   rel=unquote(u.path)
   if not rel:continue
   t=p/rel.lstrip('/') if rel.startswith('/') else self.f.parent/rel
   if not t.exists():missing.append([str(self.f.relative_to(p)),v])
for f in pages:
 s=f.read_text();navs.add(re.search(r'<div class="gd-nav".*?</div>',s,re.S).group(0).replace(' aria-current="page"',''))
 scan=Links();scan.f=f;scan.feed(s)
assert len(navs)==1,'Navigation drift'
assert not missing,str(missing[:20])
print('Shared navigation identical; relative links and static resources passed')
