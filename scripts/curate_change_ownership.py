# coding: utf-8
"""036 explicit curation of the known Chang'e cross-project sources; never keyword auto-labeling."""
from pathlib import Path
import copy,shutil
import project_pipeline as pp
from project_ownership import registry
ROOT=Path(__file__).resolve().parents[1]
def run():
 p=pp.project(pp.LIB,'2025-00');q=pp.project(pp.LIB,'2015-02');f=p/'资料归属.json'
 if f.exists():raise ValueError('已建立归属登记，不覆盖后续人工调整')
 case=pp.load(ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样/档案数据.json');sources=pp.state(p)['sources'];canon={x['id']:x for x in case['sources']};byurl={x['url']:x['id']for x in case['sources']}
 paperfiles=pp.load(p/'论文原文管理/论文原件清单.json')['items'];patentfiles=pp.load(p/'专利原文管理/专利原件清单.json')['items'];images=pp.load(p/'图片素材/图片清单.json')
 typed={x['library_source_id']:x['source_ids'][0]for x in paperfiles+patentfiles};image_map={x['library_source_id']:x for x in images['items']}
 rules={}
 for sid in canon:
  if sid in ['S01','S17','S18','S20']:scope,relation,owner,reason='shared','shared_background',None,'奖项名单/制度或平台产业讨论，非采样系统专属原始资料'
  elif sid=='S19':scope,relation,owner,reason='reassigned','other_project','2015-02','蛟龙号水声通信对照案例，应属于蛟龙号项目'
  elif sid in ['S06','S16']:scope,relation,owner,reason='project','team_context','2025-00','项目团队背景，不能据此确认每张配图属于本系统'
  elif sid in ['S07','S08','S09','S10','S11','S12','S13','S14','S15','S23']:scope,relation,owner,reason='project','technical_reference','2025-00','采样系统技术相关参照；正式成果归属/实际采用仍按原记录待确认'
  else:scope,relation,owner,reason='project','project_core','2025-00','项目专属任务/奖项页面或直接技术团队报道'
  rules[sid]=dict(scope=scope,relation=relation,owner_project=owner,reason=reason,curated_at=pp.now())
 assignments={}
 for sid,x in sources.items():
  origin=x.get('origin',{});cs=origin.get('canonical_source_id')or byurl.get(origin.get('url'))or byurl.get(origin.get('requested_url'))or typed.get(sid)
  if sid in image_map:continue
  assignments[sid]=copy.deepcopy(rules[cs])if cs else dict(scope='project',relation='project_record',owner_project='2025-00',reason='本项目原始登记资料',curated_at=pp.now())
 for sid,image in image_map.items():
  parents=[assignments[l['source_id']]for l in image['locations']]
  chosen=next((x for x in parents if x['scope']=='project'),parents[0]);entry=copy.deepcopy(chosen)
  if any(l['source_id']in sources and byurl.get(sources[l['source_id']].get('origin',{}).get('url'))=='S06'for l in image['locations']):entry.update(scope='pending',relation='media_relevance_pending',reason='人物综合报道配图，是否为本采样系统尚未逐图确认')
  assignments[sid]=entry
 media_rules={sid:dict(scope='pending',relation='media_relevance_pending',owner_project='2025-00',reason='人物综合报道的新配图须先确认设备归属')for sid,x in sources.items()if byurl.get(x.get('origin',{}).get('url'))=='S06'}
 reg=dict(image_parent_rules=media_rules,schema_version='project-ownership-1.0',version=1,project_id='2025-00',updated_at=pp.now(),assignments=assignments,url_rules={canon[sid]['url']:entry for sid,entry in rules.items()},note='文件归属与事实审核分离；旧原件及快照保留作历史，实时项目读取排除非本项目资料。')
 targetimages=pp.load(q/'图片素材/图片清单.json')if (q/'图片素材/图片清单.json').exists()else dict(schema_version='case-images-1.0',project_id=q.name,items=[],failed=[],skipped=[])
 transfers=[];common=[]
 with pp.lock(pp.LIB):
  targetreg=registry(q)
  for sid,entry in assignments.items():
   if entry['scope']=='reassigned':
    x=sources[sid];origin=dict(kind='ownership_transfer',filename=image_map[sid]['title']if sid in image_map else ('蛟龙号水声通信来源说明.md'if x.get('origin',{}).get('kind')=='source_reference'else '蛟龙号水声通信团队研制纪实.html'),transferred_from_project='2025-00',original_source_id=sid,original_origin=x.get('origin',{}),url=x.get('origin',{}).get('url'),reason=entry['reason'])
    result=pp.ingest(q,p/x['original'],origin);assert result['source_id']==sid
    targetreg['assignments'][sid]=dict(scope='project',relation='project_context',owner_project='2015-02',reason='从嫦娥误收对照资料纠正归属；仍待项目内容审核',curated_at=pp.now())
    if sid in image_map and not any(i['library_source_id']==sid for i in targetimages['items']):targetimages['items'].append(copy.deepcopy(image_map[sid]))
    entry.update(target_source_id=sid,transferred_at=pp.now());transfers.append(dict(source_id=sid,sha256=x['sha256'],target_project='2015-02'))
   elif entry['scope']=='shared':
    x=sources[sid];folder=pp.LIB/'公共资料/来源'/x['sha256'];folder.mkdir(parents=True,exist_ok=True)
    for key in ['original','document','chunks']:
     src=pp.safe(p,x[key]);dest=folder/src.name
     if not dest.exists():shutil.copy2(src,dest)
    meta=dict(original_metadata=x,associated_project='2025-00',relation='shared_background',reason=entry['reason']);pp.save(folder/'归属说明.json',meta);entry['shared_asset']=str(folder.relative_to(pp.LIB));common.append(dict(source_id=sid,sha256=x['sha256'],shared_asset=entry['shared_asset']))
  targetreg.update(schema_version='project-ownership-1.0',version=1,project_id=q.name,updated_at=pp.now());pp.save(q/'资料归属.json',targetreg);pp.save(q/'图片素材/图片清单.json',targetimages)
  pp.save(q/'资料关联.json',dict(source_titles={canon['S19']['url']:'蛟龙号水声通信团队研制纪实'}))
  pp.save(pp.LIB/'公共资料/清单.json',dict(version=1,items=common,updated_at=pp.now()))
  pp.save(f,reg);pp.save(p/'归属版本/ownership-000001.json',dict(registry=reg,transfers=transfers,common=common,actor='Codex依据用户纠错逐项整理',reason='隔离跨项目对照与公共背景；不改变历史事实与研究评分'))
  # New ingest revisions preserve the historical sources while refreshing live, filtered MD.
  pp.commit(p,pp.state(p),'按用户纠错整理归属，移交蛟龙号与公共参考，实时目录仅列本项目')
  pp.commit(q,pp.state(q),'纠正既有资料归属；仅接收旧资料，不开展新项目深研')
  index=pp.load(pp.LIB/'项目索引.json');catalog={x['id']:x for x in pp.load(ROOT/'original-app/public/knowledge-data/project-index.json')['projects']}
  for row in index['projects']:
   match=catalog.get(row['id'],{})
   for key in ['year','award','unit']:row[key]=match.get(key)
  pp.save(pp.LIB/'项目索引.json',index)
 print('transferred',len(transfers),'shared',len(common),'pending',sum(x['scope']=='pending'for x in assignments.values()))
 return reg
if __name__=='__main__':run()
