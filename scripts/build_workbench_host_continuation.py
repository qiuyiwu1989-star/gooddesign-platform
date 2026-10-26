"""ML-007 explicit Host-authored continuation after R17 model timeout, not model output."""
import copy
import json
from pathlib import Path
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/method-workbench-check/ml007'
if (OUT/'host-continuation.json').exists():
    raise ValueError('Archived Host continuation exists; write a new revision instead')
s=json.load(urlopen('http://127.0.0.1:8788/api/execution/RUBBER-20261026'))
state=s['state'];brief=state['submissions'][0]['artifact'];fm=state['submissions'][1]['artifact']
old=json.loads((ROOT/'output/rubber-tapping-pilot/Agent推理产物.json').read_text())['artifacts']
# Host alternatives, not demonstrated mechanisms. No imported source claims or performance values.
principles={
'F01':['定位后分段部署的可撤销模块','有定位状态记录的模块化挂载','人工移动与工具辅助，保留现有收胶方式'],
'F02':['人工按农艺清单判定，不明树株拒绝作业','多源状态提示加人工复核，不自动批准未知树株','人工逐株适用确认，记录拒绝原因'],
'F03':['局部机械参照与可检查定位点','表面几何测量配局部接触参照，保留坐标误差','人工粗定位配可见标记，禁止凭标记推断余皮'],
'F04':['可锁定设置与开工前清单','界面显示量测不确定性及许可状态','人工设置和双人关键条件复核，权限待定'],
'F05':['可调机械限位，未知皮厚不得试割','独立限深参考与位移反馈；余皮测量仍须另证','可检查深度基准加人工确认，不把经验视为量测'],
'F06':['受限行程的分段进给，刀形保持开放','局部轨迹进给并设置中途退出状态','电动辅助切削，人工处理例外，禁止带能量排障'],
'F07':['切屑路径与胶乳路径的物理分隔','可拆卸分隔与堵塞可视观察，不默认需要气流','停机后可见清屑口与独立托接'],
'F08':['旧胶线独立清理路径，先停止再清理','黏附与堵塞状态提示，未知状态中止','人工停机处理旧胶线，计入总工时'],
'F09':['可拆卸独立导流件，检查失胶和积胶','收集批次与工具状态关联，不默认增加在线化学传感','保留既有人工收集，记录污染和收集损失'],
'F10':['机械停止与能量隔离，退出能力需独立检验','多状态许可与人工接管，退出前核对残余能量','操作者可达停止装置与停机复核，不保证随时可接管'],
'F11':['可拆接触件与复装基准检查','工具模块版本记录与复标状态联锁','简化人工换刀清洗，复装后可视检查及必要校准'],
'F12':['受控供能接口和停机能量隔离','供能状态与退出需求协调，不假定失电自动安全','保留现有合规供能，增改接口前审查'],
'F13':['离线树ID和配置/异常记录','工具版本、时间和状态关联记录，基础设施待核','人工表单记录完整周期及缺失信息'],
'F14':['按统一口径汇总人时、品质及树体跟踪','经批准量测链汇集数据，未量测不计算ROI','人工抽样与成本区间记录，跨周期效果保持未知']}
options=[]
for f in fm['payload']['functions']:
 ident=f['id'];variants=['客户现有实现未知，待现场记录']+principles[ident]
 for i,text in enumerate(variants):
  options.append({'id':ident+'O'+str(i),'function_id':ident,'principle':text,'conditions':['Host提出的研究选项；尺寸、材料、工况、接口和安全边界待确认，不能直接制造或试割'],'evidence_refs':[]})
ids=[f['id'] for f in fm['payload']['functions']]
a=copy.deepcopy(old['R17']);a.update(artifact_id='HOST-ML007-ConceptSet',revision='host-r1',task_id=state['task']['task_id'],task_revision=state['task']['revision'])
a['conditions']=[];a['evidence_refs']=[];a['scope']='Host Agent依据本轮R14功能模型续写；原R17后台模型超时，以下不是后台模型生成或工程可行性结论。'
a['payload']={'function_ids':ids,'options':options,'combinations':[{'id':'C'+str(i),'option_ids':[f+'O'+str(i) for f in ids],'status':'unknown','reason':reason} for i,reason in enumerate(['客户现状占位，未测量，不作已证实对照','机械参考、双物流和可维护模块路线，所有接口相容性未知','测量辅助的受限闭环路线，感知和退出能力未证实','人工辅助的可撤销改造路线，工时、安全和适用树株范围待核'])], 'unknowns':['所有组合尚未完成机械、能量与控制接口验证；整套同列组合只是讨论样本，不证明所有子选项能够共存','C1/C2模块可局部用于C3，路线不互斥，必须先统一改造范围和系统边界再公平比较','F14是支持性评价功能，同样显式分配，不能因不直接切削而省略','案例当前仅有首块摘录，不能作为具体限深或分离机制成立的证据；相关假设需补证','原模型调用超时被保留，后续内容由Host提出；未生成唯一推荐']}
a['payload']['compatibility']=[{'option_ids':[left+'O'+str(i),right+'O'+str(i)],'status':'unknown','reason':reason,'evidence_refs':[]} for i in [1,2,3] for left,right,reason in [('F03','F05','表面参照不能证明真实限深，须核实量测链'),('F05','F10','限深与退出必须协调，恒力不能证明组织安全'),('F07','F09','分隔可能积胶或失胶，必须同时评估洁净与收集损失'),('F10','F12','失电停止与退出能量可能冲突，需要安全审核'),('F11','F05','清洗换刀后基准可能变化，需复装校准')]]
a['revision']='host-r2-interface-complete'
artifacts={'R17':a}
b=copy.deepcopy(old['R36']);b.update(artifact_id='HOST-ML007-ComparisonRecord',revision='host-r1',task_id=state['task']['task_id'],task_revision=state['task']['revision']);b['conditions']=[];b['evidence_refs']=[]
b['scope']='Host依据本轮需求和候选做未知项审查；不是优选或已测性能比较。'
b['payload']['requirements_revision']=brief['revision']
for c in b['payload']['criteria']:
 r=next(r for r in brief['payload']['requirements'] if r['id'] in c['requirement_ids'])
 c['text']=r['text']+'；原验收设想：'+r['acceptance']
b['payload']['recommendations']=[]
artifacts['R36']=b
for rid in ['R44','R42']:
 a=copy.deepcopy(old[rid]);a.update(artifact_id='HOST-ML007-'+a['type'],revision='host-r1',task_id=state['task']['task_id'],task_revision=state['task']['revision'])
 a['conditions']=[];a['evidence_refs']=[]
 a['scope']='Host复用并适配ML-005作者研究安排到本轮需求基线；未执行任何试验，不是后台模型新生成。'
 if rid=='R42':a['payload']['requirements_revision']=brief['revision']
 artifacts[rid]=a
OUT.mkdir(parents=True,exist_ok=True)
(OUT/'host-continuation.json').write_text(json.dumps({'authorship':'Host_Agent_adaptation_not_backend_model_generation','reason':'R17_model_timeout_no_automatic_retry','source_reuse':'ML005 author research plans; new R17 maps actual ML007 F01-F14','artifacts':artifacts},ensure_ascii=False,indent=2))
print('Host continuation drafted; requires per-step review and real MCP check/submit')
