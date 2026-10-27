# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,re
D=Path(__file__).resolve().parent;R=D.parents[2];audit=json.loads((D/'质量缺口台账.json').read_text());catalog=json.loads((R/'02-研究/方法深化执行/最终收口/方法深化库索引.json').read_text());byid={m['method_id']:m for m in catalog['methods']};newsrc=json.loads((D/'新补证记录.json').read_text())+json.loads((D/'第二组补证记录.json').read_text());arch=json.loads((D/'原件选段再核读.json').read_text())
source_extra={'R10':['R10-HANDBOOK PDF13/17/124-125/152-153及新增85推荐网络'],'R11':['R11-JSSD PDF3-5，表2与问卷方法选段'],'R12':['R12-MAZUR PDF5-6及10，VOC翻译/需要与显示比值'],'R18':['BOHN2004 archive abstract wet/dry attachment passage; current live recaptcha']} 
external={
'R01':('VDI2221完整正文及目标载荷/材料/三维运动','限制完整标准细则实施和工程制造放行；不阻止本平台设计过程教学'),
'R02':('真实完整作业观察、角色与分段定义','限制真实主要负担/问题重要性，不阻止构造重定义教学'),
'R03':('目标角色任务研究、原型表达能力及实际观察','限制理解改善/使用有效结论'),
'R04':('实际系统配置、运行概念、接口和验证材料；ISO正文','限制实际架构成立及完整标准主张'),
'R05':('真实坐标标定/时基/控制权、实际停止与残能；VDI全文','限制真实接口安全与完整标准实施'),
'R06':('真实gatekeeper授权、资源与客户/技术证据','限制真实Go/投资和发布决定'),
'R07':('批准CTQ操作定义、代表性量测原始记录、规格与稳定性','限制R&R/能力/sigma计算，12格只是准备练习'),
'R08':('真实同意范围内事件原件、角色及多情境取样','限制真实需要、频率及现场因果'),
'R09':('真实选择/放弃事件和反例、角色材料及市场研究','限制真实job分群/因果、支付意愿和市场规模'),
'R10':('已证趋势、候选两资格材料、真实共创安排与使用条件','限制真实领先者资格/普适采用'),
'R11':('1984原文、真实单特性理解预测试及目标样本','限制原始全法复刻及客户类别，不影响2014所选表版本说明'),
'R12':('目标客户需要/偏好尺度、技术关系证据、目标来源；ISO全文','限制真实排序/阈值和完整标准实施'),
'R13':('目标人群、身体/认知/环境/组织数据及任务观察','限制易用/负荷/安全结论，编码差异不等理解改善'),
'R14':('目标对象/组织边界、作用模型、量纲与时序','限制功能充分性及真实闭环安全'),
'R15':('真实团队范围/功能知识与所选原理工程依据','限制图逻辑对真实任务的充分性'),
'R16':('原始事件/配置/工况、区分性证据、措施实施与可比暴露','限制真实根因/措施成效'),
'R17':('选项兼容/整体资源与生物作用条件','限制真实工程组合可行与最优，不影响形式空间演示'),
'R18':('材料对/流体/接触条件、目标试验与相关专业核查','限制目标防黏收益及工程迁移有效'),
'R48':('真实角色确认、指标对象/测量/风险判据、授权与基线','限制实际要求/验收目标，TBR估计练习不当实测')}
summary=[];maps=[]
for row in audit['methods']:
 mid=row['method_id'];m=byid[mid];p=D/'稿件'/(mid+'.md');s=p.read_text();headings=re.findall(r'^## (.+)$',s,re.M);assert len(headings)>=3
 loc=row['evidence_location'];row['dimensions_before_revision']={
  '身份与边界准确':{'level':'充分','location':m['research_document'],'reason':'底稿已区分平台适配/原典范围；本轮补阅读入口并保留来源限制'},
  '机制讲透':{'level':'局部','location':loc,'reason':row['specific_content_gap']},
  '判断可操作':{'level':'局部','location':loc,'reason':'已有原则与固定模型分支，缺面向真实执行的协议/返回工作稿'},
  '完整示范':{'level':'充分'if mid=='R17'else'局部','location':m['teaching_artifacts_directory'],'reason':'R17已有八枚举和高阶/介质例；其他主要局部案例与完整执行之间仍需正文串联'if mid=='R17'else'底稿教学可核但部分流程留附件/空表，需用完整工作链解释'},
  '反例与迁移':{'level':'局部','location':m['research_document'],'reason':'有固定反例与迁移，但需将输入门禁扩成设计判断/适用反例'},
  '依据可追溯':{'level':'充分','location':m['source_claims'],'reason':'已有来源/范围定位；不以未取得全文自动否定受限概念说明'},
  '阅读与交接':{'level':'局部','location':m['research_document'],'reason':'审计/版本信息比例偏高，下一行动与专业操作应放前面'}}
 row['manuscript_status']='rewritten_pending_independent_content_review';row['new_manuscript']='稿件/'+mid+'.md';row['new_content_locations']=headings;row['remaining_external_dependency']={'needed':external[mid][0],'affected_claim':external[mid][1]}
 # One light footer, no audit-history repetition in reader body.
 footer='\n\n---\n[教学材料与既有版本](<'+str(R/m['research_document'])+'>) · [原典主张与核读定位](<'+str(R/m['source_claims'])+'>) · [本轮补证及边界](../来源主张映射.json)\n'
 if '[教学材料与既有版本]'not in s:p.write_text(s.rstrip()+footer)
 linked=[z for z in newsrc if mid in z.get('methods',[])];maps.append({'method_id':mid,'manuscript':str(p.relative_to(D)),'new_readings':[{'source_id':z['id'],'url':z['url'],'locator':z['selected_read_scope'],'raw_sha256':z.get('sha256'),'status':z['status']}for z in linked],'archived_selected_readings':source_extra.get(mid,[]),'inherited_claim_map_path':m['source_claims'],'inherited_manifest_sha256':m['preferred_manifest_sha256'],'claim_type_rule':'institutional/original scope is cited; all protocols/ID choices and new examples are platform adaptations, not source original algorithms or field findings','new_example_type':'explicit constructed/analytical or reused lawful teaching, no new empirical participants','fulltext_limits':external[mid]})
 summary.append({'method_id':mid,'name':m['name'],'path':str(p.relative_to(D)),'source_identity_and_range':'see 来源主张映射.json','content_status':'candidate_manuscript_pending_independent_review','independent_review':None,'engineering_validated':False})
audit['final_author_status']='19 rewritten manuscripts, not independently passed';audit['no_expert_numeric_scoring']=True;(D/'质量缺口台账.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2));(D/'来源主张映射.json').write_text(json.dumps({'date':'2026-10-28','methods':maps,'rights':'raw originals/text/rendered pages private and not public manifest','archived_pdf_identities':arch},ensure_ascii=False,indent=2));(D/'未解决项.json').write_text(json.dumps({'content_review':'pending independent Agent content review; no author selfapproval of sufficient','items':[{'method':r['method_id'],**r['remaining_external_dependency']}for r in audit['methods']]},ensure_ascii=False,indent=2));(D/'版本与交付.json').write_text(json.dumps({'version':'0.1.0','round':'ML021','date':'2026-10-28','methods':summary,'counts':{'manuscripts':19,'independent_candidate_pass':0,'pending_independent_review':19,'actual_new_field_or_user_experiments':0},'not_done':['online deployment','old-package edit','production runtime changes','domain-expert certification'],'skills_used':['innolab','design:user-research']},ensure_ascii=False,indent=2))
files=[]
for p in sorted(D.rglob('*')):
 if not p.is_file()or'private-sources'in p.parts or'__pycache__'in p.parts or'独立审核-function'in p.parts or p.name=='manifest.json':continue
 if p.suffix=='.json':json.loads(p.read_text())
 files.append({'path':str(p.relative_to(D)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'manifest.json').write_text(json.dumps({'version':'0.1.0','scope':'19 authored content candidates pending independent review','exclude':['private-sources','__pycache__','独立审核-function'],'files':files},ensure_ascii=False,indent=2));print('files',len(files),'manifest',hashlib.sha256((D/'manifest.json').read_bytes()).hexdigest())
