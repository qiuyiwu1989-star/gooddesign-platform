"""Host Agent-authored reasoning using MCP-read methods and case evidence; not backend model output."""
import json
from method_engine import ROOT
OUT=ROOT/'output/rubber-tapping-pilot'
def build():
 task=json.loads((OUT/'task.json').read_text());brief=json.loads((OUT/'需求简报-作者整理.json').read_text());artifacts={'R48':brief}
 def add(rid,kind,payload,refs=[]):
  artifacts[rid]={'artifact_id':'RUBBER-'+rid,'revision':'r1','task_id':task['task_id'],'task_revision':task['revision'],'type':kind,'scope':'Host Agent研究草稿；客户型号、目标值、树体条件未确认；没有实验、专业审核或工程认证','conditions':[],'evidence_refs':refs,'payload':payload}
 functions=[('F1','识别对象并建立局部轨迹'),('F2','约束切入与耗皮'),('F3','完成受控切削'),('F4','排出并隔离切屑与旧胶线'),('F5','监测异常并安全退出'),('F6','清理、更换与复核配置'),('F7','导流收集并记录作业')]
 add('R14','FunctionModel',{'boundary':task['boundary'],'functions':[{'id':i,'verb_object':t,'necessity':'necessary','evidence_refs':[]} for i,t in functions],
 'flows':[{'id':'L'+str(i),'from_function':a,'to_function':b,'flow_type':typ,'description':d,'evidence_refs':[]} for i,(a,b,typ,d) in enumerate([('F1','F2','signal','传递几何参考与未确认的不确定性，不代表内部组织深度已知'),('F2','F3','signal','传递允许动作边界与暂停条件'),('F3','F4','material','新切屑与旧胶线进入废物流，避免与胶乳共通'),('F3','F7','material','胶乳进入独立收集路径，路径可行性待验'),('F5','F3','signal','异常时停止切削并进入预定义退出状态'),('F6','F2','signal','更换或清理后复核参考与限位，未经确认不复工')],1)],
 'interfaces':[{'id':'I1','text':'末端与移动/固定/手持平台接口未知；本模型不预选客户架构','kind':'unknown','evidence_refs':[]},{'id':'I2','text':'农艺和加工端需共同确认树体边界与胶乳质量判据','kind':'assumption','evidence_refs':[]}], 'unknowns':['功能关系为研究分解，不是已查明的客户失效因果','树体内部边界不能仅由外表面定位得到','异常退出时的能量、切刀姿态和人工接近条件待安全审核']})
 cases={'moon':'case-479a7157f5e4d5eecce6c304','weld':'case-0205da2905f4ccacbbb38094','polish':'case-a81a5bd5f1f2e791d5e1371c','surgery':'case-0290060f5fbcac9f3803c823','apple':'case-c1dd39efa2c949b7b81a8a58'}
 dimensions=[
 ('F1',[('现有定位方式待现场采集',[]),('局部机械导向与粗定位',['S03']),('表面视觉定位加局部机械参考',['S02',cases['polish']]),('人工引导与可检查的定位标记',['S03'])]),
 ('F2',[('现有限深与基准待现场采集',[]),('可调参考与限位；组织厚度未知时暂停',['S03']),('几何/力位信息协同但独立核查残余树皮',['S04',cases['weld']]),('可检查限深基准加人工确认',['S03'])]),
 ('F3',[('现有刀具与进给待现场采集',[]),('比较连续条状切削与分阶段进给，不预定刀形',['S05']),('沿局部轨迹切削并允许中途退出',['S02']),('电动辅助切削，人工掌握例外处理',['S03'])]),
 ('F4',[('现有切屑/胶线去向待现场采集',[]),('物理分隔废物流与胶乳，旧胶线独立处理',['S01','S05',cases['apple']]),('可拆卸隔离导流与堵塞观察，验证不阻流',['S01']),('人工可见清屑口及隔离托接，避免运行中接触刀具',['S01'])]),
 ('F5',[('现有异常保护与接管待现场采集',[]),('驱动状态与接触状态交叉核查，异常退让',['S02',cases['moon']]),('多信号状态机及接管，不将恒力视作安全深度',[cases['weld'],cases['surgery']]),('停机后人工复核，切断危险能量再排障',['S01'])]),
 ('F6',[('现有维护程序待现场采集',[]),('可拆卸接触件，复装后校验基准',['S05']),('模块更换与可追溯复标，适配接口待核',['S02']),('简化清洗换刀与可视检查，耗时待测',['S03'])]),
 ('F7',[('现有收胶与记录方式待现场采集',[]),('保留胶园收集方式，补充异常与品质记录',['S06']),('记录工况与结果，隔离新增导流部件造成的污染',['S01']),('人工收胶，记录总工时与有效产出',['S06'])])]
 options=[]
 for fid,variants in dimensions:
  for j,(p,refs) in enumerate(variants):options.append({'id':fid+'O'+str(j),'function_id':fid,'principle':p,'conditions':['研究选项；尺寸、材料、接口、允许损伤与安全条件待确认'],'evidence_refs':refs})
 labels=['客户现状占位，不是已测基准','机械参考与双物流隔离模块','感知辅助与可退让闭环末端','人机协作的低门槛改造']
 add('R17','ConceptSet',{'function_ids':[f[0] for f in functions],'options':options,'combinations':[{'id':'C'+str(j),'option_ids':[fid+'O'+str(j) for fid,_ in dimensions],'status':'unknown','reason':label+'；整体条件、机械兼容与所有关键门槛均未验证'} for j,label in enumerate(labels)],
 'compatibility':[{'option_ids':['F2O1','F5O1'],'status':'unknown','reason':'柔顺或力反馈不能单独证明组织限深，需验证基准与退出动作','evidence_refs':['S03',cases['weld']]},{'option_ids':['F4O1','F7O1'],'status':'unknown','reason':'废物流隔离不得造成胶乳滞留或接触件污染','evidence_refs':['S01']}],
 'unknowns':['C0仅为客户现状待调查占位；不得比较其虚构性能','C1—C3不是完整工程图或独立验证方案','公开专利后置检索涉及柔顺仿形与排屑，组合名称不代表新颖性']})
 requirements=brief['payload']['requirements']
 add('R36','ComparisonRecord',{'requirements_revision':brief['revision'],'baseline_id':'C0','candidate_ids':['C0','C1','C2','C3'],
 'criteria':[{'id':'K'+r['id'][1:],'text':r['text']+'；判据：'+r['acceptance'],'hard':True,'requirement_ids':[r['id']]} for r in requirements],
 'judgments':[{'candidate_id':c,'criterion_id':'K'+r['id'][1:],'value':'unknown','basis':'未取得同条件客户基线、已冻结验收目标或实测。该格保留未知，不以相同或中分填补。','evidence_refs':[]} for c in ['C0','C1','C2','C3'] for r in requirements],
 'recommendations':[],'sensitivity':['平台由手持变移动时，定位与转场代价可能改变路线取舍','树株差异、积胶速度及维护负担可能改变收益','所有硬软属性未决项暂按门槛保守处理，待客户澄清后再比较'],
 'unknowns':['N04/N05/N06/N08/N09/N10/N11/N12/N15硬软属性未决','没有可支持唯一技术路线推荐的证据','建议优先开展的补证活动不是对产品方案优劣排名']})
 measures=[('M1','切入位移、割后测量与损伤分别记录','mm及经农艺确认的损伤口径','测量定义、仪器、阈值与许可先确认；不得混用深度定义'),('M2','新切屑、旧胶线、杂质与收集损失','按加工方认可的质量/比例和时间单位','明确采样与对照，检查隔离是否反而堵塞或失胶'),('M3','完整作业周期与人工介入','s/株、人工min/合格产出；干胶口径待定','包括定位、切削、清理、转场与故障，不只报刀次时间'),('M4','异常退出与恢复','受控事件记录与复位条件','先完成安全审核和非活树测试；不制造危险现场故障'),('M5','维护和复标','min/次、错误与重试记录','清洗换刀后按已批准程序复核；阈值待操作方确认')]
 add('R44','PrototypePlan',{'hypothesis':'在明确基准与安全边界后，机械参考/废物流分离/可退让监测的组合可能改善清洁与可靠性；其收益和树体影响目前未知','learning_goal':'先分离限深、排屑、异常退出及维护因素，识别哪种机制值得进一步工程化','scope':'C1/C3可作为局部台架的待比较对象，C2按测量必要性补入；不是产品优选或现场试割许可',
 'procedure':['G0与客户及农艺人员确认对象、基线、测量口径和许可；未满足不得进入活树试验','G1在非生物替代件上核查运动范围、接口、废物流路径及失电退出；替代件不证明真实树皮切削','G2采用经许可的样本及专业监督做局部对照，独立控制旧胶线、表面曲率与刀具配置；不以同树重复刀次冒充独立样本','G3在已批准边界内进行小范围真实作业，记录整周期、品质、损伤、异常与人工介入；样本规模由变异与目标差异确定','G4按事先判据解释支持、反驳或不确定，保存失败与退出记录；通过对应门槛后再讨论整机'],
 'measurements':[dict(id=i,observable=o,unit_or_scale=u,criterion=c) for i,o,u,c in measures],
 'uncovered_questions':['短期局部测试不能证明跨周期树体健康或季节产量','缺少目标平台与真实材料，尚不能给出制造尺寸和控制增益','暂未完成真实用户培训、经济性与气候覆盖'],'execution_status':'planned'})
 add('R42','VerificationPlan',{'requirements_revision':brief['revision'],'matrix':[{'requirement_id':r['id'],'purpose':'verification','method':'test' if r['id'] in ['N01','N02','N03','N04','N07','N09','N13'] else 'analysis','criterion':r['acceptance'],'configuration':'待冻结的目标设备/树株与割面/环境/刀具与传感配置；当前仅规划','evidence_status':'planned','evidence_refs':[]} for r in requirements],
 'validation_questions':['目标经营者是否认可合格产出与成本口径，而非只认刀次速度？','操作员是否能理解停机原因、低负担接管并在复位前确认安全？','农艺和加工端是否接受树体影响与胶乳品质判断？','新增装置是否适配现有作业、转场和收胶方式？'],
 'uncovered_requirements':[],'execution_status':'planned'})
 (OUT/'Agent推理产物.json').write_text(json.dumps({'authoring_mode':'host_agent_using_MCP_read_method_and_case_content_not_backend_model_generation','artifacts':artifacts},ensure_ascii=False,indent=2));print('6 Host Agent artifacts authored, pending actual checks')
if __name__=='__main__':build()
