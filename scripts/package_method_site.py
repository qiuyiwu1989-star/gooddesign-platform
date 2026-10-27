"""ML-013 static read-only deployment package; no DB or runtime secrets."""
import hashlib,json,re,shutil
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlsplit,unquote
from build_method_reader import page,document
from method_library_catalog import BASE,SUPPLEMENT,ROOT
OUT=ROOT/'output/method-site-release/site'
if OUT.exists():shutil.rmtree(OUT)
OUT.mkdir(parents=True,exist_ok=False)
def rewrite(text):
 text=text.replace('/library/','/inno/methods/').replace('/vendor/','/inno/methods/vendor/').replace('href="/"','href="/inno/methods/"').replace('好设计 <span>／ 创新工作台</span>','好设计 <span>／ 方法库</span>')
 text=text.replace('<header>','<header><a href="/inno/projects/">项目库</a>',1)
 return re.sub(r'(href="[^"#?]+)\.md(?=["#?])',r'\1.html',text)
for p in (ROOT/'extensions/method-reader').rglob('*'):
 if p.is_file() and p.suffix in {'.html','.svg','.css','.js'}:
  q=OUT/p.relative_to(ROOT/'extensions/method-reader');q.parent.mkdir(parents=True,exist_ok=True)
  q.write_text(rewrite(p.read_text()))
for base in [BASE,SUPPLEMENT]:
 for p in base.rglob('*'):
  if not p.is_file() or p.suffix not in {'.md','.json','.csv'}:continue
  rel=p.relative_to(base);q=OUT/rel;q.parent.mkdir(parents=True,exist_ok=True)
  if p.suffix=='.md':q=q.with_suffix('.html');q.write_text(rewrite(page(p.stem,'<main id="main" class="reader"><a href="/inno/methods/">← 方法库</a><h1>'+p.stem+'</h1><article class="document">'+document(p.read_text())+'</article></main>')))
  else:shutil.copyfile(p,q)
(OUT/'vendor').mkdir(exist_ok=True)
for name in ['tokens.css','design-system.css']:shutil.copyfile(ROOT/'extensions/method-workbench/vendor'/name,OUT/'vendor'/name)
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);v=a.get('href',a.get('src',''))
  if not v or v.startswith(('http:','https:','data:','mailto:')):return
  resolved=unquote(urlsplit(urljoin('https://opendesign.cc/inno/methods/'+str(self.file.relative_to(OUT)),v)).path)
  if resolved=='/inno/projects/':return
  if resolved in {'/inno/','/inno/projects/','/inno/report/','/inno/mcp/','/inno/admin/','/inno/about/','/inno/portal/portal.css','/inno/portal/system.css'}:return
  if not resolved.startswith('/inno/methods/'):raise ValueError(resolved)
  f=OUT/resolved[len('/inno/methods/'):];f=f/'index.html' if f.is_dir() else f
  if not f.is_file():raise ValueError(str(self.file)+' missing '+resolved)
for p in OUT.rglob('*.html'):
 a=Links();a.file=p;a.feed(p.read_text())
manifest={str(p.relative_to(OUT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.rglob('*') if p.is_file()}
(OUT.parent/'manifest.json').write_text(json.dumps(manifest,indent=2))
print('Validated files',len(manifest))
