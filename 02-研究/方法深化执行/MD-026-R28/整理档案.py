# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib
D=Path(__file__).parent;BASE=D.parent
names={'R28':'MD-026-R28','R29':'MD-027-R29','R18':'MD-028-R18','R49':'MD-029-R49'}
texts={
'R28':'''# ARIZ：先把问题变成可追踪的矛盾模型

本包使用基金会公开的西语 ARIZ-85V，核读部分1、2、3和6。原页标注1985与译审者；保留85V名称，不把不同语言版本号自动合并。它适用于功能冲突已经可描述、一般改良不足的研究情境。本包是受限教学投影，未执行完整九部分，也没有复刻标准解库。

原典部分1组织最小问题、冲突对和模型；部分2要求辨明作业区、作业时间与可用资源；部分3引入理想结果和物理矛盾；部分6允许回到问题表述。它们在本平台的价值是防止 Agent 直接跳到一个喜欢的技术答案。理想结果是研究方向，不能变成“已经无成本、无副作用”的结论。

## 固定构造教学

输入不是实际割胶机构。我们独立构造接触保持与释放：提高接触载荷可能改善抗滑，却增加释放负担；降低载荷可能便于释放，却削弱保持。这两句话都是待证因果假设。模型把接触元件、工件与释放执行器列出，工作/释放条件分开，接触区明确，执行器状态与表面信息资源保留 unknown。

中间产物是同一接触元件在不同条件下对载荷的相反期待，接着提出按条件分离的研究方向。输出仍 unsolved；没有从“时序分离”推出夹持力、皮层损伤率或实现安全性。真实任务要先查清是否确为同一属性、相反要求是否来自同一系统边界；若原冲突不存在，要撤回而不是强行套用。

## 失败与回退

本包实际执行固定正例和六个攻击，检查丢资源、颠倒条件、宣称解决、伪造阈值、删除历史及宣称完整ARIZ。拒绝行为来自固定字段基线，不是通用西语原典语义解释器。五类检查分别是正常教学、材料/资源缺失、边界条件失真、无证据成功声明和历史回退破坏。全部通过仅表示这七个夹具符合预期。

回退应保存前一问题版本、选择冲突的依据、新证据及变更理由。不能把旧矛盾悄悄覆盖。本次另一情境是文件分享：授权访问便利与未授权暴露相冲突，但条件区分并不等于已实现权限控制；模型只输出调查入口。

## 调用建议

先要求客户需求身份、功能模型版本和冲突证据；缺失就返回澄清问题。输出包括选定冲突、区/时/资源、未知、理想方向、回退记录和待研究假设。需要工程分析再转候选综合与验证流程，不能用ARIZ标签让候选自动通过硬门槛。

## 深化缺口

完整九部分与标准解匹配尚未逐项实现；西语译本不替代俄文校勘；需要 TRIZ 专业人员检查具体冲突表述。无用户研究或机械试验。后续优先验证最小问题、主过程和冲突因果，再扩展流程，避免把术语数量当深度。
''',
'R29':'''# 技术进化趋势：把方向变成可被推翻的研究假设

MATRIZ知识库列出其采用的TESE体系，且提醒历史版本存在差异。该页对趋势普适性与预定方向的强宣称属于机构立场；本包没有取得可独立复核其统计效度的原始专利研究全文，因此不把它当成任意具体产品必然进化的证据。趋势可帮助展开方案空间，不能代替需求、物理可行性和商业证据。

## 如何用于产品创新

首先固定系统边界和价值参数，再核查历史数据的可比条件。不同林地、树龄、作业制度、故障暴露的效率数字不能直接拼成一条曲线。所谓减少人工参与，也要核算转移给维护、监督和异常处理的人力。局部动作变少与完整作业收益增加是两个不同命题。

本包不拟合S曲线，也不判断“已处成熟期80%”。独立构造2021/2022/2023相同干清理任务动作数8、6、5，单位count/task，逐项注明synthetic。实际复算相邻变化−2、−1，总变化−3；这只描述构造历史。输出一条选择性自动化的待研究方向，同时保留设置与恢复负担可能增加的竞争解释。

## 证据与反例

数据来源要同时保存时间、参数定义、单位、操作边界、样本/暴露和缺失值。只有三个计数不能辨认完整S形，更不能预测下一年数字。若参数定义变了，应该切断序列；新代产品的指标不可直接与旧代异口径参数连接。

实际七项夹具包括原正例、单位变更、工况变更、虚构成熟度、必然未来、删去反证、发明客户目标。五类是正常描述、数据口径错误、跨边界拼接、无证据预测和竞争解释缺失。固定基线拒绝攻击，不是普适趋势识别或预测器。

另一情境为文档审批动作数下降：自动化可能增加异常回退和重复确认。已做桌面条件比较，没有采集真实审批数据；因此同样只能保留研究假设。

## 调用与质量门槛

建议调用输入包括版本化系统边界、可比历史、目标参数、趋势体系版本及竞争解释。引擎返回方向、支持范围、反证需求和不确定性，不返回看似精确的成熟百分比。后接功能分析、路线组合和证据计划。硬约束失败与成本不确定不能被“顺应趋势”抵消。

下一步需要领域历史样本、专利研究方法全文和路线失败样本，明确趋势命中/未命中如何定义。没有这些数据时准确表述缺口，比将通用趋势写成确定预言更有价值。
''',
'R18':'''# 仿生：沿自然证据到工程假设逐层迁移

本包采用Bohn与Federle发表于PNAS的2004原始研究，核读摘要、材料方法和摩擦装置/湿干比较相关段落。实验涉及猪笼草唇口与蚂蚁接触结构；湿润液膜影响软黏附垫，表面方向结构对爪作用不同。它支持有条件的自然机制，不能证明任意材料的防黏效果。

## 为什么必须拆开机制与比喻

“像猪笼草所以不粘”跳过了关键条件。自然系统的液体、表面、接触结构和环境须共同进入解释。工程端若换成乳胶、金属刀具和污物，黏度、凝固、润湿、接触压力、尺度与补液条件都改变。生物策略的名称不是机械性能数据。

本包构造一个割胶研究接口的清理方向。证据链分为原始生物实验→条件性机制→不带物种名的抽象→尚未验证的目标假设。中间映射保存三类差异：水性液膜与乳胶流变/凝固未知，蚂蚁足垫/爪与工具材料对未知，原植物湿润条件与现场污染补液未知。没有计算清理效率增益或设定客户阈值。

## 实际教学与反例

输出不是仿生表面定型，而是材料表征、湿干及表面形态对照、暴露一致和维护副作用的测试建议。真正研究需要预先定义失效、重复次数、清理周期和测量不确定性，且由专业人员选择适合材料与工况的测试。

已执行固定正例及六个攻击：错换爪/足垫机制、干燥条件普适化、删除迁移差异、发明性能增益、宣称已验证和删除控制。五类涵盖正常映射、自然机制失真、应用边界缺失、无证据效果、测试设计缺失。七项通过只证明固定教学保真，不证明仿生概念有效。

另一情境包装脱离界面把昆虫接触换成胶黏剂/聚合物，依然不能从原实验推出剥离力与耐久性。已做桌面差异核查，未做包装试验。

## 给引擎的调用边界

输入至少包含带定位的自然机制证据、目标功能、环境与材料条件；输入只有动植物名称时先补研究。输出保留自然事实与工程假设的不同类型，以及所有不能迁移的条件。建议与功能导向检索、材料效应检索、风险/实验计划连接。

本次最重要的深化是让“像什么”转为“什么条件下、通过什么机制、对什么接触结构发生什么作用”。还缺目标材料数据、工程重现实验和生物学/表面工程专业审核，不宣称专家认证。
''',
'R49':'''# FBS：让意图、期待行为、结构和分析结果保持不同身份

原作者公开PDF地址本次遇到证书过期，浏览工具也抓取超时；出版社和作者检索摘要可核题名、作者、2004期刊卷页与论文主旨。摘要说明该文将原框架扩展到动态情境。全文未成功取得，因此本包明确受限，不复原situated FBS八过程、三个世界之间的完整细则，也不把二手图当原典。

## 当前能可靠交付什么

平台教学明确分开F（为何需要）、Be（期望表现）、S（结构）、Bs（在已说明模型下推导的表现）。这是有限的教学表示，不声称完整执行论文算法。其价值在于防止直接从一个结构名称跳到“已经满足需求”，或者把分析值写成实测。

独立构造例子：希望支持保持，正常力目标仍未知；结构采用理想线性弹簧，刚度10 N/mm、位移2 mm，两个数都是教学构造而非机器人设计参数。记录线弹性范围、准静态、无损失/传动变换三项假设后，脚本实际计算Bs=20 N。它是条件性解析结果，不是测量结果。因为Be目标未知，输出不能判断符合性。

## 如何深入而不制造完整性

真实工程需要补参数来源、约束、模型适用范围、误差和外部工况。若结构变化，应重新推导行为；若目标变化，应记录期待行为的版本和来源；若观测与模型不同，应保留差异并检查假设，而不是改数字以显得达标。功能措辞也需要追溯到需求来源，不能因分析便利而偷偷缩小需求。

实际七项固定夹具包含正常算术、位移单位改变、解析值冒充实测、发明Be目标、宣称完整situated模型、删除模型假设与无依据通过。五类为正常推导、量纲失真、证据身份错误、框架范围冒充和目标/结论伪造。通过只表示这几个固定输入按预期处理，不是通用物理分析器。

另一情境是文档交付：可读性是期待行为，导出文件/路线是结构；发送记录不能替代收件人可打开目标版本的观察。已进行桌面映射，未开展真实接收者测试。

## 调用建议与阻塞项

建议输入把F/Be/S/Bs及各自证据类型拆开，单位和模型假设必填。未知Be时输出待澄清，结构未知时不产生Bs，分析结果不得自动升格实测或批准。与功能模型、候选生成、分析验证相接。

当前审核应标limited_source，不把“有28项教学检查”解释成原典已完整研究。需先合法取得作者全文、核图与过程定义，再由领域人员复核映射，然后才扩展situated部分。公开页面应显示来源深度与限制，而不隐藏不足。
'''}
urls={'R28':[('基金会ARIZ-85V西语第1部分','https://www.altshuller.ru/world/spa/ariz85v-1.asp','steps1.1–1.7'),('基金会第2部分','https://www.altshuller.ru/world/spa/ariz85v-2.asp','steps2.1–2.3'),('基金会第3部分','https://www.altshuller.ru/world/spa/ariz85v-3.asp','steps3.1–3.6'),('基金会第6部分','https://www.altshuller.ru/world/spa/ariz85v-6.asp','steps6.1–6.4')],'R29':[('MATRIZ TESE','https://wiki.matriz.org/docs/triz/trends-of-engineering-systems-evolution-tese-5919/','Overview; Hierarchical structure; trend definitions')],'R18':[('Bohn and Federle 2004 original study','https://pmc.ncbi.nlm.nih.gov/articles/PMC521129/','Abstract; Materials and Methods; Fig3; wet/dry and friction results'),('Biomimicry Institute abstraction','https://toolbox.biomimicry.org/methods/abstract/','Abstract design strategies')],'R49':[('Gero/Kannengiesser2004 publisher abstract','https://www.sciencedirect.com/science/article/pii/S0142694X03000735','Abstract only'),('author PDF failed retrieval','https://www.johngero.com/publications/2004/04GeroKannengDesignStud.pdf','not acquired; do not cite internal processes as read')]}
for rid,n in names.items():
 dd=BASE/n;(dd/'研究说明.md').write_text(texts[rid]);ss=[]
 for title,url,loc in urls[rid]:ss.append({'title':title,'url':url,'locator':loc,'claim_scope':'source-level selected passage only; platform teaching is independent construction','full_text_read':False if rid=='R49'else 'selected_sections_only'})
 (dd/'来源与主张.json').write_text(json.dumps({'method':rid,'sources':ss,'platform_rules':['unknown is not passed','hypothesis is not approved requirement','no field/expert certification'],'source_depth':'limited_abstract_only'if rid=='R49'else'selected_primary_sections','copyright':'raw originals private-sources excluded from manifest/publication; no full-text redistribution'},ensure_ascii=False,indent=2))
 (dd/'调用说明.json').write_text(json.dumps({'method':rid,'package_version':'0.1.0','status':'proposed_contract_local_fixed_teaching_only','implementation_script':str(D/'教学与反例.py'),'native_mcp_called':False,'inputs':['versioned problem context','source identity and scope','method-specific assumptions and unknowns'],'outputs':['intermediate reasoning','evidence identity','unresolved issues','bounded next research'],'refuse':['fixed source/model mutated','unknown promoted to result','unsupported completion or approval'],'scope':'not general semantic method engine','source_limitation':rid=='R49'},ensure_ascii=False,indent=2))
 t=json.loads((dd/'教学包/03-实际检查汇总.json').read_text())
 (dd/'审核与版本.json').write_text(json.dumps({'method':rid,'version':'0.1.0','problem_version':'0.1.0','status':'limited_source_pending_review'if rid=='R49'else'research_teaching_pending_independent_review','independent_review':'pending','fixed_checks':t['executed_cases'],'fixed_checks_passed':t['passed'],'engineering_tests':0,'user_studies':0,'expert_certified':False,'online_published':False,'pending':['independent agent adversarial review','domain source and engineering review','full primary paper acquisition'if rid=='R49'else'actual target context evidence']},ensure_ascii=False,indent=2))
 (dd/'反例与迁移.md').write_text('''# 固定夹具与迁移范围

实际输入、输出、六项攻击及结果见教学包。正常正例加六个负例，共七项；失败类型与拒绝原因逐项保留。它们按固定基线检查结构和有限算术，不能证明通用语义理解。

另一情境已单独保存04，检查环境、对象和证据角色变化，不把桌面迁移当实测。研究说明逐条解释五类反例与限制。共享割胶问题只提供研究背景，独立教学计数/弹簧参数不写回客户需求，也不接管第一批候选优胜判断。
''')
 (dd/'README.md').write_text(f'''# {rid} 方法深化档案

[研究说明](研究说明.md) · [来源](来源与主张.json) · [教学检查](教学包/03-实际检查汇总.json) · [调用建议](调用说明.json) · [审核状态](审核与版本.json)

已执行七项固定教学检查；不是原生MCP、工程测试或专家认证。四法复跑从项目根目录执行 MD-026-R28/教学与反例.py，写入四个本批独占目录。原始资料在忽略的private-sources中；manifest不包含全文。
''')
 sourcepath=dd/'来源与主张.json';sourceobj=json.loads(sourcepath.read_text())
 sourceobj['private_evidence_inventory']=[{'path':str(f.relative_to(dd)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'not_in_public_manifest':True,'read_scope':'selected sections or failure recorded; see source locators'}for f in sorted((dd/'private-sources').glob('*'))if f.is_file()]
 if rid=='R49':sourceobj['verified_bibliographic_identity']={'authors':['John S. Gero','Udo Kannengiesser'],'year':2004,'journal':'Design Studies','volume':25,'issue':4,'pages':'373–391','doi':'10.1016/j.destud.2003.10.010','verification':'author search index and publisher abstract; full paper not acquired'}
 sourcepath.write_text(json.dumps(sourceobj,ensure_ascii=False,indent=2))
 entries=[]
 for p in sorted(dd.rglob('*')):
  if p.is_file()and'private-sources'not in p.parts and'__pycache__'not in p.parts and p.name!='manifest.json':entries.append({'path':str(p.relative_to(dd)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (dd/'manifest.json').write_text(json.dumps({'method':rid,'version':'0.1.0','status':'pending_review','files':entries},ensure_ascii=False,indent=2))
 print(n,hashlib.sha256((dd/'manifest.json').read_bytes()).hexdigest())
