"""Render authored 64-method analyses with explicit acquisition/review boundaries."""
from pathlib import Path
import csv,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'));import method_library_catalog as catalog
oldbase=ROOT/'02-研究/ML-014-逐法深度研究'
previous=json.loads((oldbase/'研究总索引.json').read_text())
prior={x['research_id']:x for x in previous['methods']}
rows=list(csv.DictReader((BASE/'逐法研究判断.tsv').open(),delimiter='\t'))
assert len(rows)==64 and len({x['id'] for x in rows})==64
assert {x['id']for x in rows}=={x['research_id']for x in catalog.catalog()['methods']}
traces={r['id']:r['trace']for r in csv.DictReader((BASE/'逐法推演片段.tsv').open(),delimiter='\t')}
assert set(traces)=={r['id']for r in rows}
sources=json.loads((ROOT/'output/method-deepening-ML017/来源取得清单.json').read_text())['sources']
# These are the sections actually read or visually checked, never a declaration of full-text review.
review={
 '1ea6a457c53a19':'VDI目录项的2019-11版本、56页及公开摘要；未得标准正文。',
 '6e59bc8d6b4505':'四活动与非线性迭代说明段；不据此声称真实用户调研已完成。',
 '70e514c9ce7cd1':'Empathize开头及对应观察/访谈说明选段，非90页逐卡精读。',
 '36974a25c56fb3':'章节结构、迭代递归关系及四个设计过程的开篇选段；非NASA全手册。',
 '3deac9d19ba477':'公开介绍中2021版扩展V模型及跨专业关联选段；非标准全文。',
 'fba0cea6d64896':'阶段/关口和资源取舍说明选段；未采纳营销效果自述。',
 '2e6f97d2443320':'Interview场地、角色及提问记录说明选段。',
 '7cf3d3e2546528':'Immersion中的现场观察、具体细节与解释区分选段。',
 '8c2f208bf1f61e':'Definition与功能/社会/情绪进步说明选段。',
 'd019b673f25b90':'正反提问、定性预测试及问卷描述修订选段；这是GitLab实践规则，非Kano原论文。',
 'b39b61aabf112b':'Quick Facts前部对QFD系统与客户需要的范围说明。',
 '5b972eb496a481':'任务分析、身体与心理负荷及人机任务分配选段。',
 '289e675ee4f9b7':'动词—名词功能表达及VA/FAST引入选段；署名镜像不是官方标准全文。',
 'a5e31f14938f68':'维度定义、CCA、逻辑/实证/规范区分选段；未把一致性当工程因果。',
 '62468ffaf44195':'Definition Check和抽象机制选段；未研究某具体生物机制实验。',
 '820b977a2996e9':'教学协议的逐轮变体和独立记录页面选段；不复制完整卡组。',
 'c6e6e3c60c314d':'作者论文摘要与四操作引入选段；不称完整形式理论复刻。',
 'ab8da70006b071':'问题识别后调用求解工具的范围说明。',
 'dde5c990ae25d2':'技术矛盾定义与改善—恶化关系选段；未取得完整矩阵。',
 '8357b008cf4eef':'工程/物理矛盾定义、参数数量与IF-THEN-BUT关系选段。',
 '28037986929927':'IFR定义及不引入新问题的目标性说明选段。',
 '3d888c93cbcc21':'标准解集合身份及物场表示选段；不是76条规则逐项核读。',
 'acc2ade884bbd9':'裁剪的功能重新分配及新问题产生选段。',
 'f5efc967c71241':'三页作者文章中直接搜索局限与FOS引入选段。',
 '398980e246690f':'趋势定义及其普适性自述选段；后者未独立证实，不当经验规律保证。',
 '38bd446b3bf260':'正文确为MIT公理化设计组介绍；四域与FR/DP定义选段，异常网页标题不等正文错误。',
 '3b1d1bea2a691d':'矩阵表示、聚类和排序用途选段；未对新产品执行模块优化。',
 'eaa96ff0e7bf82':'PDF页10—14附近机构示例与自由度/冗余约束提醒选段；非完整尺寸综合教材。',
 'd247c4b724b84d':'PDF页8—9附近功能/约束/目标与筛选框架选段；非全部材料物性数据。',
 'b18d5a36476ccd':'DFA先于DFM及二者不同对象的选段；成本数字未作性能依据。',
 '392de718b73e30':'官方教育用途、代码版本和扩展说明选段；未在本轮重新运行拓扑求解。',
 '1d36767043e2ad':'Phase2多方案及记录草图选段；不是Pugh原著完整规则。',
 '18e1e179c6b680':'决策分析的判断、偏好、不确定性和记录输出选段。',
 'db45a51a2a26fd':'二水平全因子设计、8次运行不含重复/中心点选段。',
 '9e02478b4c808a':'残差与模型修订方法目录选段，不等完整诊断算法。',
 'b0f9f11d61645c':'Taguchi设计与分数因子、离线质量控制概念选段。',
 '6c258a00f3bff8':'危险对应风险评估及安全整合要求选段；英国指导不等其他地区法规。',
 '8f7f8e52e95da5':'端到端测试与接口/整体功能核对选段。',
 'a02af2c01912a0':'确认活动中模型、模拟、演示与检查的区别选段。',
 '3b72217e354436':'价值工程job plan入口及四步组织说明；非完整SAVE标准。',
 'd907d9edb9e6fa':'本轮只取得页面，未以导航摘录声称新核方法操作细则。',
 'e08babc792e151':'步骤1—3的跨职能支持、单场景范围及前后台研究选段。',
 'e469186f8f8337':'PDF标题/作者、页35—36控制模型及页69—73四类UCA选段；79页讲义非2018完整手册。',
 '02426f074883c4':'论文标题、VOI依赖模型结构以及EVSI未在该例展示的说明选段。',
 '7094e23ebd42b9':'本人署名文中3I/7D/1+3+X/5A与12+1的明确文字选段；作者效果自述不当独立评估。',
 '73cc05e7e8d064':'2003论文PDF页1—2题名、作者、三化与广义质量概念选段；非2017专著。',
 '0bcbf490afa7cc':'2007论文PDF页2（刊页386）第二、三节文字和两图；已渲染视觉核读。',
 'c68660f3727f00':'2006论文PDF页1（刊页532）提取乱码，改用渲染视觉核读题名、作者、摘要和图1；其余公式未核。',
 'd76c2cae30871f':'2010论文PDF页1题名、作者、摘要；未复现熵权—模糊评价全流程。',
 'd23c41d4f337f3':'公开32行数据、26参数原响应模型及高阶项汇作误差假设选段；实际复算前一模型，不声称最终Box-Cox模型复现。',
 'b6a18fc13508a1':'NASA附录C的主动主体、可追溯、假设确认及可检验要求选段。',
 '919ea5c2ea32d2':'NIST官网框架范围及页面标为Initial Public Draft；未宣称正式标准。',
 '6890cadeb38392':'取得官方新入口，未据导航抽取声称比既有Framework更多新方法规则。',
 '736133f585ed01':'Course Description明确2026短手册是用户创新案例汇编；与22页实际文件相符。',
 'a4038373ecaf8a':'GSFC-HDBK-8004范围、4.3相关选段及PDF页23量表渲染核对；不同量表不可直接通用。',
 '894dfe33616eca':'HSG245四阶段及PDF页18—24附近原因、控制行动、责任选段；非88页逐题精读。',
 'fd8d6fd7514e96':'WIPO Guidelines目录、7.4与8.2.3检索策略分享选段；131页全文已取得但未逐页核读。',
 '8c253444e18683':'Ansys四项设计因素及固定几何例外的完整短页文字。',
 'a2d2265d5ce94d':'EPA机构题录与文献身份；未因此声称LCA正文取得。',
}
issues={
'dc9106315b7393':'本轮仅Research Portal壳，无论文摘要或全文，不能沿用旧读范围冒充本轮新读。',
'a36a84764e2af5':'目标PDF请求实际重定向院系首页，不是论文；按内容拒绝。',
'eebede67398607':'仅EPA PURL展示标题壳，不能支持LCA操作主张。',
'e46f9fc7583e01':'返回MIT脚本维护说明，不是STPA页面或手册。',
'9aa813652559dc':'实际22页2026案例汇编，不是原Lead User Project Handbook；身份须更正。',
}
for x in sources:
 x['selected_read_scope']=review.get(x['id'],'本轮未核读有效内容；失败/机器取得不等于文献研究完成。')
 if x['id']in issues:x['identity_issue']=issues[x['id']]
 x.pop('text',None);x.pop('raw',None)
(BASE/'来源复核台账.json').write_text(json.dumps({'date':'2026-10-27','scope':'availability_and_bounded_selected_section_review_not_all_fulltexts','sources':sources},ensure_ascii=False,indent=2))
out=BASE/'逐法档案';out.mkdir(exist_ok=True);manifest=[];index=[]
for row in rows:
 rid=row['id'];d=catalog.read(rid);p=prior[rid];old=oldbase/p['report'];assert hashlib.sha256(old.read_bytes()).hexdigest()==p['sha256']
 ss=[s for s in sources if rid in s['methods']]
 text=f"# {rid} · {d['name']}：第二轮深化研究\n\n2026-10-27。范围：既有研究与来源状态复核、平台原创深化分析及验证设计。不是64部原典逐页精读、独立专家认证或现场工程验证。\n\n"
 text+='## 本方法值得深入的核心\n\n'+row['focus']+'\n\n## 真正需要专家判断的地方\n\n'+row['decision']+'\n\n'
 text+='## 应交付怎样的完整研究包\n\n'+row['artifact']+'\n\n这些产物中，除R38公开数据局部复算与R33构造材料模型复算外，本轮不将建议或既有教学包改写为新做的现场实验。\n\n'
 text+='## 一段可跟随的判断推演\n\n'+traces[rid]+'\n\n除R33、R38明确标注的数学复算外，本段为平台构造的思考示例，不是来源原案例、客户事实或已执行现场试验。\n\n'
 text+='## 必须能识别的失败反例\n\n'+row['negative_case']+'\n\n这是一条用于审查的构造反例，不是本客户真实事故记录。\n\n'
 text+='## 与引擎及其他方法的交接\n\n'+row['handoff']+'\n\n建议引擎返回“可继续研究／应补材料／仅作启发／不适用”的原因、所用版本和所缺证据。这里的建议尚未改写现有MCP契约。\n\n'
 text+='## 本轮来源取得与核读边界\n\n'
 for s in ss:
  text+=f"- [{s.get('title') or s['url']}]({s['url']})\n  - 机器取得状态：`{s['status']}`；证据ID：`{s['id']}`。\n  - {s['selected_read_scope']}\n"
  if s.get('identity_issue'):text+='  - 身份问题：'+s['identity_issue']+'\n'
 text+='\n## 承接的既有资料\n\n'+f"第一轮报告：[原报告](../../ML-014-逐法深度研究/{p['report']})，本轮核对SHA256 `{p['sha256']}`。冻结方法档案由catalog.read校验。\n\n"
 text+='未决缺口保留：\n\n'+''.join('- '+v+'\n' for v in p.get('unresolved',[]))
 text+='\n以上是第一轮记录的缺口，不能直接视作最新教学升级缺陷。R01/R02/R03/R04/R14/R17/R36/R42/R44/R48已有独立范围的教学展示；后续实施先核对对应升级版本，不重复覆盖。\n'
 fp=out/(rid+'.md');fp.write_text(text)
 entry={'research_id':rid,'name':d['name'],'report':str(fp.relative_to(BASE)),'sha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'status':'bounded_research_and_deepening_design','new_engineering_validation':False,'expert_certified':False,'priority_focus':row['focus'],'source_ids':[s['id']for s in ss],'full_primary_texts_all_reviewed':False}
 manifest.append(entry);index.append(f"|{rid}|[{d['name']}]({entry['report']})|{row['focus']}|{row['artifact']}|")
(BASE/'64项深化索引.md').write_text('# 64项逐法深化索引\n\n52个方法档案与12个闻邦椿谱系专题，均有单独分析。此表为第二轮深化研究与具体补强设计，不是64项完整原典研究或64项执行器交付。\n\n|ID|档案|核心深化点|具体产物|\n|---|---|---|---|\n'+'\n'.join(index)+'\n')
from collections import Counter
summary={'round':'ML-017','date':'2026-10-27','reports':64,'methods':52,'lineage_topics':12,'all_ids_match_catalog':True,'prior_report_hashes_verified':64,'public_url_attempts':len(sources),'machine_acquisition_status':dict(Counter(s['status']for s in sources)),'all_original_fulltexts_read':False,'new_expert_certifications':0,'online_library_changed':False,'new_mcp_execution_contracts':0,'methods_index':manifest}
(BASE/'研究清单.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in summary.items()if k!='methods_index'},ensure_ascii=False))
