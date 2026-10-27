from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;BASE=P.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
readscopes={
'MIT-HANDBOOK':('Lead User Project Handbook, Churchill/von Hippel/Sonnack; 2009 web preface, text revisions stated 1998','PDF3前言、PDF13定义/早期购买区别、PDF17相关领域、PDF33/39/43阶段与趋势、PDF124-125访谈、PDF152-155共创安排','full_pdf_acquired_selected_pages_read'),
'MIT-OLD1988':('Urban/von Hippel author manuscript, June1986, related publication explicitly1988','PDF1身份、PDF2摘要、PDF3两特征、PDF5单案例方法/概念测试、PDF18定义不要求已创新及单例/非真实市场限制','author_manuscript_selected_pages_not_1988_journal_typeset'),
'MIT-2026':('MIT OCW Lead User Innovation Handbook 2026 case collection','Course Description：短篇案例汇编身份；不是168页原项目手册','identity_only'),
'JSSD-2014':('Hwang/Tsai/Mitsuhashi/Miyazaki2014, DOI10.11247/jssdj.61.1_27','PDF1题名/摘要，PDF4刊页30表2与相邻矛盾文字、PDF5-6样本与问卷范围；表2已视觉核对','empirical_paper_selected_sections_and_table_visual'),
'KANO-1984':('Kano/Seraku/Takahashi/Tsuji1984, DOI10.20684/quality.14.2_147','机构题录及摘要；JOURNAL RESTRICTED ACCESS，不声称全文/原表已取得','metadata_abstract_only'),
'GITLAB-PRACTICE':('GitLab Handbook Kano practice page','特性描述/定性预测试与正反问题操作；作为该组织实践，不是原理论全文','practitioner_primary_organization_page'),
'QFDI-FACTS':('QFD Institute Quick Facts','1综合系统、3产品与服务、4不等于HoQ；5后机构推广声明不当独立实证','institutional_position_selected'),
'QFDI-AHP-TUTORIAL':('QFD Institute AHP tutorial','AHP及尺度/ISO表述是机构立场；未由此宣称标准全文要求或保证效果','institutional_position_selected'),
'QFDI-WHAT':('QFD Institute What is QFD','需要展开至设计、制造与服务等组织功能的说明','institutional_position_selected'),
'QFDI-MEMBERSHIP2013':('Glenn H.Mazur2013 QFD for Membership Organizations','PDF2摘要，PDF5-9需要翻译/分层/优先级，PDF10刊页9图2视觉核对，PDF11图3用于区分不同显示值；非全调查重建','case_author_report_selected_sections_and_partial_recalculation'),
'ISO16355-CATALOG':('ISO16355-1:2021官方目录','web工具核题录/摘要；直接HTTP取得失败，未得61页标准全文','web_verified_catalog_only'),
}
claims={
'MD-011-R10':[
{'id':'C-LU01','type':'primary_method_supported','statement':'领先用户须相对具体需要趋势判断，且有显著预期收益；不等同早期购买者。','source_id':'MIT-HANDBOOK','locator':'PDF13/39','limit':'不证明任何真实候选满足条件'},
{'id':'C-LU02','type':'primary_empirical_author_statement','statement':'已开展创新不是领先用户定义的必要条件；该稿单案例和概念评价不能外推实际市场产品成效。','source_id':'MIT-OLD1988','locator':'PDF18','limit':'作者稿，不是声称完整发表版重现'},
{'id':'C-LU03','type':'platform_adaptation','statement':'以三态资格、构造证据引用和迁移状态形成保守筛选；无真实人物、市场或邀请。','source_id':None}],
'MD-012-R11':[
{'id':'C-K01','type':'metadata_abstract_supported','statement':'1984原文提出二维质量认识与类别研究；本轮未核原分类表全文。','source_id':'KANO-1984','locator':'Abstract','limit':'不据摘要编25格'},
{'id':'C-K02','type':'selected_primary_empirical_version','statement':'本包25格按2014论文PDF4表2行列转录；邻近文字称5个Q但表仅2个Q，明确采用表而保留差异。','source_id':'JSSD-2014','locator':'PDF4 Table2','limit':'不是原1984全文，也不复制其回归/客户结论'},
{'id':'C-K03','type':'platform_adaptation','statement':'完整回答对用于规则覆盖，缺答保持未知；构造夹具计数不当真实受访者分布，类别不自动转权重。','source_id':None}],
'MD-013-R12':[
{'id':'C-Q01','type':'institutional_position','statement':'QFD展开需要至组织各功能，不能以填一张HoQ代替完整工作。','source_id':'QFDI-FACTS','locator':'items1,3,4','limit':'机构方法说明不等标准全文实施'},
{'id':'C-Q02','type':'primary_author_case','statement':'2013组织案例从需要与层级进入优先级及行动；本包只复算图2显示比较值的列归一化行平均切片。','source_id':'QFDI-MEMBERSHIP2013','locator':'PDF5-10, Figure2','limit':'未得原参与者矩阵；无客户目标迁移'},
{'id':'C-Q03','type':'public_catalog_scope','statement':'ISO16355-1:2021公开题录/摘要可核，未取得完整标准。','source_id':'ISO16355-CATALOG','locator':'official catalog abstract','limit':'不以QFDI关于AHP的描述替代标准条款'},
{'id':'C-Q04','type':'platform_adaptation','statement':'需要、关系、偏好、目标与验证分层；主链全部未知不排名，单独公布公开案例复算与代数边界。','source_id':None}],
}
for folder in claims:
 p=BASE/folder;raw=json.loads((p/'来源取得记录.json').read_text());sources=[]
 for r in raw:
  if r['id']not in readscopes:continue
  title,scope,typ=readscopes[r['id']];x=dict(r,title=title,read_scope=scope,scope_type=typ,fulltext_entirely_read=False,public_raw_distribution=False)
  if r.get('raw'):assert sha(p/r['raw'])==r['sha256']
  sources.append(x)
 save(p/'来源与主张.json',{'version':'0.1.0','sources':sources,'claims':claims[folder],'source_snapshot_policy':'原始文件内部private-sources；交付只包括原创分析、定位、哈希及有限事实性表转录','not_claimed':['全部原典全文精读','独立专家认证','真实客户研究','完整标准实施']})
 method={'MD-011-R10':'R10','MD-012-R11':'R11','MD-013-R12':'R12'}[folder]
 count={'R10':7,'R11':10,'R12':12}[method]
 call={'method_id':method,'contract_status':'proposal_not_registered_mcp_tool','version':'0.1.0','inputs':['problem/version/source SHA','scope and material provenance','explicit unknowns','method-specific fixed version/criteria'],'outputs':['traceable research artifacts','intermediate judgments','unknowns and next evidence actions','input/output bindings'],'actual_local_capability':{'R10':'fixed declared two-trait qualification in constructed cases','R11':'versioned 25-answer-pair mapping, no real customer classification','R12':'unknown-preserving research deployment and separate published-case partial recalculation'}[method],'reject_or_pause':['source identity/version mismatch','unknown imputed as zero/pass','synthetic evidence promoted to field evidence','unjustified target/safety waiver'],'not_implemented':['general semantic inference','registered MCP execution','customer approval','domain expert decision'],'permission_scope':'read explicit local teaching/source materials; write own package only; no outreach, equipment or production changes'}
 save(p/'调用说明.json',call)
 save(p/'审核与版本.json',{'method_id':method,'task_id':folder,'version':'0.1.0','date':'2026-10-27','author':'function_deepening Agent','status':'ready_for_independent_agent_review_research_only','independent_agent_review':'pending','domain_expert_review':'not_performed','customer_approved':False,'engineering_validated':False,'field_research_conducted':False,'online_published':False,'new_mcp_registered':False,'fixed_check_count':count,'full_original_method_reconstruction':False,'known_limits':['first batch source guards still require separate revision; frozen teaching binding is not expert approval','fixed encoded data only, not general text interpretation','real user/population/engineering evidence missing']})
 (p/'README.md').write_text(f'''# {method} 方法深化包 · 0.1.0

入口：[研究说明](研究说明.md)、[来源与主张](来源与主张.json)、[反例与迁移](反例与迁移.md)、[调用说明](调用说明.json)、[审核状态](审核与版本.json)。

所有客户场景为构造教学，不是现场材料；原件在gitignore排除的private-sources，manifest不收原文或截图。复核尚未完成，不改原库、线上或MCP契约。

在项目根运行`python3 02-研究/方法深化执行/{folder}/构建教学包.py`可重建固定教学材料，依赖冻结共享教学输入。R12另有`公开案例局部复算.py`，只用已公开原例显示值，需内部原PDF存在。不愿读取原文者仍可审阅保存的输出与来源定位。

脚本只在自己的教学包中写文件。独立审核应先看路径并在隔离副本进行，不直接重跑覆盖原件。角色定义/分类值是构造记录或已转录规则，不是程序从任意自然语言推断。
''')
print('Source claims, proposed contracts and pending-review versions created')
