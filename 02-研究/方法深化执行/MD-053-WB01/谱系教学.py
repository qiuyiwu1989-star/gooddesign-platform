# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy,hashlib
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
base={'origin':'versioned_primary_source_scope_ledger_not_author_algorithm','nodes':[{'id':'W2003','year':2003,'source':'WEN2003','scope':'PDF1 abstract and PDF5-7 section3 selected','terms':['dynamic_optimization','intelligent_design','visualization'],'identity':'three_fold_design_means_not_four_project_stages'},{'id':'W2008-CANDIDATE','year':None,'source':None,'scope':'task_card_bibliographic_target_not_verified_primary_edition','terms':[],'identity':'pending_book_identity_and_fulltext'},{'id':'W2017','year':2017,'source':'HEP2017','scope':'publisher bibliographic record and chapter directory only','terms':['research_and_topic','planning','implementation','inspection_assessment'],'identity':'book_organization_not_full_chapter_read'},{'id':'W2019','year':2019,'source':'NEU2019','scope':'author_self_description_case3 items5-8','terms':['3I','7D','1+3+X','5A'],'identity':'self_description_not_independent_effectiveness_evaluation'}],'claimed_edges':[],'platform_plan':[{'task':'inspect user/environment/risk questions','routing':'WB02 with chapter limits'},{'task':'plan scope and methods','routing':'WB03 not yet executed here'},{'task':'study selected functional/performance route','routing':'WB04 etc not yet executed here'},{'task':'review evidence gaps','routing':'WB10 etc not yet executed here'}],'merge_as_one_original_algorithm':False,'efficacy_confirmed':False}
EXP=copy.deepcopy(base)
def check(i):
 if i['origin']!=EXP['origin']or i['nodes']!=EXP['nodes']:raise ValueError('source_identity_year_scope_or_terms_changed')
 if i['claimed_edges']or i['merge_as_one_original_algorithm']or i['efficacy_confirmed']:raise ValueError('unsupported_lineage_or_effectiveness')
 if i['platform_plan']!=EXP['platform_plan']:raise ValueError('platform_route_changed_or_attributed_to_author')
 return {'literature_layers':i['nodes'],'historical_order_not_causal_derivation':True,'missing_source_targets':['2008 candidate edition identity/primary catalogue','2008 full text','2017 method chapters'],'usable_scope':'retain distinct source versions plus explicitly platform-authored research orchestration','platform_plan':i['platform_plan'],'completed_author_algorithm':False,'engineering_or_expert_validation':False}
put('01-版本节点与定位输入.json',base);put('02-不混写谱系与平台编排.json',check(base));cases=[]
def t(n,k,mut,exp):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':n,'class':k,'input':q,'output':o,'actual':state,'expected':exp,'pass':state==exp})
t('normal_distinct_versions','正常',lambda x:None,'accepted');t('invent_2008_full_read','缺材料',lambda x:x['nodes'][1].update(scope='fulltext_read'),'rejected');t('2003_contains_four_stage','冲突',lambda x:x['nodes'][0]['terms'].append('3I'),'rejected');t('chronology_as_proved_evolution','边界',lambda x:x['claimed_edges'].append({'from':'W2003','to':'W2019','type':'proved_derivation'}),'rejected');t('selfreport_as_independent_effect','不适用',lambda x:x.update(efficacy_confirmed=True),'rejected');t('merged_algorithm','冲突',lambda x:x.update(merge_as_one_original_algorithm=True),'rejected');t('directory_as_full_chapter','缺材料',lambda x:x['nodes'][2].update(scope='full_chapter_read'),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-另一情境迁移.json',{'context':'document archive platform research','platform_suggestion':['investigate needs/environment/risk','plan roles/versioning','implement selected route','review evidence'],'author_claim':'none; this mapping is platform adaptation','original_algorithm_executed':False,'actual_scope':'desktop orchestration map only'})
print('WB01:7 fixed provenance checks passed')
