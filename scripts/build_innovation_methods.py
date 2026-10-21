# coding: utf-8
"""040: author three versioned platform method cards; no third-party text copied."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];LIB=ROOT/'04-知识库/创新方法库'
SOURCES={
 'SRC-DC':dict(publisher='Design Council',title='Framework for Innovation',url='https://www.designcouncil.org.uk/resources/framework-for-innovation/',locator='The process: Discover/Define; design principles',basis='先了解受影响者，再界定挑战，迭代核对理解。',rights='原站框架标CC BY 4.0；本卡为注明来源的平台操作改编'),
 'SRC-NASA':dict(publisher='NASA',title='Systems Engineering Handbook · 4.3 Logical Decomposition',url='https://www.nasa.gov/reference/4-3-logical-decomposition/',locator='4.3.1.2.1–4.3.1.2.2',basis='将目标和要求分解为功能，并明确功能之间的接口。',rights='链接引用；未复制原书或图'),
 'SRC-ALT':dict(publisher='Official G.S. Altshuller Foundation',title='Contradictions: Administrative, Technical and Physical',url='https://www.altshuller.ru/world/eng/triz6.asp',locator='technical contradiction; physical contradiction; spatial and temporal separation',basis='区分期望冲突、参数间的改善/恶化、同一对象的相反要求，研究分离可能。',rights='原典权利归原权利人；仅题录与简要释义，不复制原文')}
def step(mid,n,title,operation,inputs,output,checks,queries=(),stop='缺少必需信息则记录待补，不填造数据'):
 return dict(step_id=mid+'-S%02d'%n,title=title,purpose=title,operation=operation,input_refs=inputs,depends_on=[]if n==1 else[mid+'-S%02d'%(n-1)],output_key=output,knowledge_query_ids=list(queries),checks=checks,stop_condition=stop)
def inp(key,label,required=True,typ='object'):
 return dict(key=key,label=label,type=typ,required=required,missing_action='ask_or_stop'if required else'mark_unknown_and_limit_output')
def query(qid,purpose,entity,fields,exclude):
 return dict(query_id=qid,purpose=purpose,entity=entity,fields=fields,evidence_requirement='区分原文事实、平台分析和目标假设；结论需定位块和版本',exclude=exclude,context_priority=['硬约束','问题/功能','机制与边界','验证','原文'],limit=3)
def card(mid,name,purpose,source,inputs,steps,outputs,questions,exclusions,queries,failures,checks,composable):
 return dict(schema_version='method-card-1.0',method_id=mid,version='1.0.0',status='pilot_ready',name=name,aliases=[],provenance=dict(nature='platform_adaptation',sources=[dict(source_id=s,**SOURCES[s],accessed_at='2026-10-21',read_scope='relevant_full_web_sections')for s in source],original_authors=['G.S. Altshuller'if s=='SRC-ALT'else SOURCES[s]['publisher']for s in source],adaptations=['字段、操作步骤、证据标准、提问与检查规则由平台设计，不作为原作者逐字方法或官方认证版本','用于案例回看时属于平台重构，不认定原研发团队采用本方法'],rights='平台编写部分可用于本项目；外部原典依各自权利'),purpose=purpose,stages=[name],triggers=questions,preconditions=[i['label']for i in inputs if i['required']],exclusions=exclusions,missing_input_questions=questions,inputs=inputs,steps=steps,knowledge_queries=queries,outputs=[dict(key=o,label=l,kind=k)for o,l,k in outputs],quality_checks=checks,failure_cases=failures,composable_with=composable,evaluations=[dict(id=mid+'-EVAL-01',scenario='关键输入缺失',expected='追问或停止，保留未知'),dict(id=mid+'-EVAL-02',scenario='嫦娥→工业颗粒材料取样模拟任务',expected='原文事实/平台解释/目标假设分层，输出可追溯'),dict(id=mid+'-EVAL-03',scenario='目标硬约束冲突',expected='相关方向排除或降为条件性，不用案例相似覆盖约束')],review_status='platform_structure_reviewed_not_method_expert_certified',validation_status='engineering_effect_not_validated',change_log=[dict(version='1.0.0',date='2026-10-21',reason='首批可执行方法卡，验证与项目库的证据联动')])
def build():
 a='IM-PD-001';b='IM-FA-001';c='IM-CA-001'
 cards=[]
 cards.append(card(a,'问题定义','把企业愿望整理为对象、情境、目标、约束、成功口径与待确认的问题简报。',['SRC-DC','SRC-NASA'],[inp('task','用户/模拟任务'),inp('project_context','项目知识背景',False)], [
 step(a,1,'建立任务边界','明确谁在何处对什么对象完成什么工作，保留需求来源和模拟/真实标签。',['task'],'task_boundary',['对象和目标清楚','不把模拟输入写成访谈事实']),
 step(a,2,'区分症状、目标和原因假设','记录观察到的现象、希望获得的效果、对原因的猜测；没有企业数据时症状和基线留空。',['task','task_boundary'],'problem_layers',['原因不是事实标签','不把已有技术方案写成唯一目标']),
 step(a,3,'检查约束与知识参照','核对硬约束、可变条件和未知；从源项目提取问题/功能结构作参考，不移植其数值。',['task','problem_layers'],'constraint_map',['硬约束优先','来源目标与企业目标分开'],['PD-Q1']),
 step(a,4,'定义成功口径与追问','将成功拆成独立可测量维度：对象、指标、单位、工况、阈值与测量方法。缺少阈值则记录确认责任。',['constraint_map'],'success_and_questions',['未知不补0','样品质量不能替代层序保持','无基线不计算提升'],['PD-Q2']),
 step(a,5,'形成问题简报与阶段许可','汇总目标、边界、缺口和关键假设；输入足够可做概念探索，缺工况/阈值则禁止定型和效果承诺。',['task_boundary','problem_layers','constraint_map','success_and_questions'],'problem_brief',['每项要求可回溯需求','明确允许与禁止的输出'])],
 [('problem_brief','问题简报','analysis'),('success_and_questions','成功指标与追问','provisional_requirements')],['服务谁，处理什么对象？','现状与基线有什么记录？','哪些限制绝对不能改变？','成功由什么指标和阈值判定？'],['关键对象和目标未知时先追问','紧急安全处置不能等候此研究流程','本方法不替代用户验证或正式需求评审'],[query('PD-Q1','发现问题结构而非行业名称相似','problem',['title','scenario','goal','constraints'],['整器全部技术','目标领域未验证结论']),query('PD-Q2','检查指标对象与工况口径','metric',['subject','value_kind','unit','conditions','qualifier'],['任务总量替代子系统结果','地面参数当企业默认值'])],['把我想要某机器人直接当完整问题','没有基线却输出效率提升','把来源约束误当企业已确认限制'],['目标不预设唯一解','事实/假设/未知可区分','硬约束和验收口径可追溯'],[dict(next_method=b,binding={'problem_brief':'problem_brief'},gate='至少具备对象、目标和初步边界')]))
 cards.append(card(b,'功能分析','将任务拆成对对象产生作用的功能和接口，识别有用作用、有害作用及不足。',['SRC-NASA'],[inp('problem_brief','上一步问题简报'),inp('project_mechanisms','项目机制与证据')],[
 step(b,1,'确定系统与超系统边界','区分待设计系统、对象、操作者与外部环境；现有企业系统未知时只建目标功能模型。',['problem_brief'],'system_boundary',['目标功能模型不是现有设备实测']),
 step(b,2,'分解必要功能','使用动词+对象描述功能及输出，关联上一阶段成功指标；保持功能与物理部件的区别。',['system_boundary','problem_brief'],'function_tree',['每个功能服务一个要求','保留替代实现空间'],['FA-Q1']),
 step(b,3,'描述作用关系','记录作用主体、作用、受体、结果、阶段、类型及依据；有害作用的目标发生情况未知则标风险假设。',['function_tree','project_mechanisms'],'interaction_model',['有害/不足/缺失不混用','每条关系有事实或假设标记']),
 step(b,4,'核对接口与失效链','描述前一环节的输出怎样进入后一环节；标出颗粒、运动、封口、转送等接口的条件及可能失效。',['interaction_model'],'interface_risks',['单件成功不等于整链成功','专利候选不等于整机采用'],['FA-Q2']),
 step(b,5,'确定优先分析的功能问题','按影响与未验证程度选择问题；把关系及接口作为下一步矛盾候选输入，不编造风险概率。',['function_tree','interaction_model','interface_risks'],'function_model',['给出焦点与理由','不将功能图视为工程验证'])],
 [('function_model','功能与接口模型','analysis'),('interface_risks','接口风险清单','hypotheses')],['系统边界是什么？','每个功能的输入输出是什么？','哪些作用必要，哪些作用有害或不足？','哪一个接口最需要验证？'],['企业现有设备不详时不宣称已找到真实故障根因','不能用部件罗列替代功能分析','危险工艺仍需专业安全评审'],[query('FA-Q1','借鉴作用结构与机制','innovation',['measure','mechanism','failure_boundary','tradeoffs'],['平台解释冒充研发团队原始决策']),query('FA-Q2','核对部件关系与接口','technology',['function','principle','interfaces'],['专利构型当型号实配'])],['只列钻头、电机、软袋没有动作或受体','未见企业数据却标已发生故障','以一个部件性能代替全流程质量'],['作用有主体动作受体结果','接口指向明确','每条目标关系区分需求/假设/事实'],[dict(next_method=c,binding={'function_model':'function_model','problem_brief':'problem_brief'},gate='至少明确一个功能目标及其潜在不利影响')]))
 cards.append(card(c,'矛盾分析','将功能问题转成可核对的改善/恶化关系，区分技术矛盾与物理矛盾候选，提出带验证条件的方向。',['SRC-ALT'],[inp('problem_brief','问题简报'),inp('function_model','功能与接口模型'),inp('evidence','原文和试验边界')],[
 step(c,1,'筛选是否构成矛盾','只有愿望冲突时继续追问；检查是否有证据表明某项改进导致另一项变差。区分源项目陈述与目标假设。',['function_model','evidence'],'conflict_candidates',['愿望清单不是已证实技术矛盾','专利自述不是比较试验']),
 step(c,2,'形成技术矛盾表述','说明在什么条件下，哪项设计改变改善什么、恶化什么，保存原因链和支持程度。',['conflict_candidates'],'technical_contradictions',['改善量和恶化量可测','不强配未经核实的矩阵参数编号'],['CA-Q1']),
 step(c,3,'检查物理矛盾候选','检查同一对象是否在明确条件下需要相反属性；正常的先开后关可能只是工序切换，不能直接称发明矛盾。',['technical_contradictions','function_model'],'physical_candidates',['同一对象/属性/条件明确','不足信息保持候选']),
 step(c,4,'提出分离与替代思路','探索时间/空间的条件分离及接口/功能分担，保留替代解释。此为平台启发式组合，不伪称已调用矛盾矩阵或最优原理。',['technical_contradictions','physical_candidates'],'resolution_directions',['方向要解释如何影响矛盾','记录新增复杂性或风险'],['CA-Q2']),
 step(c,5,'用硬约束筛选方向','逐一核对材料接触、传感、空间等约束；冲突则排除，未知则条件性保留，不给假精确适配分。',['resolution_directions','problem_brief'],'filtered_directions',['相关性不能覆盖硬约束','目标实测与可制造性未知则不定型']),
 step(c,6,'形成验证与企业决策包','为每个方向指定关键假设、对照、测量口径、需企业确认的阈值、通过/停止条件与下一决策。',['filtered_directions','evidence'],'enterprise_brief',['没有试验不得宣称有效','经济收益和性能数值不猜填'])],
 [('enterprise_brief','企业创新研究建议','concept_hypotheses'),('technical_contradictions','矛盾及证据表','analysis'),('filtered_directions','条件性方向与验证计划','unvalidated_hypotheses')],['改善什么会恶化什么，因果证据是什么？','相反要求是否属于同一对象和属性？','哪些要求可按时间或空间分开？','新增方案会带来什么代价？'],['未找到因果关系则输出待验证矛盾','不可用愿望强行填矩阵','不提供侵权/许可或权利有效性结论','本方法不保证产生可实施发明'],[query('CA-Q1','查构型取舍及原始范围','innovation',['baseline','tradeoffs','failure_boundary'],['仅关键词相似','未知目标数值']),query('CA-Q2','检查验证的材料与局限','validation',['method','result','limitations','material_apparatus'],['把地面5次对照当企业保证'])],['强行把所有问题归为TRIZ矛盾','正常工序切换自动被判发明','无原矩阵却输出矩阵命中编号','先给方案再忽略目标约束'],['矛盾有证据或明确假设标签','分离方向有作用解释与代价','每个方向有验证和退出条件'],[]))
 for m in cards:
  f=LIB/'方法'/m['method_id']/m['version']/'方法卡.json';f.parent.mkdir(parents=True,exist_ok=True);text=json.dumps(m,ensure_ascii=False,indent=2)+'\n'
  if f.exists()and f.read_text()!=text:raise ValueError('已存在不同版本内容，禁止覆盖:'+str(f))
  f.write_text(text)
 index=dict(schema_version='method-catalog-1.0',status='pilot_library',registered_methods=len(cards),methods=[dict(method_id=m['method_id'],version=m['version'],name=m['name'],purpose=m['purpose'],status=m['status'],search_terms={'IM-PD-001':['问题界定','需求澄清'],'IM-FA-001':['功能分解','功能建模'],'IM-CA-001':['TRIZ','技术矛盾','物理矛盾']}[m['method_id']],sha256=__import__('hashlib').sha256((LIB/'方法'/m['method_id']/m['version']/'方法卡.json').read_bytes()).hexdigest(),path=str((Path('方法')/m['method_id']/m['version']/'方法卡.json')))for m in cards],task_facets=[m['name']for m in cards],evaluation_note='结构、检索与固定示例可测试；非专家认证或工程有效性验证')
 (LIB/'方法目录.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
 print('Created',len(cards),'method cards; steps',sum(len(m['steps'])for m in cards))
if __name__=='__main__':build()
