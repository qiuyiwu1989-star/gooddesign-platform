from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,collections,re
R=Path(__file__).resolve().parents[1];S=R/'site';bad=[];ext=set()
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src','poster') and v:self.refs.append(v)
for p in S.rglob('*.html'):
 h=Links();h.refs=[];h.feed(p.read_text())
 for val in h.refs:
  u=urlsplit(val)
  if u.scheme or u.netloc:ext.add(u.netloc);continue
  if not u.path:continue
  path=unquote(u.path);t=(S/path.lstrip('/')) if path.startswith('/') else p.parent/path
  if not t.exists():bad.append((str(p.relative_to(S)),val))
for p in S.rglob('*'):
 if p.is_file() and (p.name.startswith('.') or p.suffix in {'.pdf','.pptx','.md'} or any(x in p.parts for x in ['backstage','outputs','materials'])):raise AssertionError('private file in site: '+str(p.relative_to(S)))
a=json.loads((S/'awards.json').read_text());assert len(a)==560;assert len({x['slug'] for x in a})==560
assert all((S/'project'/f"{x['slug']}.html").exists() for x in a)
assert all((S/'atom'/f"{x['slug']}.html").exists() for x in a)
summary={'projects':len(a),'counts':dict(collections.Counter(x['level'] for x in a)),'html_pages':len(list(S.rglob('*.html'))),'broken_links':bad,'external_hosts':sorted(ext)}
(R/'00-项目管理/发布检查.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps({**summary,'broken_links':bad[:25]},ensure_ascii=False,indent=2));print('TOTAL BROKEN',len(bad));raise SystemExit(bool(bad))
