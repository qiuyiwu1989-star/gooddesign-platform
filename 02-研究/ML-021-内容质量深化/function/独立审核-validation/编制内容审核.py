from pathlib import Path
import hashlib,json
p=Path(__file__).parent;src=p.parents[1]/'validation';rows=[]
# Each selector locates a concrete section/paragraph read; ratings apply to bounded manuscript, not full original algorithm.
selectors={
'R37':['当轻便','假设可加','完整构造例','交点w','两种实质','NASA决策','操作产物'],
'R38':['它适合','两水平全因子','设计完成前','六列矩阵','至少三种','NIST将','R38估计'],
'R39':['产品在','外阵列不是','首先按','构造例有','两种误用','NIST以','完整操作'],
'R40':['FMEA用于','模式是','操作先','给三条','两种实质','出处定位','行动记录'],
'R41':['机器正常','切断电驱','先声明','给一份','两种误用','HSE公开','每项措施'],
'R42':['同一设备','验证检查','准备时','修改CONFIG','两种误用','NASA系统','交付应'],
'R43':['一台设备','参考流才','操作中','完整构造例','两类实质','GSA官方','交付应'],
'R44':['原型的价值','竞争解释','完整教学协议','现在给三条','两类实质','出处定位','产物包括'],
'R45':['价值工程不是','worth是','操作从','在人为规定','两种误用','FHWA公开','输出应'],
'R46':['专利景观研究','计数先','先定研究','可跟随的真实','两类实质','WIPO2015','交付应'],
'R47':['多个团队','连续上下限','输入不能','完整构造例','两种实质','LEI官方','输出为'],
'R49':['它不替代','Gero与','先写F','候选A','两种实质','作者上传','引擎调用'],
'R50':['蓝图不是','前台/后台','先确定','未来版蓝图','两种误用','NN/G原','产物从'],
'R51':['部件都','四类是','先写损失','完整构造例','两类误用','作者讲义','输出应'],
'R52':['它适合','当前风险','列出现在','状态good','两类误用','Johnson等','形成研究'],
'WB07':['把大模型','第一条流程','第二条流程','再给产品','两类误用','出处定位','输出应'],
'WB08':['可视优化不是','运动动画','先写要','候选C','两种误用','出处定位','产物保留'],
'WB09':['作者2019','线性化','先确定','完整独立','两类实质','出处定位','接R38'],
'WB10':['质量检验','离散权重','操作先','完整构造','两种误用','出处定位','本专题输出'],
'WB11':['原则提醒','四种类型','规则记录','完整构造例','两类实质','出处定位','具体工程'],
'WB12':['方法库','same_as','先固定','再给两个','两类误用','出处定位','输出为']}
notes={
'R37':'解析权重交点与选择完整；偏好与值全构造、非NASA权重，重复计分反例实质。',
'R38':'独立最小二乘复算六系数/秩/自由度与正文一致；可跟随地从曲率转到域内最大点再确认，未冒充实测。',
'R39':'四情景最低值先筛选；样本标准差未当现场概率，公差与参数改进区别具体。',
'R40':'陈旧反馈/共电源因果链到改版行为完整，未以新传感器数量证明冗余独立。',
'R41':'人员清堵任务与三能量通道明确；具体结构措施尚是研究方向，未给合规/检修放行。',
'R42':'D1验证满足却用途失败、D2再核完整，模型/配置/环境复用边界明确。',
'R43':'参考流与全阶段BU加总正确；寿命敏感性揭示反转，明确非完整ISO LCA。',
'R44':'竞争解释和C1—C4编码有实质回返；O3反例没有被忽略，选择的是继续研究方向。',
'R45':'费用与功能分摊不混价值权重，五次维护选择及交点复算一致，错SAVE来源已撤回。',
'R46':'真实检索和身份纳排可复查；技术编码核心仍未来式，尚无逐格权项定位的实际比较，需内容修订。',
'R47':'交集/新约束/按原因重开示范可独立枚举，明确离散人工耦合式不冒物理定律。',
'R49':'实际核作者上传正文F/Be/Bs/S和重构分类；弹簧/摩擦例完整且μ变化回返，不把Bs当实测。',
'R50':'有可读蓝图表；接单责任与恢复授权清楚分开，构造等待变化未虚报效果。',
'R51':'四类UCA具体情境均有对应，SC1/SC2机制不同且派生验证，未称穷尽或已有防线。',
'R52':'独立Bayes分支复算EVSI6/净3/弱信号0，行动阈值5/7正确；来源EVPPI与平台EVSI自推分开。',
'WB07':'两种智能分支清楚；时效只作门槛不推出实际停机/授权，泛化数据泄漏风险具体。',
'WB08':'消干涉但损失任务的B被拒，C保任务有明确几何变化；1D投影不冒三维可制造验证。',
'WB09':'局部初始加速度例可操作，未把它包装轨迹/稳定性/专著方程；相对误差分母可更清楚。',
'WB10':'熵权仅区分度非价值，恒定硬要求保留，版本/3A5A不混；建议在正文显示具体熵数帮助复算。',
'WB11':'原则/程序/资源/领域知识区别操作化，补证动作不变安全结论；全专著算法受限明确。',
'WB12':'关系类型和暂不合并有依据，但正式实体比较表会更便于实际去重；不伪造七类对应表。'}
dims=['身份边界与邻近法','机制及前提','判断回返与操作','完整例与中间产物','实质失败与迁移','来源与适配区分','可读性与交接']
for i,ss in selectors.items():
 f=src/'稿件'/f'{i}.md';ls=f.read_text().splitlines();ds={}
 for k,t in zip(dims,ss):
  matches=[(n,l) for n,l in enumerate(ls,1) if t in l];n,l=matches[0] if matches else (1,ls[0]);ds[k]={'assessment':'局部' if (i=='R46' and k=='完整例与中间产物') else '充分','locator':f'稿件/{i}.md:{n}','evidence':l,'scope':'本文明确限定的教学/适配范围；非原著全部实现或工程认证'}
 rows.append({'method_id':i,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'dimensions':ds,'review_comment':notes[i],'conclusion':'needs_content_revision' if i=='R46' else 'bounded_content_candidate_no_blocker_found'})
findings=[{'id':'CV-F01','severity':'P2','method':'R46','locator':'稿件/R46.md:11','problem':'技术编码段仍承诺下一步，没有真正输出已检CN/WO样本的机制对比和逐格摘要/权项证据。当前完整例只到文献身份/纳排，不覆盖景观核心技术编码。','repair':'基于已合法取得文本增两候选×至少三维技术编码表，每格绑定实际摘要/权项位置及未核身份；给至少一个由比较触发的具体后续研究问题，保留检索覆盖/FTO边界。','blocking_scope':'R46完整教学维度，其他20无此阻断'}, {'id':'CV-F02','severity':'P3','method':'WB09','problem':'初始加速度偏差约1%/100%没有明确相对误差分母，分母若用完整模型就是约.99%/50%。','repair':'明确相对于线性预测绝对值，或把两种归一口径列清。','blocking_scope':'不阻断局部适用判断，5%阈值在两种口径下均相同决定'}, {'id':'CV-F03','severity':'P3','method':'WB10','problem':'熵权给[1,0]但未写第一列熵值/离散度，初学者需自行补对数运算。','repair':'加H约.92062、1−H约.07938中间值，并说明样本列归一权仍为1。','blocking_scope':'可读性增强'}, {'id':'CV-F04','severity':'P3','method':'WB12','problem':'实体关系说明清楚，但2006/2010/2019真实例没有小型并列身份/操作/来源定位表。','repair':'补三来源身份及same_as不成立的差异表；不求重建七类全表。','blocking_scope':'可读性增强'}]
report={'reviewer':'independent Agent function_deepening; not domain expert certification','source_manifest_sha256':hashlib.sha256((src/'manifest.json').read_bytes()).hexdigest(),'read_scope':'all21 manuscripts full text; source map all21, selected new primary NIST CCD, Gero2004 author body and arxiv identity, inherited prior evidence selected; originals not all reread','review_basis':'ML021 seven dimensions, not word count or guard tests','methods':rows,'findings':findings,'summary':{'methods':21,'no_new_content_blocker_found':20,'needs_revision':['R46'],'not_claimed':['expert-level certification','full source monographs read','real-world efficacy','deployment approval']}}
(p/'逐稿七维独立内容审核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(p/'审核结论.md').write_text('''# validation21稿独立内容审核

已逐篇阅读21稿及来源映射，复算R38/R52等数值与新情景。20稿在明确限定范围内未发现阻断项；R46完整示范维度为局部，需要修订实际技术编码比较。详见逐稿JSON，所有维度有具体正文位置。Agent审核不替代领域专家，不因构造例缺真实现场而否定教学可读性，也不因例子算对就认定工程成功。

R46必须补两公开候选至少三技术维度的实际编码表，逐格绑定已读摘要/权项位置及未知；目前“下一步编码”没有完成该方法核心展示。其余三项为可读性/口径建议：WB09误差分母、WB10熵计算中间值、WB12实体比较小表。作者应保存旧冻结稿，在修订后交差异复核。

本次独立新情景包括R52中等信号仍未跨行动阈值、R47新阈值使集合为空、R43寿命4年需明确整数替换。它们用于核解释边界，不虚称原作者包处理了所有未知情景。原包只读，未复跑可能写原目录的作者编制脚本，独立计算写本审核目录。
''')
print('review21 written')
