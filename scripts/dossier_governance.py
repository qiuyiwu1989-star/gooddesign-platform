# coding: utf-8
"""Local dossier quality metrics and immutable, reasoned research revisions (015)."""
import argparse,copy,datetime,hashlib,json,re,shutil,tempfile
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
def read(p):return json.loads(p.read_text())
def encode(v):return (json.dumps(v,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
def digest(v):return hashlib.sha256(encode(v)).hexdigest()
def save(p,v):p.write_bytes(encode(v))
def quality(p):
 d=read(p/'原子字段档案.json');s=read(p/'字段规范.json');basis=read(p/'质量评估依据.json')
 F={f['key']:f for f in s['fields']};by_entity=[]
 for en in s['entities']:
  records=[r for r in d['records'] if r['entity']==en['key']]
  cells=[c for r in records for c in r['cells'].values()]
  p0=[c for r in records for n,c in r['cells'].items() if F[r['entity']+'.'+n]['priority']=='P0']
  known=sum(c['value_state']=='known' for c in cells);p0_known=sum(c['value_state']=='known' for c in p0)
  by_entity.append(dict(entity=en['key'],label=en['label'],records=len(records),slots=len(cells),known=known,coverage=round(100*known/len(cells),1) if cells else None,p0_slots=len(p0),p0_known=p0_known))
 cells=[c for r in d['records'] for c in r['cells'].values()];states=dict(Counter(c['value_state'] for c in cells))
 known=[c for c in cells if c['value_state']=='known']
 assert sum(x['weight'] for x in basis['dimensions'])==100
 dimensions=[]
 for item in basis['dimensions']:
  assert item['level'] is None or (type(item['level']) is int and 0<=item['level']<=4)
  assert item['rationale'] and item['evidence_files'] and item['next_actions']
  for f in item['evidence_files']:assert (p/f).exists(),f
  dimensions.append(dict(item,points=item['weight']*item['level']/4 if item['level'] is not None else None))
 report=dict(policy_version=basis['policy_version'],assessment_type='platform_document_self_assessment_not_expert_review',assessed_by=basis['assessed_by'],as_of=basis['as_of'],score=sum(x['points'] for x in dimensions) if all(x['points'] is not None for x in dimensions) else None,max_score=100,grade=None,grade_reason='试行量规未校准，不自动授予S/A/B等级',dimensions=dimensions,metrics=dict(record_count=len(d['records']),registered_slots=len(cells),known_slots=len(known),registration_coverage=round(100*len(known)/len(cells),1),value_states=states,known_with_source_or_derivation=sum(bool(c['source_ids'] or c.get('derivation')) for c in known),per_entity=by_entity),gates={'expert_review_complete':d['professional_reviewed'],'project_asset_list_confirmed':False,'full_research_complete':False},limits=['得分是有依据的平台自评，权重尚待跨案例校准；不是技术或获奖水平评分','登记覆盖率只评价现有记录槽位，不代表所有应有资料或质量','更多资料不保证升分；冲突、删除与纠错必须重新评估','数据谱系和来源字段存在不代表事实已独立核实'])
 save(p/'质量评估.json',report);return report

def capture(p):
 names={'evidence':'档案数据.json','document':'主档案结构.json','atomic':'原子字段档案.json','search_log':'研究日志.json','field_schema':'字段规范.json','quality_basis':'质量评估依据.json','quality':'质量评估.json'}
 result={k:read(p/n) for k,n in names.items()}
 if (p/'阅读内容.json').exists():result['reader_content']=read(p/'阅读内容.json')
 result['source_cards']={f.stem:f.read_text() for f in sorted((p/'来源卡').glob('*.md'))}
 for key in ['evidence','atomic']:
  sequences=[result[key]['records']] if key=='atomic' else [v for v in result[key].values() if isinstance(v,list) and v and isinstance(v[0],dict) and 'id' in v[0]]
  for rows in sequences:
   assert all('id' in r for r in rows),f'missing record id: {key}'
   ids=[r['id'] for r in rows];assert len(ids)==len(set(ids)),f'duplicate ids: {key}'
 return result

def normalized(value):
 if isinstance(value,list):
  if value and all(isinstance(x,dict) for x in value):
   for key in ['id','key']:
    if all(key in x for x in value) and len({x[key] for x in value})==len(value):return {x[key]:normalized(x) for x in value}
  return [normalized(x) for x in value]
 if isinstance(value,dict):return {k:normalized(v) for k,v in value.items()}
 return value

def differences(old,new,path=''):
 out=[]
 if isinstance(old,dict) and isinstance(new,dict):
  for key in sorted(old.keys()|new.keys()):
   pointer=path+'/'+str(key).replace('~','~0').replace('/','~1')
   if key not in old:out.append(dict(operation='add',path=pointer,before=None,after=new[key]))
   elif key not in new:out.append(dict(operation='remove',path=pointer,before=old[key],after=None))
   else:out.extend(differences(old[key],new[key],pointer))
 elif old!=new:out.append(dict(operation='replace',path=path,before=old,after=new))
 return out

def verify(p):
 folder=p/'版本';index=read(folder/'版本索引.json') if (folder/'版本索引.json').exists() else {'versions':[],'latest':None}
 previous=None
 for entry in index['versions']:
  version=entry['version'];manifest=read(folder/version/'manifest.json');assert digest(manifest)==entry['manifest_sha256'],'manifest corrupt';bundle=read(folder/version/'snapshot.json');changes=read(folder/version/'changes.json')
  assert manifest['version']==version and manifest['snapshot_sha256']==entry['snapshot_sha256']==digest(bundle),'snapshot corrupt'
  assert manifest['changes_sha256']==digest(changes),'changes corrupt'
  assert manifest['parent']==previous,'broken parent chain'
  if previous:
   prior=read(folder/previous/'snapshot.json');assert changes==differences(normalized(prior),normalized(bundle)),'invalid changes'
  else:
   assert manifest['change_kind']=='governance_baseline','first revision must be baseline'
   assert changes==differences({},normalized(bundle)),'invalid baseline changes'
  assert manifest['operations']==dict(Counter(c['operation'] for c in changes)),'incorrect operation counts'
  previous=version
 assert index['latest']==previous,'latest inconsistent'
 return index

def snapshot(p,version,reason,actor):
 if not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('version must be X.Y.Z')
 if not reason.strip() or not actor.strip():raise ValueError('reason and actor required')
 folder=p/'版本';folder.mkdir(exist_ok=True);index=verify(p);bundle=capture(p)
 target=folder/version
 if target.exists():
  assert read(target/'manifest.json')['snapshot_sha256']==digest(bundle),'version exists with different content; use a new version'
  assert any(x['version']==version for x in index['versions']),'orphan revision requires repair'
  return read(target/'manifest.json')
 if index['latest']:
  assert tuple(map(int,version.split('.')))>tuple(map(int,index['latest'].split('.'))),'version must increase'
  prior=read(folder/index['latest']/'snapshot.json')
  if digest(prior)==digest(bundle):return read(folder/index['latest']/'manifest.json')
 else:prior={}
 changes=differences(normalized(prior),normalized(bundle));counts=dict(Counter(c['operation'] for c in changes))
 manifest=dict(version=version,parent=index['latest'],change_kind='research_update' if index['latest'] else 'governance_baseline',reason=reason,actor=actor,recorded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),snapshot_sha256=digest(bundle),changes_sha256=digest(changes),operations=counts,source_count=len(bundle['evidence']['sources']),note='首次快照是当前治理基线，不追造此前研究历史；增删改含元信息，不等同于新增事实数量')
 # Build on the same disk, then rename a complete revision into place.
 with tempfile.TemporaryDirectory(prefix='.revision-',dir=str(folder)) as temp:
  t=Path(temp);save(t/'snapshot.json',bundle);save(t/'changes.json',changes);save(t/'manifest.json',manifest);t.rename(target)
 index['versions'].append({'version':version,'snapshot_sha256':digest(bundle),'manifest_sha256':digest(manifest)});index['latest']=version
 temp=folder/'.index-new.json';save(temp,index);temp.replace(folder/'版本索引.json');return manifest

def render(p):
 import html
 e=lambda x:html.escape(str(x))
 q=read(p/'质量评估.json');index=verify(p);v=read(p/'版本'/index['latest']/'manifest.json') if index['latest'] else None
 def number(x):return '待评估' if x is None else f'{x:g}'
 rows=''.join(f'<tr><td>{e(x["label"])}</td><td>{number(x["level"])}/4</td><td>{number(x["points"])}/{x["weight"]}</td><td>{e(x["rationale"])}</td></tr>' for x in q['dimensions'])
 history=''.join(f'<li>{e(x["version"])}：{e(read(p/"版本"/x["version"]/"manifest.json")["reason"])} · <a href="版本/{e(x["version"])}/manifest.json">版本说明</a> · <a href="版本/{e(x["version"])}/changes.json">增删改明细</a></li>' for x in index['versions'])
 return f'''<div class="governance-note"><b>档案质量自评：{number(q['score'])}/100</b> · 试行量规，待专业审核<br>数据登记覆盖：{q['metrics']['known_slots']}/{q['metrics']['registered_slots']}（{q['metrics']['registration_coverage']}%）。覆盖仅针对已建记录，不表示资料穷尽。<br>当前研究版本：{e(v['version'] if v else '尚未冻结')}；字段规范、网页版本、研究内容版本分别管理。</div><details class="record-library"><summary>查看评分依据、缺口与版本记录</summary><p class="small">本评分评价档案研究质量，不评价项目技术优劣。证据不足可降分，内容增多不自动升分。</p><div class="table-wrap"><table><thead><tr><th>维度</th><th>等级</th><th>得分/权重</th><th>依据与限制</th></tr></thead><tbody>{rows}</tbody></table></div><ul>{history}</ul><p><a href="质量评估.json">质量评估与下一步</a> · <a href="版本/版本索引.json">全部内容版本</a></p></details>'''

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('command',choices=['quality','snapshot','verify']);parser.add_argument('--case',type=Path,default=DEFAULT);parser.add_argument('--version');parser.add_argument('--reason',default='');parser.add_argument('--actor',default='')
 args=parser.parse_args()
 if args.command=='quality':result=quality(args.case);print(json.dumps({'score':result['score'],'metrics':{k:v for k,v in result['metrics'].items() if k!='per_entity'}},ensure_ascii=False))
 elif args.command=='verify':print(json.dumps(verify(args.case),ensure_ascii=False))
 else:print(json.dumps(snapshot(args.case,args.version or '',args.reason,args.actor),ensure_ascii=False))
