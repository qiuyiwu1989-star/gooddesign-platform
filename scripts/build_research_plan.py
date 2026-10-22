# coding: utf-8
"""047: private, live-derived project research plan. Does not launch agents or fetch URLs."""
import argparse,datetime
from pathlib import Path
import project_pipeline as pp
import project_ownership as own
import research_workflow as rw
PRIORITY=['2025-00','2015-02','2017-01','2019-s10','2021-00','2021-01','2021-02','2025-02']
CHECKPOINTS=['核对获奖对象与边界','回收旧原件及归属核定','联网获取一手材料','清洗与证据提炼','事实复核与有界AI解读','版本/导读/评估验收']
def build(lib=pp.LIB,root=pp.ROOT,output=None):
 lib,root=Path(lib),Path(root);output=Path(output)if output else root/'04-知识库/历史素材登记/深研计划'
 catalog=pp.load(lib/'项目索引.json')['projects'];old=root/'99-历史项目快照/good-design/.build/enrich.json';links=pp.load(old)if old.exists()else{}
 rows=[]
 for item in catalog:
  pid=item['id'];p=pp.project(lib,pid);state=pp.state(p);reg=own.registry(p);active=own.select(p,state['sources'],reg=reg)
  w=rw.current(p);revision='research-%06d'%w['revision']if w['revision']else None
  candidates=[];seen=set()
  for link in links.get(pid,[]):
   url=link.get('url','')
   if not isinstance(url,str)or not url.startswith(('https://','http://'))or url in seen:continue
   candidates.append(dict(url=url,legacy_title=str(link.get('title','')),status='legacy_link_unverified_not_fetched_by_this_plan'));seen.add(url)
  rank=PRIORITY.index(pid)if pid in PRIORITY else 100
  rows.append(dict(project_id=pid,title=item['name'],catalog_year=item.get('year'),catalog_award=item.get('award'),catalog_status='legacy_unverified_unless_separately_evidenced',priority=rank,lane='维护既有研究'if rank<4 else'首批新例'if rank<6 else'下一批候选'if rank<8 else'待排期',status='research_version_available_not_complete'if revision else'catalog_only_not_deep_researched',research_revision=revision,registered_sources=len(state['sources']),project_scoped_sources=len(active),original_source_files=sum(x.get('origin',{}).get('kind')not in ('project_source_excerpt','project_json_row')for x in active.values()),legacy_url_candidates=candidates,next_checkpoint='复核缺口/原始验证/权利；保留既有版本'if revision else'先核获奖对象，再回收旧料/核验候选URL',reader_url='http://127.0.0.1:8776/dossier/?project='+pid,expert_reviewed=False,full_research_complete=False))
 rows.sort(key=lambda r:(r['priority'],-len(r['legacy_url_candidates']),r['project_id']))
 report=dict(schema='project-research-plan-1.0',generated_at=pp.now(),mode='planning_only_not_background_research_scheduler',max_new_projects_in_progress=2,checkpoints=CHECKPOINTS,summary=dict(projects=len(rows),with_research_versions=sum(bool(r['research_revision'])for r in rows),catalog_only=sum(not r['research_revision']for r in rows),with_legacy_links=sum(bool(r['legacy_url_candidates'])for r in rows),legacy_link_candidates=sum(len(r['legacy_url_candidates'])for r in rows)),projects=rows)
 output.mkdir(parents=True,exist_ok=True);stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');pp.save(output/'快照'/f'{stamp}.json',report);pp.save(output/'项目深研队列.json',report)
 text=['# 项目深研队列','','此表是工作计划和读取时的实际状态，不是持续联网调度器。旧链接尚未核验，研究版不等于完成或专家通过。','',f"共{len(rows)}个题录；{report['summary']['with_research_versions']}个已有研究版本；其余仍待逐案深研。",'','| 顺序 | 项目 | 阶段 | 当前研究版 | 旧链接候选 |','|---|---|---|---|---|']
 for n,r in enumerate(rows,1):text.append(f"| {n} | {r['project_id']} {r['title'].replace('|','／')} | {r['lane']} | {r['research_revision']or'尚无'} | {len(r['legacy_url_candidates'])} |")
 (output/'项目深研队列.md').write_text('\n'.join(text)+'\n',encoding='utf-8');return dict(path=str(output/'项目深研队列.json'),**report['summary'])
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--library',type=Path,default=pp.LIB);a.add_argument('--root',type=Path,default=pp.ROOT);a.add_argument('--output',type=Path);v=a.parse_args();print(build(v.library,v.root,v.output))
