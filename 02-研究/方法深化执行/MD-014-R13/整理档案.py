# -*- coding: utf-8 -*-
from pathlib import Path
import hashlib,json,re,ast
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
DIRS={'R13':P,'R15':P.parent/'MD-015-R15','R16':P.parent/'MD-016-R16'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
claims={
'R13':[('HF-S1','HSE-INTRO','Introduction / Job, equipment and environment / Individual factors','This definition includes','人因需要共同考虑任务、个体和组织，身体与认知匹配不能分开。'),('HF-S2','HSE-WORKLOAD','Why is workload important? / Key principles in workload','underload can also','正常、异常、经验差异以及身体和心理负荷都应纳入研究。')],
'R15':[('FAST-S1','VA-FAST','Steps in constructing the FAST Diagram','Place the answer','HOW向右、WHY向左复核；WHEN不是时钟先后。'),('FAST-S2','VA-FAST','Is there a correct FAST Diagram?','validity of a FAST','FAST有效性依赖知识与范围；本固定图不是唯一正确图。'),('FAST-S3','FHWA-VE','Investigation / Identifying the functions','an action verb','用作用和被作用对象表达功能；本教学选定的摩擦路径是平台构造。')],
'R16':[('RCA-S1','HSE-CAUSE','Identify immediate and underlying causes','Immediate (or direct)','区分直接原因与潜在条件，不能由事件现象自动推出唯一根因。'),('RCA-S2','HSE-HSG245','PDF第21/23/24页选段；非88页逐项精读','Job factors:','调查关注任务、人、组织因素和控制行动；本例的竞争矩阵与暴露计算是平台适配。')]
}
for rid,d in DIRS.items():
 rr=json.loads((d/'来源取得记录.json').read_text());sources={x['id']:x for x in rr};mapped=[]
 for cid,sid,loc,anchor,claim in claims[rid]:
  r=sources[sid];tp=ROOT/r['text_path'];t=tp.read_text();p=t.find(anchor)
  mapped.append({'claim_id':cid,'source_id':sid,'claim':claim,'url':r['url'],'raw_sha256':r['raw_sha256'],'text_sha256':sha(tp),'raw_path_private':r['raw_path'],'text_path_private':r['text_path'],'locator':loc,'short_anchor':anchor,'anchor_start':p if p>=0 else None,'read_scope':'selected sections only; not full original monograph or all industry standards','does_not_support':['真实目标人群/客户事实','本构造模型工程有效','所有原法规则已实现','独立专业认证']})
 notes=[]
 if rid=='R15':notes=['WVDOT旧PDF链接失败；USBR两个入口失败/维护，未取得相应正文','EPA扫描PDF取得131页但文本抽取为空，未据此声称已核读FAST操作规则','实际操作依据采用VA Canada官方公开完整短页与FHWA公开功能定义；图为平台简化教学视图']
 (d/'来源与主张.json').write_text(json.dumps({'method':rid,'date':'2026-10-27','claims':mapped,'source_attempts':rr,'retrieval_notes':notes,'platform_adaptations':['固定JSON模型与拒绝规则','构造输入、反例、状态及迁移情境','源版本/SHA与保真治理'],'not_full_original_reconstruction':True},ensure_ascii=False,indent=2))
 s=json.loads((d/'教学包/04-实际检查汇总.json').read_text())
 proposal={'method':rid,'version':'0.1.0','status':'suggested_adapter_not_registered_MCP','implemented_scope':'local_fixed_teaching_script_only','script':str((P/'教学与反例.py').relative_to(ROOT)),'not_general_semantic_validator':True,'when_to_use':{'R13':'需要分析人群、任务、环境及异常接管的适配','R15':'需要核功能目的—手段与范围而非时间流程','R16':'已有事件材料，需组织竞争原因、反证和行动'}[rid],'input':{'R13':['角色与任务情境','信息/动作/反馈','目标人群数据状态','原始观察或构造标签'],'R15':['所用FAST视图','功能范围与HOW/WHY问答','支撑关系和未知'],'R16':['事件原件/条件与时间线','支持/反证及其能力范围','拟议行动、实施和可比暴露']}[rid],'output':{'R13':['任务与信息缺口','仅编码层面的表征碰撞分析','待执行研究'],'R15':['逐边问答、范围及支撑','替代路径与未知','人工逻辑审查记录'],'R16':['竞争解释与未决证据','行动队列','描述性暴露指标或不可计算']}[rid],'reject_or_return':['源身份/范围/版本失配','构造材料冒充客户/实测','未确认数据被升级为结论','固定关系被无依据篡改'],'unimplemented':['通用MCP端点','任意自然语言语义验证','用户/工程现场验证','专家签署'],'production_mutation':False}
 (d/'调用说明.json').write_text(json.dumps(proposal,ensure_ascii=False,indent=2))
 audit={'method':rid,'version':'0.1.0','date':'2026-10-27','author':'validation_deepening Agent','status':'ready_for_independent_agent_review','independent_agent_reviewer':None,'domain_expert_reviewer':None,'actual_fixed_checks':s['executed'],'passed':s['passed'],'field_trials':0,'human_participants':0,'customer_approved':False,'engineering_validated':False,'online_published':False,'native_mcp_invoked':False,'first_batch_reference_status':'pending_root_coordinated_fidelity_revision_no_old_bytes_or_SHA_changed','gaps':['目标场景实际材料','独立Agent复核','专业复核/现场有效性'],'scope':'research_and_bounded_fixed_lesson_not_expert_certification'}
 (d/'审核与版本.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
 (d/'README.md').write_text(f'''# {rid} 逐法深化执行 · 0.1.0

[研究说明](研究说明.md) · [来源与主张](来源与主张.json) · [反例与迁移](反例与迁移.md) · [调用说明](调用说明.json) · [审核版本](审核与版本.json)。

本包有完整构造输入、中间分析和输出，实际运行{s['executed']}项固定检查；没有现场/用户试验、专家认证或上线。构造材料不冒充真实项目证据。

三个第二批教学包的复算入口在MD-014-R13：

```sh
python3 '02-研究/方法深化执行/MD-014-R13/教学与反例.py'
```

代码只作固定模型的表征、逻辑记录或证据账本检查，不作任意人因、FAST语义或事故因果推断。修改图和事实不一定理论上错误，但会成为另一个需重新核读的新版本。

原件在.gitignore排除的private-sources，manifest不包含全文；公开分享只用原创说明、短定位与来源链接。首批三项待修订状态与源SHA只读保留，本包未覆盖旧输出。
''')
print('Three second-batch metadata sets prepared')
