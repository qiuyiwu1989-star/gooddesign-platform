#!/usr/bin/env python3
# coding: utf-8
"""Map existing evidence to atomic records. Unknown values stay explicitly unknown."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'04-知识库/标杆案例/2025-00-嫦娥钻取采样'
d=json.loads((P/'档案数据.json').read_text());schema=json.loads((ROOT/'04-知识库/项目档案标准-v1/原子字段字典-v3.json').read_text())
entities={en['key']:en for en in schema['entities']};sources={s['id']:s for s in d['sources']};records=[]
def record(entity,id,title,vals,sids=(),claims=(),locator=None,narrative=(),nature='source_statement',states=None):
 known={f['name'] for f in entities[entity]['fields']};assert set(vals)<=known,(entity,set(vals)-known)
 cells={}
 for f in entities[entity]['fields']:
  value=vals.get(f['name']);vstate='known' if value is not None else (states or {}).get(f['name'],'not_researched')
  cells[f['name']]=dict(value=value,value_state=vstate,source_ids=list(sids) if value is not None else [],claim_ids=list(claims) if value is not None else [],locator=locator or ('；'.join(sources[s]['locator'] for s in sids) if sids else ''),content_nature=nature,verification_state='source_read_pending_review' if value is not None and sids else 'platform_metadata' if value is not None else 'pending')
 r=dict(id=id,project_id='2025-00',entity=entity,title=title,cells=cells,narrative_refs=list(narrative));records.append(r);return r
record('project','PRJ-2025-00','项目身份',dict(project_id='2025-00',canonical_name=d['title'],scope_included=d['scope']['included'],scope_excluded=d['scope']['excluded']),sids=['S01'],claims=['C01'],narrative=['F001','F004'],nature='platform_metadata')
# Scope is a platform research decision, not an award statement.
for k in ['scope_included','scope_excluded']:
 records[-1]['cells'][k]['content_nature']='platform_analysis';records[-1]['cells'][k]['claim_ids']=[]
record('award','AWD-2025-10','2025年第十届好设计奖金奖',dict(award_name='好设计奖',year=2025,edition=10,level='金奖',organizer='中国机械工程学会',official_number='12025070107',completion_org_ids=['ORG-01','ORG-02'],proof_source_ids=['S01']),['S01'],['C01','C02'],locator='官方获奖名单第1页金奖首行',narrative=['F002','F003'])
# The organizer is the document issuer in this archive, not a broader inferred institutional role.
records[-1]['cells']['organizer']['locator']='名单发布网站为中国机械工程学会；主办背景见S17';records[-1]['cells']['organizer']['source_ids']=['S17'];records[-1]['cells']['organizer']['claim_ids']=[]
for i,name in enumerate(d['award']['organizations'],1):
 record('organization',f'ORG-{i:02d}',name,dict(name_original=name,name_canonical=name,project_role='获奖完成单位',role_evidence='2025年第十届金奖官方名单'),['S01'],['C02'],narrative=['F003','F031'])
record('person','PER-01','报道涉及：邓宗全',dict(name='邓宗全',project_role='校方报道中的月背采样多学科团队牵头人',role_source_ids=['S03']),['S03'],['C19'],narrative=['F030'])
record('problem','NEED-01','未知环境中的可靠采样',dict(title='未知月壤与工程约束下的钻取采样',scenario='月球深层月壤取样',goal='获取并保护有层序信息的样品',constraints=['月壤特性不确定','极端环境','重量/功耗/空间限制','地月通信条件']),['S02','S03'],['C04','C05'],narrative=['F005','F006','F007'],nature='platform_analysis')
record('technology','TECH-01','双管与软袋取芯',dict(name='双管与内翻软袋取芯技术路线',function='钻进及样心收集',principle='以软袋内翻包裹样心，减少相对滑移',materials=['取芯软袋相关柔性材料'],interfaces='钻具、芯管、软袋及提芯/封口之间的配合'),['S07','S12'],['C05'],narrative=['F009','F011'],nature='platform_analysis')
for i,m in enumerate(d['metrics'],1):
 c=next(c for c in d['claims'] if c['id']==m['claim_id'])
 record('metric',m.get('id',f'MET-{i:02d}'),m['scope']+' / '+m['metric'],dict(name=m['metric'],subject=m.get('subject','整任务' if 'mission_context' in m['scope'] else '钻取子系统'),version_id=m['scope'],value=m['value'],unit=m['unit'].split('，')[0],qualifier=m.get('qualifier','约' if m['claim_id']=='C08' else '原文未另列范围'),value_kind=m.get('value_kind','公告披露' if 'mission_context' in m['scope'] else '项目官网披露'),conditions=m.get('conditions'),original_statement=c['value']),c['source_ids'],[c['id']],locator=m.get('locator',c['locator']),narrative=['F021' if 'mission_context' in m['scope'] else 'F022' if '论文' in m.get('value_kind','') else 'F020'])
for k in d['knowledge']:
 record('innovation',k['id'],k['title'],dict(title=k['title'],baseline=k.get('baseline'),measure=k['measure'],mechanism=k['mechanism'],tradeoffs=k['tradeoffs'],applicable_conditions=[k['boundary']],failure_boundary=k['boundary']),k['source_ids'],k['claim_ids'],narrative=[{'K01':'F015','K02':'F016','K03':'F017','K04':'F018','K05':'F008','K06':'F018'}[k['id']]],nature='platform_analysis')
a_publications={'P01':'CN102720501A','P02':'CN102721572A','P03':'CN104062141A','P04':'CN107503698A','P05':'CN109323884A','P06':'CN102745364A'}
public_dates={'P01':'2012-10-10','P02':'2012-10-10','P03':'2014-09-24','P04':'2017-12-22','P05':'2019-02-12','P06':'2012-10-24'}
for p in d['patents']:
 vals=dict(title=p['title'],application_number=p['application_number'],publication_number=a_publications[p['id']],grant_number=p['publication'] if p['publication'].endswith('B') else None,jurisdiction='CN',filing_date=p['filing_date'],publication_date=public_dates[p['id']],grant_date=p['grant_publication_date'],publication_holder=p['publication_holder_zh'],project_relation='技术候选，待项目方确认',relation_evidence=p['relationship_evidence'],innovation_ids=p['mechanism_ids'])
 if p['id'] in ['P04','P05']:vals['patent_type']='发明';vals['claims_locator']='原始授权公开文本第2页起，权利要求1'
 if p['id']=='P04':vals['inventors']=['邓宗全','梁杰能','马超','蒙承奇','姜生元','陈明']
 r=record('patent',p['id'],p['title'],vals,p['source_ids'],locator='文献著录Info、Other versions与Publications；原始文本已核读时以首页(21)/(22)/(65)/(73)为准',narrative=['F026'],states={'current_holder':'not_obtained','legal_status':'not_obtained','family_id':'not_obtained'})
 for key in ['project_relation','relation_evidence','innovation_ids']:r['cells'][key]['content_nature']='platform_analysis'
 for key in ['publication_number','publication_date']:
  r['cells'][key]['locator']='已核读文献的Other versions/Publications；S10、S11原始文本首页(65)/(43)'
for p in d['papers']:
 vals=dict(title=p['title'],authors=p['authors'],year=p['year'],doi=p['doi'],url=sources[p['source_ids'][0]]['url'],reading_scope='全文文字及关键表格' if p['read_scope']=='full_pdf_text_and_tables' else '全文文字' if p['read_scope']=='full_article_text' else '摘要',project_relation={'direct_technical_relation_not_award_list_confirmed':'技术相关，未确认获奖清单归属','external_technical_reference':'外部技术参照','task_related_not_award_list_confirmed':'任务相关，获奖清单归属待确认'}[p['relation']])
 if p['id']=='A01':vals.update(venue='北京航空航天大学学报',volume='41',issue='11',pages='2052—2060',online_date='2015-02-25',method='模拟月壤钻进试验及取心率模型',findings='平均误差率小于5%，仅限文中工况')
 if p['id']=='A02':vals.update(venue='中国空间科学技术',volume='32',issue='6',pages='16—22',online_date='2012-12-25')
 for key in ['venue','volume','issue','pages','affiliations','research_question','method','findings']:
  if key in p:vals[key]=p[key]
 r=record('paper',p['id'],p['title'],vals,p['source_ids'],locator='1024页题录、正文第3—5节及表4' if p['id']=='A04' else '发布页题录、DOI与摘要；A01原文第3.2节与文末书目信息',narrative=['F027'])
 r['cells']['project_relation']['content_nature']='platform_analysis';r['cells']['project_relation']['verification_state']='analysis_pending_review'
 if p.get('bibliography_source_id'):
  for key in ['year','venue','volume','issue','pages']:
   r['cells'][key]['source_ids']=[p['bibliography_source_id']];r['cells'][key]['locator']=p['bibliography_locator']

for i,(kind,count,unit) in enumerate([('发明专利',50,'件'),('论文',60,'篇'),('软件著作权',1,'项'),('专著',2,'部')],1):
 record('achievement',f'OUT-{i:02d}','官网披露：'+kind,dict(kind=kind,title='项目官网披露的'+kind+'总量',count=count,count_unit=unit,count_basis='项目官网累计披露，未取得逐项清单及统计截止时间',item_list_obtained=False,review_status='已核读来源陈述，未逐项核对'),['S02'],['C15'],narrative=['F025'])
for ev in d['events']:
 record('event',ev['id'],ev['title'],dict(title=ev['title'],date=ev['date'],date_precision=ev['date_precision'],entity_scope=ev['scope'],occurrence='已发生（按来源记录）',result=ev['detail']),ev['source_ids'],narrative=['F034'])
for v in d['validations']:
 record('validation',v.get('atomic_id','TEST-01'),v.get('title','2015年模拟取心率模型验证'),dict(title=v.get('title','2015年模拟取心率模型验证'),objective='对比模型或控制方式在来源工况中的表现',version_id='2015 HIT-2' if v['id']=='V01' else '2025论文样机试验',material_apparatus=v['material']+'；'+v['apparatus'],method=v['method'],control=v['baseline'],metric_ids=v['metric_ids'],result=v['result'],limitations=v['limitations']),v['source_ids'],v['claim_ids'],narrative=['F022','F023'])
for i,(version,cids,sid) in enumerate([('嫦娥五号',['C06','C08'],'S04'),('嫦娥六号',['C07','C09'],'S05')],1):
 record('application',f'APP-{i:02d}',version+'任务应用',dict(scenario='月球采样任务背景',version_id=version,status='历史任务应用有公开来源',limitations='整任务结果与钻取系统贡献分别记录，不能据此推定商业化收益'),[sid,'S02'],cids,narrative=['F020','F021'])
for st in d['stories']:
 record('story',st['id'],st['title'],dict(title=st['title'],narrative=st['narrative'],interview_status='公开报道梳理；本轮未访谈'),st['source_ids'],st['claim_ids'],narrative=['F037' if st['id']=='H02' else 'F036'],nature='source_statement' if st['nature']=='source_summary' else 'platform_analysis')
for s in d['sources']:
 record('source',s['id'],s['title'],dict(title=s['title'],publisher=s.get('publisher'),sha256=s.get('sha256'),local_path=s.get('internal_path'),source_type=s['type'],url=s['url'],published_at=s['published_at'],accessed_at=s['accessed_at'],reading_scope=s['read_scope'],locator=s['locator'],rights=s['rights'],visibility='公开资料元信息与研究摘要'),[s['id']],locator=s['locator'],narrative=['F044'],nature='platform_metadata')
for t in d['tasks']:
 record('task',t['id'],t['title'],dict(title=t['title'],task_type='补证或核验',priority=t['priority'],status='尚未派发',acceptance=t['acceptance']),narrative=['F048'],nature='platform_metadata')
# Auto-computed facts have their derivation saved, not an invented original source.
for r in records:
 for key,c in r['cells'].items():
  if c['value'] is not None and not c['source_ids']:c['derivation']='本平台已有研究任务记录；不是项目方提供的事实。'
  c['valid_as_of']=None  # Source access date is not the fact validity date.
  c['visibility']='internal_research'  # Public source does not automatically authorize republishing assets.
  if c['value'] is not None:assert c['source_ids'] or c.get('derivation')
  assert set(c['source_ids'])<=sources.keys()
assert len({r['id'] for r in records})==len(records)
D=dict(version='atomic-case-3.0',project_id='2025-00',research_as_of=d['as_of'],schema_file='../../项目档案标准-v1/原子字段字典-v3.json',records=records,counts={'patent_reported':50,'patent_records_found':6,'patent_project_confirmed':None,'papers_reported':60,'paper_records_found':len(d['papers']),'paper_full_text_read':sum(p['read_scope'].startswith('full_') for p in d['papers']),'paper_abstract_read':sum(p['read_scope']=='abstract_only' for p in d['papers'])},count_rules={'reported':'S02/C15项目披露，未逐项清单核实','found':'本轮实际记录去重数','confirmed':'未完成项目方归属确认，保留未知，不填0'},professional_reviewed=False)
(P/'原子字段档案.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
print(len(records),'records;',sum(len(r['cells']) for r in records),'typed cells')
