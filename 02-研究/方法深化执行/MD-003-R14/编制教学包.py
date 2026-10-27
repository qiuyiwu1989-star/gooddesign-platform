from pathlib import Path
import json,hashlib,urllib.request,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
up=ROOT/'02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'
u=json.loads(up.read_text());assert sha(up)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
functions=[
('F-T01','定义允许作业区域',['N-T01','N-T03'],'区域边界及人工授权','区域可操作性与授权状态','边界/授权未知则不允许自动进入作用'),
('F-T02','建立局部表面参考',['N-T01','N-T03'],'观察/接触获得的状态','带坐标系、时间戳、有效标记的参考','表面参考不等于内部组织边界'),
('F-T03','约束相对切入作用',['N-T01','N-T03'],'参考及待确认的允许范围','允许/禁止作用及运动限制','真实组织边界和限值未知，不能判深度合格'),
('F-T04','产生相对作业运动',['N-T01'],'作用许可、供能和目标对象','作用状态、残余物及反力','不确定载荷、功率及危险后果'),
('F-T05','识别状态失效并抑制作用',['N-T02','N-T03'],'状态、测量时点和许可','抑制指令及需人工核查的信息','未定义新鲜度阈值，不能写已实现及时检测'),
('F-T06','停止作用并交接恢复',['N-T02','N-T04'],'抑制指令和残余能量状态','停止/待退出/待人工状态及恢复条件','停止不等于安全退出，未知残余能量需保留')]
fs=[dict(id=i,verb_object=n,parent_need_ids=r,inputs=[inp],outputs=[out],failure_and_return=fail,derivation='platform_derived_research_function_not_customer_confirmed',customer_approved=False)for i,n,r,inp,out,fail in functions]
interfaces=[
('IF-T01','F-T01','F-T02','signal','工作区域、授权及版本',None,'区域或授权未明则退回F-T01'),
('IF-T02','F-T02','F-T03','signal','局部表面参考、frame_id、t_meas、valid','mm and ms (representation only)','坐标系/时效不能解释则unknown并请求抑制'),
('IF-T03','F-T03','F-T04','signal','允许范围与作用许可','mm (no accepted target)','未批准限值不标自动作业合格'),
('IF-T04','F-T04','F-T05','signal','实际状态与时点','ms (no accepted latency)','陈旧或缺失状态转为未知'),
('IF-T05','F-T05','F-T03','signal','失效抑制反馈',None,'不得因为有反馈环就强制删除边'),
('IF-T06','F-T05','F-T06','signal','停止及交接请求',None,'请求停止不等实际已停'),
('IF-T07','F-T06','EXT-OP','signal','残余能量状态、恢复前置项',None,'状态未知不得自动恢复'),
('IF-T08','EXT-OP','F-T01','signal','人工核查与重新授权',None,'原始授权不可跨异常沿用'),
('IF-T09','EXT-TREE','F-T04','material','待作用树体局部',None,'树种与组织状态未知'),
('IF-T10','F-T04','EXT-RESIDUE','material','切除物/污染物',None,'清理收集及对生物组织影响未知'),
('IF-T11','EXT-POWER','F-T04','energy','作业供能','W (value unknown)','功率/负载未测'),
('IF-T12','F-T04','EXT-TREE','energy','接触反作用',None,'未核力/方向和组织损伤')]
ints=[dict(id=i,origin=a,destination=b,flow_type=t,payload=p,representation_units=unit,threshold=None,unknown_action=action,owner_agreement='not_obtained',physical_validation='not_executed')for i,a,b,t,p,unit,action in interfaces]
model={'schema':'R14-research-teaching-model-0.1.0','problem_id':u['problem_id'],'version':'0.1.0','upstream':{'path':str(up.relative_to(ROOT)),'sha256':sha(up),'version':u['version']},'mode':'constructed_teaching_not_customer_evidence','scope':'workhead and local control interface; not entire robot or validated biological-depth control','functions':fs,'external_entities':['EXT-OP','EXT-TREE','EXT-RESIDUE','EXT-POWER'],'interfaces':ints,'known_approved_targets':[],'unknowns':[dict(x,origin='R48_shared_context')for x in u['unknowns']],'scenarios':[
{'id':'SC-T01','kind':'normal_research_path','function_ids':['F-T01','F-T02','F-T03','F-T04','F-T05'],'interface_ids':['IF-T01','IF-T02','IF-T03','IF-T04','IF-T05'],'claim':'only a declared control path; no operation executed'},
{'id':'SC-T02','kind':'stale_feedback_or_loss','function_ids':['F-T05','F-T06','F-T01'],'interface_ids':['IF-T06','IF-T07','IF-T08'],'claim':'requires explicit human reauthorization; actual detect/stop time unknown'}],
'coverage':[{'need_id':n['id'],'function_ids':[f['id']for f in fs if n['id']in f['parent_need_ids']],'status':'research_allocation_not_satisfaction'}for n in u['needs']],
'limits':['structural checks do not prove semantic sufficiency','control feedback and material/energy interfaces are modeled separately','no conservation/stability/biological injury analysis','N-T04 only stop/maintenance handover represented; complete cleaning, maintenance and transfer remain outside boundary'],
'customer_approved':False,'engineering_validated':False}
save(P/'教学包/01-功能与接口输入-v0.1.0.json',model)
save(P/'教学包/02-分解选择与派生判断.json',{'problem_id':u['problem_id'],'decisions':[{'id':'DEC-F01','question':'为何不把功能命名为配置传感器？','basis':'that specifies a candidate component and does not state what must be accomplished','choice':'establish local surface reference; biological boundary remains unknown','kind':'platform_interpretation'}, {'id':'DEC-F02','question':'功能分解何时停止？','choice':'when alternatives and interfaces can be examined in this limited research problem, not at a prescribed depth','kind':'platform_interpretation'}, {'id':'DEC-F03','question':'异常后能自动恢复吗？','choice':'no evidence permits it; explicit human reauthorization is a teaching control choice, not a verified safety solution','kind':'teaching_assumption'}],'alternative_decomposition':{'alternative':'按感知/决策/执行分组','difference':'same responsibilities may be grouped differently; operational scenarios and traceability remain necessary','not_uniquely_correct':True}})
save(P/'教学包/03-交给R17的子问题.json',{'problem_id':u['problem_id'],'version':'0.1.0','source_model':{'path':'01-功能与接口输入-v0.1.0.json','sha256':sha(P/'教学包/01-功能与接口输入-v0.1.0.json')},'morphology_function_ids':['F-T02','F-T03','F-T06'],'common_function_ids':['F-T01','F-T04','F-T05'],'not_full_need_coverage_claim':True,'unknowns_preserved':[x['id']for x in u['unknowns']],'required_checks':['surface reference is not internal tissue boundary','stop versus retreat distinguished','power and actuator hypotheses not confirmed','do not score unknowns as ties'],'customer_approved':False,'engineering_validated':False})
# Recheck prior package manifests without writing their directories.
verified=[]
for rel in ['output/method-reader-review/upgrades/R14-v0.2.2-proposal','output/method-reader-review/upgrades/R17-v0.2.2']:
 b=ROOT/rel;m=json.loads((b/'manifest.json').read_text());items=m['files']
 if isinstance(items,dict):items=[{'path':k,'sha256':v}for k,v in items.items()]
 for x in items:assert sha(b/x['path'])==x['sha256'],str(b/x['path'])
 verified.append({'path':rel,'manifest_sha256':sha(b/'manifest.json'),'files_verified':len(items),'execution':'read_only_hash_recheck_not_rerun'})
save(P/'教学包/04-已有教学包只读复核.json',{'packages':verified,'independent_review_notes':['R14 existing 0.2.2 evaluator limited to declared chain shapes; do not call general feedback coverage checker','R17 native fixed adapter is not a generic input-accepting pipeline']})
print('R14 model created',sha(P/'教学包/01-功能与接口输入-v0.1.0.json'))
