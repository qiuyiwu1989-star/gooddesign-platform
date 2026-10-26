"""ML-005 author-curated research intake, never a confirmed customer specification."""
import json,hashlib
from method_engine import ROOT,digest
OUT=ROOT/'output/rubber-tapping-pilot'
SOURCES=[
('S01','DG/T 315—2024 割胶机','https://www.moa.gov.cn/nybgb/2025/202501/202501/P020250114359428607129.pdf','官方PDF全文，重点§1、§3、§5.3和表4；表4截图核对','该鉴定大纲适用于电驱手持式和固定式设备；定义刀次时间并提出作业质量与可靠性评价。其深度测量刺入至木质部，不能与刀具切入位移混用。移动机器人需另核适用范围。'),
('S02','天然橡胶割胶机器人视觉伺服控制方法与割胶试验','https://www.smartag.net.cn/article/2020/2096-8094/2096-8094-2020-2-4-56.shtml','期刊HTML，§2、§3、§4；2020卷期，2021网络出版','研究样机采用双目视觉及多传感反馈，说明行业已有视觉路线。其切割深度与耗皮量有专门定义；该样机和试验树位结果不可直接外推到客户设备或异地胶园。'),
('S03','割胶机切割仿形机构设计与试验','https://www.aeeisp.com/zgnjhxb/en/article/doi/10.13733/j.jcam.issn.2095-5553.2024.02.010','期刊英文摘要，非全文','该研究设计了导向、斜面组件与切刀组成的限深限厚机构，并在手持式设备开展试验；仿形限深属于已有技术方向，不能仅以采用导向器声称首创。'),
('S04','Design and Experiment of Laser Ranging Depth Control Rubber Tapping Machine','https://www.j-csam.org/jcsamen/article/abstract/20250426?st=article_issue','2025年期刊摘要，非全文','已有激光测距调刀研究，涉及测距位置角度、工具调整和切割质量；摘要性能限于其试验配置，不能把报告的合格率当客户方案预测。'),
('S05','橡胶所在橡胶树机械割胶策略优化方面取得新进展','https://www.catas.cn/contents/9/246781.html','研究机构官方报道，非独立验证','研究团队把旧胶线处理与刀片、导向器及农艺参数联合研究；旧胶线干扰应与新切屑污染分开诊断。报道与所述Forests论文是同一研究链，不计作独立重复验证。'),
('S06','KAU Rubber Harvesting','https://www.celkau.in/Crops/cashcrops/rubber/harvesting.php','农业大学官方收获指南，Tapping及Rain guarding段落','该指南说明采胶方式应考虑品系、作业时段、耗皮与更新，并讨论雨水防护。因此产出异常不能只归因机械刀具；印度当地作业建议不直接移植为中国客户参数。'),
('S07','An Optimization Study on a Novel Mechanical Rubber Tree Tapping Mechanism and Technology','https://www.mdpi.com/1999-4907/14/12/2421','检索返回正文片段及附录；直开返回429，未逐页全文核读','检索可见立刃刀片与可调导向器设计、胶线缠绕及切屑污染讨论；只作既有技术线索，不采用其拟合方程、最优参数或数值效果为设计依据。'),
('S08','Comprehensive Evaluation of New Tapping Technologies for Rubber Trees','https://www.rdzwxb.com/EN/10.3969/j.issn.1000-2561.2026.07.011','2026年题录与检索摘要；页面摘要模板未渲染，未读PDF','最新检索摘要提示不同机采技术可能存在产胶、品质与伤口等权衡；因尚未取得正文，本实验不引用其数值结论，不据此排列设备优劣。')]
REQS=[
('N01','保护树体及长期割面资源','胶园经营者/农艺人员','避免短期增产以伤树或过度耗皮为代价',True,['S01','S06'],'在定义明确的深度、耗皮与损伤口径下测量，并安排跨周期跟踪；阈值待客户及农艺人员确认'),
('N02','区分表面跟随与真实限深','设备研发/农艺人员','适应树干曲率及树皮差异，同时控制生物安全边界',True,['S02','S03','S04'],'对曲率、厚度和旧割面分层试验；刀位移、剩余树皮及损伤分别记录；允许误差待定'),
('N03','隔离新切屑与胶乳','收胶人员/加工方','降低切屑混入及后续清理负担',True,['S01','S07'],'定义污染采样方法，比较杂质、损失胶乳及清理时间；限值待下游确认'),
('N04','处理旧胶线与黏附堵塞','操作员/维护人员','处理已有胶线、刀面黏附和排屑阻塞',None,['S05','S07'],'记录堵塞、停机、清理及重启；阈值待定，不能以空载切削代替'),
('N05','提高全流程有效产出','胶园经营者','提高单位人时的合格干胶产出，而非仅提高刀速',None,['S01','S06'],'同时记录定位、安装、切割、转场、收胶、清理、故障、人机协作时间及干胶口径；目标待实测'),
('N06','降低对熟练工的依赖','操作员/经营者','将关键判断转为可检查的设置与反馈',None,['S03','S05'],'新手与熟练人员分组，记录培训、误操作、返工与接管，不能仅调查喜欢程度'),
('N07','异常时安全退让并可接管','操作员/研发人员','失去接触、堵转或感知异常时停止危险切削并记录',True,['S01','S02'],'在受控环境验证急停、断电、传感异常、退出路径与复位条件；先安全审核'),
('N08','适应雨水与弱光的作业安排','胶园经营者/操作员','识别不适合作业条件并避免为自动化强行作业',None,['S02','S06'],'现场调查光照、湿度、雨后割面和允许时段；雨水防护不等于雨中可割'),
('N09','可清洗维护和耗材更换','维护人员','降低刀具、导向件与胶乳接触区维护负担',None,['S05','S07'],'计时清洗、换刀、复装校准，跟踪磨损和积胶；材料与费用未知'),
('N10','兼容现有胶园与装备','设备方/胶园','在手持、固定与移动架构之间避免过早锁定',None,['S01','S02'],'调查树距、坡度、挂载接口、供电与收胶流程，再确定目标平台'),
('N11','保持可追溯的作业与验收数据','经营者/研发人员','知道哪棵树何时按何配置作业，问题可追查',None,['S01','S02'],'记录树ID、时间、工具版本、工况、异常和数据缺失，不编造客户已有数字化基础'),
('N12','可比较的全生命周期经济性','采购方/运营方','把人工、维护、停机、折旧及树体影响纳入选择',None,['S01','S06'],'采集实际成本与利用率，用情景区间比较；不输出无数据ROI'),
('N13','保护胶乳有效品质与收集率','加工方/收胶人员','避免通过增加水分或牺牲品质制造表面增产',True,['S01','S06'],'由加工方确认干胶含量、杂质和收集损失测量方法；不能以初始流速代替季节产量'),
('N14','识别不适用树株并保留人工例外','农艺人员/操作员','对厚度未知、旧伤、树结或状态异常的对象先停止或转人工',True,['S02','S06'],'定义适用树株与例外规则，记录覆盖率与误拒绝；识别能力需验证'),
('N15','分阶段改造与可撤销试点','经营者/设备研发','先验证末端或局部改造，再决定整机投入',None,['S03','S04'],'完成接口勘察与局部验证，不把试验优先顺序解释成已选定产品架构')]
def build():
 sources=[{'id':s,'title':t,'url':u,'read_scope':scope,'research_note':note,'accessed_at':'2026-10-26','verification':'author_read_not_independent_expert'} for s,t,u,scope,note in SOURCES]
 requirements=[{'id':i,'title':title,'stakeholder':actor,'need':need,'hard_proposal':hard,'status':'research_proposed_not_customer_confirmed','source_refs':refs,'acceptance_proposal':accept,'target_value':None} for i,title,actor,need,hard,refs,accept in REQS]
 intake={'schema':'research-demand-intake-0.1','request_id':'RUBBER-20261026','revision':'r1','origin':'user_supplied_meeting_plus_public_research_not_customer_approved','scenario':'rubber_tapping_research_pilot','requirements':requirements,'sources':sources,'unknowns':['目标企业、设备型号与架构','品系、树龄、树皮及树围分布','实际全流程效率与胶乳质量','预算、接口和验收负责人','农艺许可与现场试验条件'],'approved':False}
 (OUT/'需求包.json').write_text(json.dumps(intake,ensure_ascii=False,indent=2)+'\n')
 evidence=[]
 for s in sources:
  text=s['research_note'];evidence.append({'id':s['id'],'server':'public_research_notes','project_id':'RUBBER-20261026','source_id':s['id'],'source_revision':'research-note-'+hashlib.sha256(text.encode()).hexdigest(),'locator':s['read_scope'],'text':text,'text_sha256':hashlib.sha256(text.encode()).hexdigest(),'url':s['url'],'read_scope':s['read_scope'],'support_review':'author_paraphrase_not_independent_semantic_validation'})
 (OUT/'private/research-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2))
 task={'task_id':'RUBBER-20261026','revision':'r1','object':'rubber tapping end-effector and operating workflow','desired_outcome':'研究兼顾树体保护、胶乳洁净和有效产出的改进路线；研究需求N01—N15均为待客户确认，不得给出唯一工程推荐','boundary':'研究/概念/试验计划；平台架构、客户工况及目标值未知，不执行树体试验','delivery_level':'concept','stage':'frame','demand_packet_sha256':digest(intake),'source_policy':'公开研究笔记是作者释义而非逐字原文；案例指标不迁移为客户参数；所有需确认的硬软属性保持未知。'}
 brief={'artifact_id':'RUBBER-research-brief','revision':'r1','task_id':task['task_id'],'task_revision':'r1','type':'ProblemBrief','scope':task['boundary'],'conditions':[],'evidence_refs':[], 'payload':{'actor':'潜在胶园经营者、操作与农艺人员、设备方、加工方，尚未访谈确认','object':task['object'],'boundary':task['boundary'],'desired_outcome':task['desired_outcome'],'requirements':[{'id':r['id'],'text':r['title']+'：'+r['need'],'hard':r['hard_proposal'],'acceptance':r['acceptance_proposal'],'status':'proposed','evidence_refs':r['source_refs']} for r in requirements],'conditions':[],'unknowns':intake['unknowns']}}
 (OUT/'task.json').write_text(json.dumps(task,ensure_ascii=False,indent=2));(OUT/'需求简报-作者整理.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2))
 print('15 requirements, 8 research sources; client confirmation pending')
if __name__=='__main__':build()
