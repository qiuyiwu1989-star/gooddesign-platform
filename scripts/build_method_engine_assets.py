"""Export authored contract overlay and source-checked claim notes, without touching frozen library."""
import json
from pathlib import Path
from method_engine import Engine, ROOT, digest
from method_engine_contracts import META, contract, OVERLAY

NOTES = {
 'R48': {
  'source': 'https://www.nasa.gov/reference/4-2-technical-requirements-definition/',
  'locator': '4.2.1.2.1–4.2.1.2.6',
  'claims': ['要求需关联使用边界、约束、功能与接口。', '要求质量检查涉及可行性、可验证性和利益相关方期望。', '形成基线需经过确认与配置控制，而不是模型自动宣告。'],
  'adaptation': 'NASA所述正式要求过程与平台早期问题澄清不同；本契约允许proposed/unknown以组织概念研究，不把它们升级为批准基线。',
  'operation': '先保存客户原话，再区分使用者、对象、期望改变与现有解法。每条要求分别写接受口径、硬/软、确认状态和出处。输入缺口不会被默认目标值填满。确认标签必须有证据引用，但证据是否真的代表客户批准仍需人工核对。',
  'counterexample': '“采用视觉传感器”通常是候选实现；若直接作为必要功能，会过早排除机械定位等方向。应先问要观察什么、在何条件下、达到什么结果。'},
 'R14': {
  'source': 'https://www.nasa.gov/reference/4-0-system-design-processes/',
  'locator': '4.3.1.1–4.3.1.3 Logical Decomposition',
  'claims': ['逻辑分解关注系统各层需要实现什么。', '功能及接口关系支持需求分解与分配。', '派生要求、假设与设计决策应一并保留。'],
  'adaptation': '本契约用功能节点与物料/能量/信号流表达概念模型，是平台选定的一种表示，不等同NASA完整系统架构规范。',
  'operation': '冻结本轮系统边界，按动词—对象列功能，区分必要、支撑和未知。给功能稳定ID，用有方向的流记录作用或传递，并写明未证实关系。检查接口两端确实存在，返回需求核对遗漏；功能图不能凭箭头证明根因。',
  'counterexample': '删除“释放工件”会使夹持动作看似完成，却漏掉完整使用循环；功能分解必须返回装载、保持、释放及维护场景核查。'},
 'R17': {
  'source': 'https://swemorph.com/ma.html', 'locator': 'Fundamentals / Cross Consistency Assessment',
  'claims': ['形态学组织参数及其状态形成组合空间。', 'CCA检查状态能否共存，不表示因果方向。', '逻辑、经验及规范约束应区分，不把偏好当作物理不可能。'],
  'adaptation': '以子功能为维度、实现原理为选项是平台机械概念应用。完整工程可行性仍需多体、工艺、载荷和整体约束检查，不由成对兼容直接推出。',
  'operation': '从功能模型取同一粒度的维度，为每维列原理及成立条件。一组合为每个已选功能选择一个原理，逐对保留兼容、冲突和未知的理由。冲突组合排除并记录；未知可以保留作研究候选，不能标为已实现。查维度是否遗漏释放、防护或能源供应。',
  'counterexample': '气动夹紧与气源未知并非已知物理冲突；应标条件缺失。若同一接口又必须完全密封又必须连续开放，则需改变边界、时序或原理，而非把两选项记为兼容。'},
 'R36': {
  'source': 'https://ocw.mit.edu/courses/ec-720j-d-lab-ii-design-spring-2010/pages/projects/ideas/',
  'locator': 'Concept Evaluation / Pugh Chart Analysis',
  'claims': ['Pugh比较使用参照方案与统一准则。', '相对判断可写优于、相同或劣于参照。', '概念可经进一步研究、试验及组合后再比较。'],
  'adaptation': '原课程有符号计数与可选权重。本平台另加硬门槛和unknown状态，不把它们冒称为Pugh唯一原规则；未知不以0代替。',
  'operation': '保留需求基线版本、比较基准、候选和准则ID；用requirement_ids把准则绑定到需求简报。每项硬要求及硬软属性未知的要求必须映射到硬门槛；属性未知时不得推荐。先查硬门槛，再填写有依据的相对判断，证据不足写unknown。对基准、批量、工况变化作敏感性讨论。推荐不是最高符号总和的自动同义词；这些追溯与停止规则属于平台约束，不冒称Pugh原规则。',
  'counterexample': '半自动方案的维护成本未知时，填“与人工相同”会制造虚假优势。应提出维修频率、工时和耗材的补证任务，必要时暂不排名。'},
 'R44': {
  'source': 'https://dschool.stanford.edu/tools/experiment-expedition', 'locator': 'How does it work? / public introduction',
  'claims': ['原型活动用于测试与修订假设。', '公开介绍区分规划、制作、试验、采集与解释。', '实际学习需要执行及数据，不能把计划写成反馈。'],
  'adaptation': '本轮只复读公开介绍，未取得并逐页核读工作表；没有复制外部卡组。输出是平台原创计划契约，不是试验结果格式。',
  'operation': '选会改变路线的关键假设，写清观察量、试验范围、步骤和判据。判据未确认时须在执行前补齐，不能开始试验后按结果选择门槛。保留原型不覆盖的寿命、强度等问题，另建验证活动。',
  'counterexample': '泡沫外形原型可以帮助讨论握持与可达性，但不能用来证明夹具在目标载荷下不会屈服。需要不同原型与验证配置分别回答。'},
 'R42': {
  'source': 'https://www.nasa.gov/reference/5-3-product-verification/', 'locator': '5.3.1 Inputs / Methods; 5.4 Product Validation related public section',
  'claims': ['Verification针对规定要求及配置。', 'Validation关注预期使用环境中的用户期望。', '计划、执行结果与认证属于不同记录，不能互相替代。'],
  'adaptation': '结合公开5.4章复读。平台当前仅实现计划契约；inspection/analysis/demonstration/test名称不意味着已具备测试设施或行业认证资格。',
  'operation': '将每项要求ID交给明确方法、判据、配置及证据状态，未覆盖项显式列出。记录要求基线版本，变更后重新核对覆盖。独立列使用者与环境确认问题。计划只能含none/planned，实际结果需后续单独的结果契约和审查。',
  'counterexample': '样机尺寸满足图纸不代表使用者能在预期环境完成维护；反过来一次操作顺畅也不能证明所有强度与寿命要求。两条证据链分别保存。'},
}


def build():
    engine=Engine();base=OVERLAY
    if (base/'发布冻结.json').exists():raise ValueError('contract_overlay_frozen_create_new_version')
    base.mkdir(exist_ok=True)
    claims=[]
    for rid,note in NOTES.items():
        folder=base/rid;folder.mkdir(exist_ok=True)
        data=engine.get(rid,'overview');c=contract(rid)
        c.update({'source_method_id':data['method']['method_id'],'source_content_version':data['method']['version'],
                  'source_content_sha256':data['content_sha256'],'implementation_scope':'concept_research_and_planning_only'})
        (folder/'contract.json').write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')
        (folder/'执行深读.md').write_text('\n\n'.join([f'# {rid} 执行深读', '状态：平台补强，未独立专家审核；不修改冻结正文。',
            '## 关键操作',note['operation'],'## 反例',note['counterexample'],'## 原典与适配边界',note['adaptation'],
            '## 本轮核读','2026-10-25复读公开来源相关段落，未将目录或未取得的工作表记为正文。',
            f"[{note['source']}]({note['source']})；定位：{note['locator']}",
            '## 进入下一方法前',META[rid]['stop'],'结构检查不等于事实正确、方案可行或专家批准。'])+'\n')
        for i,statement in enumerate(note['claims'],1):
            claims.append({'claim_id':rid+'-C'+str(i),'research_id':rid,'statement':statement,'url':note['source'],
                           'locator':note['locator'],'read_at':'2026-10-25','support_status':'agent_checked_public_source_not_expert_reviewed',
                           'adaptation_boundary':note['adaptation']})
    (base/'关键主张台账.json').write_text(json.dumps({'claims':claims,'expert_reviewed':False},ensure_ascii=False,indent=2)+'\n')
    config={'mcpServers':{'gooddesign_method_engine':{'command':str(ROOT/'.runtime/pipeline/bin/python'),
          'args':[str(ROOT/'scripts/method_engine_mcp.py')],
          'env':{'METHOD_ENGINE_DB':str(ROOT/'04-知识库/创新方法库/运行数据-v0.2/runs.sqlite3')}}}}
    dest=ROOT/'output/method-engine-ML003';dest.mkdir(exist_ok=True)
    (dest/'mcp-config.local.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'contracts':len(NOTES),'source_checked_claims':len(claims),'output':str(base)},ensure_ascii=False))


if __name__=='__main__':build()
