# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
base={'origin':'publisher_scoped_3I_roles_plus_explicit_platform_research_plan','source_version':'HEP2017 ISBN9787040481778 introduction_and_contents','known_chinese_roles':['用户需求调研','产品环境调研','产品风险调研'],'english_I_expansions':None,'chapter5_fulltext_acquired':False,'source_original_steps':None,'topic':'tapping robot research_not_customer_commission','questions':[{'id':'Q-N','role':'用户需求调研','question':'操作者/经营者在哪些具体异常与选择事件中需要帮助？','material':'event observation and interview plan','method_attribution':'platform R08/R09 adaptation not claimed WB original step','evidence_ids':[]},{'id':'Q-E','role':'产品环境调研','question':'树体/天气/作业组织/维护支持如何影响边界与使用？','material':'condition inventory and source retrieval plan','method_attribution':'platform context research adaptation','evidence_ids':[]},{'id':'Q-R','role':'产品风险调研','question':'作用越界、异常恢复或维护隔离缺口有哪些待审风险？','material':'hazard hypothesis and verification gap ledger','method_attribution':'platform R46/context and R40/R51 complementary routing not author procedure','evidence_ids':[]}],'evidence_ledger':[],'topic_selected_by_customer':False,'priority_rank':None}
EXP=copy.deepcopy(base)
def check(i):
 for k in ['origin','source_version','known_chinese_roles']:
  if i[k]!=EXP[k]:raise ValueError('verified_Chinese_roles_or_source_changed')
 if i['english_I_expansions']is not None or i['chapter5_fulltext_acquired']or i['source_original_steps']is not None:raise ValueError('unread_chapter_or_guessed_expansion')
 if i['questions']!=EXP['questions']or i['evidence_ledger']:raise ValueError('platform_questions_or_evidence_status_changed')
 if i['topic_selected_by_customer']or i['priority_rank']is not None:raise ValueError('unsupported_customer_selection_or_ranking')
 roles={q['role']for q in i['questions']}
 assert roles==set(i['known_chinese_roles'])
 return {'role_coverage':sorted(roles),'real_evidence_count':0,'source_method_depth':'Chinese scope verified from publisher; chapter mechanics missing','research_plan':i['questions'],'missing_acquisition':[{'target':'2017 chapter5.2','scope':'needs methods/detail'},{'target':'2017 chapter5.3','scope':'environment taxonomy/detail'},{'target':'2017 chapter5.4','scope':'risk procedure/detail'}],'topic_decision':'not_ready_no_customer_material','original_3I_algorithm_executed':False,'platform_research_can_continue':'explicitly label its other method provenance'}
put('01-已核职责与平台问题输入.json',base);put('02-职责覆盖取证与选题边界.json',check(base));cases=[]
def t(n,k,mut,exp):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':n,'class':k,'input':q,'output':o,'actual':state,'expected':exp,'pass':state==exp})
t('normal_roles_known_steps_unknown','正常',lambda x:None,'accepted');t('guess_three_English_words','冲突',lambda x:x.update(english_I_expansions=['invented1','invented2','invented3']),'rejected');t('claim_chapter_read','缺材料',lambda x:x.update(chapter5_fulltext_acquired=True),'rejected');t('copy_R08_as_author_steps','不适用',lambda x:x.update(source_original_steps=['interview','code']),'rejected');t('no_risk_question','缺材料',lambda x:x['questions'].pop(),'rejected');t('customer_picked_topic','冲突',lambda x:x.update(topic_selected_by_customer=True),'rejected');t('zero_rank_is_not_unknown','边界',lambda x:x.update(priority_rank=0),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'document export application','platform_questions':{'用户需求调研':'哪次交付造成版本追问？','产品环境调研':'接收方平台/权限/网络怎样？','产品风险调研':'错版本/泄露/不可读风险怎样？'},'original_3I_steps_claimed':False,'evidence':[],'actual_scope':'desktop question map, not interviews or chapter replication'})
print('WB02:7 fixed provenance checks passed')
