# coding: utf-8
"""037: verify a built package without depending on the author's source drive."""
import json, re, subprocess, sys, zipfile
from pathlib import Path
from urllib.parse import unquote
p=Path(sys.argv[1]).resolve()
def read(name):return json.loads((p/name).read_text(encoding='utf-8'))
checks=[]
def check(name,condition):
 assert condition,name
 checks.append(name)
for f in p.rglob('*.json'):json.loads(f.read_text(encoding='utf-8'))
check('所有JSON可解析',True)
q=subprocess.run([sys.executable,str(p/'read_example.py'),'verify'],capture_output=True,text=True)
check('文件清单逐项SHA256与大小一致',q.returncode==0)
rows=read('资料库/来源目录.json')['items'];ids={x['id']for x in rows}
check('来源ID唯一',len(ids)==len(rows))
check('来源均在当前项目归属',all(x['ownership']['scope']=='project'for x in rows))
for x in rows:
 for key in ['original','document','chunks']:
  f=(p/'资料库'/x[key]).resolve();f.relative_to(p/'资料库');check('文件存在:'+x['id']+':'+key,f.is_file())
 import hashlib
 check('原件指纹:'+x['id'],hashlib.sha256((p/'资料库'/x['original']).read_bytes()).hexdigest()==x['sha256'])
for n in ['论文原文管理/论文原件清单.json','专利原文管理/专利原件清单.json','图片素材/图片清单.json']:
 check('专用索引均指向本项目:'+n,all(x['library_source_id']in ids for x in read('资料库/'+n)['items']))
refs=read('资料库/研究来源对照.json');canonical={x['id']for x in refs}
check('来源对照不指向排除资料',all(set(x['library_source_ids'])<=ids for x in refs))
a=read('项目文档/原子字段档案.json')['records']
check('记录ID唯一',len({x['id']for x in a})==len(a))
check('所有原子字段引用均有题录',all(set(c.get('source_ids',[]))<=canonical for x in a for c in x['cells'].values()))
for n in ['overview','records','sources']:
 q=subprocess.run([sys.executable,str(p/'read_example.py'),n,'--limit','1'],capture_output=True,text=True);check('示例读取:'+n,q.returncode==0 and isinstance(json.loads(q.stdout),dict))
q=subprocess.run([sys.executable,str(p/'read_example.py'),'source','--id',rows[0]['id'],'--limit','1'],capture_output=True,text=True);check('来源分块可读取',q.returncode==0 and len(json.loads(q.stdout)['data'])<=1)
for args in [['source','--id','../../README'],['sources','--limit','999'],['sources','--offset','-1']]:
 q=subprocess.run([sys.executable,str(p/'read_example.py')]+args,capture_output=True,text=True);check('拒绝非法读取:'+str(args),q.returncode!=0)
for folder in ['项目文档','应用试验']:
 for f in (p/folder).glob('*.html'):
  for ref in set(re.findall(r'(?:href|src)=[\"\']([^\"\']+)',f.read_text())):
   if ref.startswith(('#','https:','http:','data:','javascript:')):continue
   t=unquote(ref.split('?')[0].split('#')[0])
   if t:check('阅读器相对链接:'+t,(f.parent/t).is_file())
check('导出目录元信息无本机绝对路径','/Volumes/'not in(p/'资料库/来源目录.json').read_text()and'/Users/'not in(p/'资料库/来源目录.json').read_text())
with zipfile.ZipFile(str(p)+'.zip')as z:
 check('ZIP完整性',z.testzip()is None)
 check('ZIP无越界路径',all(not Path(x).is_absolute()and'..'not in Path(x).parts for x in z.namelist()))
 check('ZIP文件数一致',len(z.namelist())==len(read('文件清单.json')['files'])+1)
print(json.dumps({'status':'passed','assertions':len(checks),'project_sources':len(rows),'records':len(a),'notes':['校验不等于资料语义审核','未运行真实LLM、在线MCP或第三方应用demo']},ensure_ascii=False,indent=2))
