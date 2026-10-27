from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
DIRS={'R36':D,'R44':D.parent/'MD-006-R44','R42':D.parent/'MD-007-R42'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
acq={x['id']:x for x in json.loads((D/'来源取得记录.json').read_text())}
claims={
'R36':[
 ('C36-01','MIT-CONCEPT','PDF第1页，Pugh Concept Selection开头','does not aim to','发展、组合和改进概念是该教学材料强调的用途；不保证唯一最优。','author_teaching_scope'),
 ('C36-02','MIT-DLAB','Concept Evaluation / Pugh Chart Analysis','One idea is chosen','使用datum及逐准则比较；该教程允许加权，平台不加权不是原典唯一规则。','author_teaching_scope'),
 ('C36-03','MIT-CONCEPT','PDF第1页，Design Selection列表','Reflect on results','流程包含反思；本包将更换datum作为研究敏感性检查。','author_teaching_plus_explicit_platform_adaptation'),
],
'R44':[
 ('C44-01','DS-NOBUILD','What is it? / How does it work?','These prototypes often','低保真外化用于参与和学习；不是所有原型都需要高技术构建。','author_tool_scope'),
 ('C44-02','NASA-VAL','Methods of Validation及5.4.1.2活动说明','Methods of Validation','分析、演示、检查和测试的可支持范围应区分；本包的原型能力映射是平台适配。','author_process_plus_platform_adaptation'),
],
'R42':[
 ('C42-01','NASA-VAL','5.4开头两段','intended environment','确认指向使用者期望与预期环境；要求符合性与用途满足不能混同。','author_process_scope'),
 ('C42-02','NASA-V','5.3.1.2 Conduct Planned Product Verifications','When a “discrepancy”','偏差须进入记录与分析；平台固定夹具仅检查记录结构。','author_process_plus_platform_adaptation'),
 ('C42-03','NASA-V','5.3.1.3 Outputs / Product verification work products','configuration drawings','验证产物关联配置、校准和异常记录；本包配置SHA绑定是平台实现建议。','author_process_plus_platform_adaptation'),
]}
for rid,dd in DIRS.items():
 mapped=[]
 for cid,sid,loc,anchor,claim,kind in claims[rid]:
  r=acq[sid];tp=D/'private-sources'/(sid+'.txt');text=tp.read_text();idx=text.find(anchor)
  mapped.append({'claim_id':cid,'claim':claim,'claim_type':kind,'source_id':sid,'url':r['url'],'source_raw_sha256':r['sha256'],'local_raw_path':r['raw_path'],'local_text_path':str(tp.relative_to(ROOT)),'local_text_sha256':sha(tp),'locator':loc,'short_anchor':anchor,'anchor_start_in_normalized_text':idx if idx>=0 else None,'read_scope':'selected sections only; source acquired privately; not full original method monograph','does_not_support':['真实割胶性能','用户研究已实施','客户批准目标','专家认证','本平台完整实现原典所有规则']})
 # Detail which guarantees are ours rather than author claims.
 obj={'method':rid,'date':'2026-10-27','claims':mapped,'platform_adaptations':['未知不当持平或0','硬失败不可由偏好总分抵消','研究假设不得升级为批准要求','版本与SHA绑定','计划结果保持空且不伪造执行'],'gaps':['原始Pugh专著未核全文']if rid=='R36'else['没有真实用户/原型/工程试验数据','实际工况及判据尚未确认'],'source_license_handling':'公开原件仅private-sources保留；不复制原卡、图表或完整网页为公开正文。'}
 (dd/'来源与主张.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2))
 tests=json.loads((dd/'教学包/04-实际检查汇总.json').read_text())
 function={'R36':'bounded_pugh_research_projection','R44':'bounded_hypothesis_prototype_plan','R42':'bounded_verification_validation_plan'}[rid]
 call={'schema':'gooddesign-method-adapter-proposal-1','method':rid,'name':function,'status':'proposed_contract_with_local_fixed_teaching_script_not_native_mcp','actual_implementation':{'script':str((D/'生成与检查.py').relative_to(ROOT)),'scope':'three frozen teaching inputs only; not general semantic interpreter','native_mcp_called':False,'production_write':False},'trigger':{'R36':'已有版本化候选且需比较/补证','R44':'有明确设计不确定性并需安排学习活动','R42':'需要追溯声明、配置和证据覆盖'}[rid],'must_inputs':['问题版本与SHA','上游产物版本与SHA','来源及未知状态'],'returns':{'R36':['逐格相对关系','未知与硬失败','补证队列','可能没有排名'],'R44':['假设与原型能力','解释分支','准备度缺口','空观察表'],'R42':['声明身份','计划覆盖与未覆盖','配置绑定','未就绪原因','空证据表']}[rid],'refuse_or_return':['悬空引用或版本失配','虚构客户批准或执行','未知被填成通过','原型不具备所需能力应返回设计'],'cannot_claim':['独立专家认证','真实用户验证','工程性能达标','完整原典算法已复刻']}
 (dd/'调用说明.json').write_text(json.dumps(call,ensure_ascii=False,indent=2))
 previous={'R36':'output/method-reader-review/reviews/R36-upgrade-v0.2.1/review.md','R44':'output/method-reader-review/reviews/R44-upgrade-v0.2.1/review.md','R42':'output/method-reader-review/reviews/R42-upgrade-v0.2.0/review.md'}[rid]
 ver={'method':rid,'version':'0.1.0','date':'2026-10-27','compiled_by':'validation_deepening Agent','status':'research_teaching_ready_for_independent_agent_review','independent_review':{'reviewer':None,'status':'pending','not_equivalent_to_domain_expert_review':True},'prior_teaching_review':{'path':previous,'sha256':sha(ROOT/previous),'scope':'read_only_reference_not_new_execution'},'actual_local_checks':{'cases':tests['executed_cases'],'pass':tests['passed'],'scope':tests['qualification']},'user_studies_executed':0,'engineering_tests_executed':0,'domain_expert_certified':False,'customer_approved':False,'online_published':False,'pending':['独立交叉Agent复核','真实场景材料及专业复核','决定是否经现有流程整合公开页面']}
 (dd/'审核与版本.json').write_text(json.dumps(ver,ensure_ascii=False,indent=2))
 index=f'''# {rid} 深化执行档案 · 0.1.0

[研究说明](研究说明.md) → [来源与主张](来源与主张.json) → [反例与迁移](反例与迁移.md) → [调用说明](调用说明.json) → [审核与版本](审核与版本.json)。

本包已运行{tests['executed_cases']}项固定教学检查，覆盖五类情境；不是原型试验、客户验证、专业认证或生产MCP调用。

教学输入和逐步输出在`教学包/`。完整跨组链由MD-005-R36的`生成与检查.py`按已固定的R48/R17版本复算，检查脚本及SHA不是通用方法引擎承诺。根目录运行：

```sh
python3 '02-研究/方法深化执行/MD-005-R36/生成与检查.py'
```

R36主链32格未知、不能排名；独立datum小例的人为计数不属于割胶事实。R44未造原型、未招参与者、观察为空。R42没有已批准要求，未覆盖项明确且未就绪。

未读到或不支持的主张见来源JSON。新增审核者可在独立目录留下意见，不覆盖输入或历史输出。private-sources不进入Git或公开网站。
'''
 (dd/'README.md').write_text(index)
print('Prepared source claims, proposal contracts and pending-review metadata for three methods')
