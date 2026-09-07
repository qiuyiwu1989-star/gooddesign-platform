"""006: Build museum curation and award comparison from preserved public archives."""
from pathlib import Path
import json, hashlib, shutil
from exhibit_content import EXHIBITS
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'99-历史项目快照/good-design/public'
ROUTES=[
 {'id':'unknown','title':'走进未知环境','audience':'初次参观 / 亲子共读','duration':'建议20分钟，可自行调整','question':'环境无法完全预知，设计怎样为任务留下余地？','stops':[
  {'id':'2025-00','look':'月壤不确定，重量和功耗却有上限，怎样安排采样？','task':'从原文找出两项环境挑战和两项资源约束，区分“想实现的目标”和“不能超出的条件”。','reflect':'地面验证可以覆盖哪些条件？仍有哪些差异？'},
  {'id':'2015-02','look':'深海任务需要哪些系统一起工作？','task':'从档案挑选一项能力，画出它依赖的设备、能源和人员条件。','reflect':'单个部件性能提高，是否足以让整个任务成功？'}]},
 {'id':'systems','title':'从部件到系统','audience':'公众 / 高中与大学研学','duration':'建议25分钟，可自行调整','question':'为什么复杂装备的“好”，需要从整个系统来理解？','stops':[
  {'id':'2015-00','look':'列车的性能由哪些设计因素共同决定？','task':'从原文提取两项性能目标，列出可能互相影响的条件；推测要与原文事实分开写。','reflect':'比较作品时，只看一个性能数字会遗漏什么？'},
  {'id':'2021-01','look':'大型能源装备如何兼顾多个系统要求？','task':'找出一个原文中的设计措施，写出“目标—措施—依据”的对应关系。','reflect':'档案里哪些是效果陈述，哪些还需要测量条件才能比较？'}]},
 {'id':'precision','title':'力量如何变得精确','audience':'工程兴趣 / 教师备课','duration':'建议25分钟，可自行调整','question':'从施加力量到稳定完成任务，还需要解决哪些问题？','stops':[
  {'id':'2023-00','look':'大型制造装备为什么需要同时关注力量与控制？','task':'阅读原文，把性能、工况和设计措施分别标出，不用额定参数直接推断加工结果。','reflect':'要判断设计是否有效，还需要什么实测资料？'},
  {'id':'2024-02','look':'关键设备的可靠工作依赖哪些条件？','task':'选一条档案描述，分别写出已知条件、未说明的条件和你想追问的问题。','reflect':'把一个行业的方法迁移到另一行业前，应先核对什么？'}]}
]
def build(pub):
 out=pub/'explore';shutil.copytree(ROOT/'extensions/public/explore',out,dirs_exist_ok=True)
 rows=[]
 for a in json.loads((SRC/'awards.json').read_text()):
  pid=a['slug'];f=SRC/f'cases/detail/{pid}.json';d=json.loads(f.read_text()) if f.exists() else {};desc=d.get('desc','').strip()
  present=bool(desc and desc not in {'无','待补充','暂无','暂无资料','无。'})
  cover=a.get('cover','');cover='/'+cover.lstrip('/') if cover and (SRC/cover.lstrip('/')).is_file() else None
  rows.append({'id':pid,'name':a['name'],'year':a['year'],'award':a['level'],'unit':a.get('unit',''),'description_status':'archive_text' if present else 'missing','excerpt':desc[:400] if present else '', 'excerpt_truncated':present and len(desc)>400,'project_url':f'/project/{pid}.html','source_url':f'/cases/detail/{pid}.json' if f.exists() else None,'lesson_url':f'/lesson/{pid}.html' if (SRC/f'lesson/{pid}.html').is_file() else None,'cover':cover,'review_status':'历史档案，未独立核验'})
 routes=json.loads(json.dumps(ROUTES,ensure_ascii=False))
 for route in routes:
  for stop in route['stops']:
   f=SRC/f"cases/detail/{stop['id']}.json";d=json.loads(f.read_bytes());excerpt=next(p for p in d['desc'].split('\n') if p.strip());stop['evidence']={'field':'desc','start':d['desc'].index(excerpt),'end':d['desc'].index(excerpt)+len(excerpt),'excerpt':excerpt,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
 exhibits=json.loads(json.dumps(EXHIBITS,ensure_ascii=False))
 for pid,exhibit in exhibits.items():
  raw=(SRC/f'cases/detail/{pid}.json').read_bytes();desc=json.loads(raw)['desc']
  for field in exhibit['fields']:
   start=desc.index(field['quote'])
   field['source']={'url':f'/cases/detail/{pid}.json','field':'desc','start':start,'end':start+len(field['quote']),'sha256':hashlib.sha256(raw).hexdigest()}
 (out/'deep.json').write_text(json.dumps(exhibits,ensure_ascii=False,indent=2))
 (out/'data.json').write_text(json.dumps({'version':'0.1','projects':rows,'routes':routes},ensure_ascii=False,indent=2))
 # Add small discovery links to original subpages; root homepage remains untouched.
 for page,href,label in [('hall.html','museum.html','主题导览：带着问题参观好设计馆'),('award.html','awards.html','奖项与作品对照：筛选档案，比较三件作品')]:
  path=pub/page
  if path.exists():
   text=path.read_text()
   if 'id="explore-entry"' not in text:
    marker='</header>' if '</header>' in text else '</nav>'
    text=text.replace(marker,marker+f'<aside id="explore-entry" style="max-width:1120px;margin:28px auto;padding:20px 28px;border-bottom:1px solid var(--line,#ddd)"><a href="explore/{href}">{label} →</a></aside>',1)
    path.write_text(text)
 return rows,routes
if __name__=='__main__':
 rows,routes=build(ROOT/'original-app/public');print(f'{len(rows)} projects; {len(routes)} routes')
