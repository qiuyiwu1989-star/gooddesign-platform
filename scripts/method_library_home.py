"""Concise discovery copy for the methods index; frozen source text is untouched."""
from html import escape as E
from method_glass_icons import VERSION
CATEGORIES={'A':'需求洞察','B':'功能与概念','C':'矛盾求解','D':'结构与系统','E':'工程优化','F':'评价与验证','G':'流程与管理'}
TITLES={'R05':'机电系统 V 模型','R27':'功能检索与科学效应','R28':'ARIZ 发明问题求解','R41':'机械风险评估','R46':'专利景观与技术路线','R49':'功能—行为—结构（FBS）','R50':'服务蓝图与服务协同','R51':'系统理论过程分析（STPA）','R52':'信息价值与验证优先级','WB01':'系统化与综合设计','WB05':'主辅功能与功能优化','WB06':'结构性能与动态设计','WB07':'使用性能与智能设计','WB08':'制造性能与可视化设计','WB10':'设计质量检验与评价','WB11':'方法规则与专家系统','WB12':'设计方法分类与出处'}
COPY={
'R01':'从任务、功能到实体，组织可回返的产品开发过程。',
'R02':'先看清问题，再比较方案，用两轮发散与收敛推进设计。',
'R03':'理解人的经历，通过构思、原型与测试反复学习。',
'R04':'协调需求、架构、接口与验证，核对系统级目标。',
'R05':'把跨学科设计与集成验证对应起来，提前规划证明路径。',
'R06':'在增加研发投入前，用阶段证据判断继续、返工或终止。',
'R07':'把顾客需求转为可测的质量特性，纳入设计与验证。',
'R08':'从真实任务中的行为、原话和环境提炼需求线索。',
'R09':'理解用户在什么情境下，为什么选择或放弃一个方案。',
'R10':'寻找提前遇到新需求的用户，共同发展可验证的概念。',
'R11':'区分不同特性对满意度的影响，为需求取舍提供依据。',
'R12':'把顾客需要转为可追踪的工程响应与组织行动。',
'R13':'综合人的能力、任务与设备，核对人机适配要求。',
'R14':'拆解功能与输入输出，明确子系统间的接口。',
'R15':'追问“为什么”和“如何实现”，发现功能替代机会。',
'R16':'用事实与可检验的因果假设追查问题，验证纠正措施。',
'R17':'列出各子功能的候选原理，检查并组合成设计概念。',
'R18':'从自然策略中抽象机制，检验它在工程情境中的适配。',
'R19':'用具体的设计变换提示，突破对第一个概念的固着。',
'R20':'区分概念与已有知识，在探索和求证之间往返推进。',
'R21':'用功能、矛盾和资源重述问题，选择合适的发明工具。',
'R22':'把性能权衡表述为技术矛盾，寻找可追溯的原理提示。',
'R23':'识别相反要求，按时间、空间或系统层级寻找分离机制。',
'R24':'明确理想目标，盘点可用资源，探索少增负担的方案。',
'R25':'把关键作用抽象为物质与场，再回译为工程机制。',
'R26':'删除不必要的功能载体，检查有用功能由谁接替。',
'R27':'跨行业寻找技术与科学效应，再检验目标场景的差距。',
'R28':'结合问题重构、资源与矛盾，逐步求解复杂发明问题。',
'R29':'借助系统演化模式，形成可被证据检验的创新路线。',
'R30':'建立需求、功能与结构的映射，诊断设计耦合。',
'R31':'用依赖矩阵识别模块边界、接口与循环耦合。',
'R32':'从期望运动与轨迹，反求机构形式和尺寸。',
'R33':'先按约束筛选材料，再比较性能与可制造证据。',
'R34':'检查零件与装配动作是否必要，减少制造和装配负担。',
'R35':'在载荷与边界明确后，探索材料分布并复核可制造性。',
'R36':'围绕共同基准比较概念，用差异与未知推动下一轮验证。',
'R37':'明确评价准则、偏好与不确定性，检查选择的敏感性。',
'R38':'设计因素组合试验，分析效应并独立确认参数建议。',
'R39':'寻找对噪声不敏感的参数，再决定哪些公差值得收紧。',
'R40':'识别失效模式、影响与原因，安排措施并跟踪验证。',
'R41':'识别危险情境，比较设计、防护与风险验证措施。',
'R42':'分别核对规定要求与预期使用，收集对应的客观证据。',
'R43':'比较全生命周期环境影响，定位热点与负担转移。',
'R44':'围绕高风险假设选择最小原型，用实验获得决策依据。',
'R45':'澄清必要功能与成本，比较满足同等功能的替代方案。',
'R46':'整理可复现的专利集合，识别技术路线并保留证据边界。',
'R47':'跨专业保留多种可行选项，再用证据逐步缩小范围。',
'R48':'把真实情境转为可验证的要求，管理假设、冲突与变更。',
'WB01':'把调研、规划、实施与检验联结成可回返的设计体系。',
'WB02':'分别检查用户需求、产品环境与风险，明确调研缺口。',
'WB03':'联结目标、环境、过程与方法，让总体规划可检查。',
'WB04':'以功能为核心，协同多类设计方法并检查整体影响。',
'WB05':'梳理主辅功能，核对方案组合与功能实现。',
'WB06':'围绕结构动态性能，联结运动模型、试验与设计修正。',
'WB07':'围绕使用性能，组织操作、控制与状态监测研究。',
'WB08':'用受控模型模拟制造过程，检查可达性与过程可行性。',
'WB09':'针对线性近似不足的问题，研究复杂动态行为。',
'WB10':'把功能与性能转为评价指标，解释证据及薄弱项。',
'WB11':'梳理方法论规则与推理边界，保留待核出处。',
'WB12':'追溯原文分类，区分框架、方法与编纂收录线索。',
'R49':'在功能与结构之间比较行为，避免凭外形直接选方案。',
'R50':'连起用户、前台与后台，发现服务交接中的遗漏需求。',
'R51':'从控制动作、情境与反馈，检查系统交互风险。',
'R52':'判断哪些新证据可能改变决策，安排下一步验证。',
}


def render(records):
    assert set(records)==set(COPY), 'Every visible method needs reviewed discovery copy'
    total=len(records)
    body=f'''<main id="main" class="overview method-home">
<header class="mh-heading"><p class="mh-kicker">方法库</p><h1>从问题出发，找到方法</h1><p class="mh-lead">梳理需求、构思方案、验证判断。</p></header>
<div class="mh-discovery"><form class="mh-search" role="search"><label class="mh-sr" for="method-search">搜索方法</label><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input id="method-search" name="q" type="search" placeholder="搜索方法名称或关键词" autocomplete="off" aria-controls="method-cards"><button class="mh-clear" type="button" aria-label="清除搜索" hidden><svg aria-hidden="true" viewBox="0 0 24 24"><path d="m7 7 10 10M17 7 7 17"/></svg></button></form>
<nav class="categories mh-categories" aria-label="方法分类"><button type="button" data-category="" aria-pressed="true">全部</button>'''
    body+=''.join(f'<button type="button" data-category="{k}" aria-pressed="false">{E(v)}</button>' for k,v in CATEGORIES.items())
    body+=f'''</nav></div><div class="mh-results"><p id="search-status" role="status" aria-live="polite" aria-atomic="true">全部 · {total} 项方法与专题</p><button type="button" class="mh-reset" data-reset-filters hidden>重置筛选</button></div><div class="cards" id="method-cards">'''
    for rid,d in records.items():
        name=TITLES.get(rid,d['name'])
        search=' '.join([rid,d['method_id'],d['name'],name,d['english_name'],d['summary'],COPY[rid]]+d.get('search_terms',[])+d.get('aliases',[])).lower()
        body+=f'''<a class="method-card cat-{d['category'][0]}" data-cat="{d['category'][0]}" data-search="{E(search,quote=True)}" href="methods/{rid}.html" aria-label="{E(d['name'],quote=True)}"><div class="mh-card-top"><img src="icons/{rid}.svg?v={VERSION}" alt="" width="72" height="72"><div>{'<span class="mh-topic">谱系专题</span>' if rid.startswith('WB') else ''}<h2>{E(name)}</h2></div></div><p>{E(COPY[rid])}</p></a>'''
    return body+'''</div><div id="empty" class="mh-empty" hidden><h2>没有找到匹配的方法</h2><p>换个关键词，或清除筛选后再试。</p><button type="button" class="gd-button" data-reset-filters>清除筛选</button></div></main>'''
