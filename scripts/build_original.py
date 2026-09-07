from pathlib import Path
import shutil, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'99-历史项目快照'
OUT=ROOT/'original-app'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
app=SRC/'good-design'
shutil.copy2(app/'server.js',OUT/'server.js')
for folder in ['agents','knowledge','public']:
    shutil.copytree(app/folder,OUT/folder)
pub=OUT/'public'
# Internal documents remain in the untouched historical snapshot, outside the web release.
for name in ['backstage','materials','outputs']:
    shutil.rmtree(pub/name,ignore_errors=True)
private_pages=['architecture.html','report.html','exhibition-summary.html','exhibit-guide.html']
for name in private_pages:
    (pub/name).unlink(missing_ok=True)
for f in list(pub.rglob('*')):
    if f.is_file() and (f.name.startswith('.') or f.suffix.lower() in ['.md','.pdf','.pptx','.zip','.env']): f.unlink()
shutil.copytree(SRC/'teacher-workbench',pub/'teacher-workbench',dirs_exist_ok=True)
shutil.copytree(SRC/'courseware',pub/'education-tools/courseware',dirs_exist_ok=True)
teacher=pub/'teacher-workbench/index.html'
teacher.write_text(teacher.read_text().replace('../courseware/','../education-tools/courseware/'))
for f in pub.rglob('*.md'): f.unlink()
(pub/'education-tools').mkdir(exist_ok=True)
s=(SRC/'index.html').read_text().replace('./teacher-workbench/','/teacher-workbench/').replace('./courseware/','/education-tools/courseware/')
(pub/'education-tools/index.html').write_text(s)
learn=pub/'learn.html'
text=learn.read_text()
marker='<a href="teacher-dash.html"'
pos=text.index(marker)
text=text[:pos]+'<a href="teacher-workbench/" style="padding:10px 18px;border:1px solid var(--line);border-radius:10px;text-decoration:none;color:var(--ink);background:#fff;font-size:13.5px;font-weight:600">教师备课工作台 →</a>\n        '+text[pos:]
learn.write_text(text)
server=(OUT/'server.js').read_text().replace("const dir = path.join(ROOT, '.build');", "const dir = process.env.DATA_DIR || path.join(ROOT, '.build');")
(OUT/'server.js').write_text(server)
# Maintained extensions survive rebuilds; original archive remains untouched.
shutil.copytree(ROOT/'extensions/public',pub,dirs_exist_ok=True)
connect=pub/'connect.html'
s=connect.read_text().replace('<main class="wrap">','<main class="wrap"><p style="padding:18px;border:1px solid #b9c4d0"><a href="industry-demo/">好设计 × 双环：进入产业创新研究 Demo →</a></p>',1)
connect.write_text(s)
from platform_design import apply
page_count = apply(pub)
changes=[]
for f in (app/'public').rglob('*'):
    if f.is_file():
        rel=f.relative_to(app/'public'); dst=pub/rel
        if not dst.exists(): changes.append({'path':str(rel),'status':'private-excluded'})
        elif f.read_bytes()!=dst.read_bytes(): changes.append({'path':str(rel),'status':'design-system-migration'})
assert (SRC/'good-design/public/index.html').exists()
report={'homepage_sha256':hashlib.sha256((pub/'index.html').read_bytes()).hexdigest(),'unified_html_pages':page_count,'project_pages':len(list((pub/'project').glob('*.html'))),'atom_pages':len(list((pub/'atom').glob('*.html')))-1,'public_differences':changes,'added':['teacher-workbench/','education-tools/','education-tools/courseware/ (root edition preserved separately)'],'server_change':'DATA_DIR for persistent inquiry storage'}
(ROOT/'00-项目管理/原版迁移检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='public_differences'},ensure_ascii=False))
