# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,math
import numpy as np
O=Path(__file__).parent;V=O.parent;ROOT=V.parents[2];N=ROOT/'02-研究/ML-021-内容质量深化/needs';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(N/'manifest.json')=='5d7bbec6d3ea03294fe402a765b2218cd9077db43cee33f964a488131e3ea3ec'
m=json.loads((N/'manifest.json').read_text());assert all(sha(N/r['path'])==r['sha256']for r in m['files']);before={r['path']:sha(N/r['path'])for r in m['files']}
# Every prose body actually read in full; locations below preserve exact frozen text.
detail={
'R01':['分层承诺与回返，不把机构名当功能','二维通道冲突/释放间隙决定布局修订','0/400/0mm²与2/6mm明确局部选择','照抄机构后补功能；二维无交叠冒三维可用','VDI2221摘要与平台四层分工明确'],
'R02':['两个收敛对象与可重开边界','恢复负担分段改变挑战，协议例排除跨介质','40/60构造与四路线协议提供明确动作','确认老板想法式访谈；同结构小变化冒发散','Design Council迭代与GOV.UK研究范围分层'],
'R03':['模式按学习问题选择，能力与任务分开','样例缺时点导致修原型前提而非评词义失败','完整任务/记录/替代解释，纸面修订链可跟随','逼真动画冒控制证据；提示后成功冒自主理解','d.school2018选段，不复制卡组'],
'R04':['用途—功能—架构—接口双向一致性','对象ID缺失回接口；派生延迟随架构重评','分拣职责与A300/B100派生变更链','相机正确但对象关联错；换配置沿用旧证据','NASA设计/逻辑分解选段不冒ISO完整实施'],
'R05':['左右层级配对与接口语义/时基/权限','4mm符号异常回合同；超龄与错时钟返回','±2/−1mm、20/30ms、单写角色例','单元正常整体符号错；新鲜但错对象','VDI公开框架与NASA集成选段明确'],
'R06':['证据支持资源承诺，建议与授权分开','风险未知Hold实体活动并列复审动作','24构造人时请求与Hold/Recycle/Kill/Go条件','收益抵危险；技术足却组织资源不足','官方Gates依据与平台教学分开'],
'R07':['DMADV各阶段和量测代表性讲清','当前只到v2/v1判不满足及补身份，后半设计/确认未演示','12空格加单条属性偏差不足以走完本法实例','重复性好不等准确；熟练常温不代表现场','NIST新设计与量具选段准确，L>2条件复核相符'],
'R08':['事件/表示/解释/假设分型与命题强度','反例撤回必要命题，保留概率假设与补证','6便签归3事件、H1/H2/H3分判和研究修订','重复表示当多事件；只看顺利运行','GOV.UK观察/访问协议与平台命题推理分开'],
'R09':['具体选择/力量/进步而非属性清单','两构造选择故事转向采用/支援问题','A暂缓/B未试用的编码与job表述','属性填句式；领导支付冒操作者任务','CI2021 PDF9方法与非代表性已实际再核'],
'R10':['相对趋势领先与预期收益两资格','B匹配/C补证/D类比迁移/A-E排除本趋势','五候选逐项资格动作与推荐网络','无自研就排除；极端方案当普通用户可用','168页手册身份与PDF85/153范围明确'],
'R11':['成对反应的语义/方向和具体版本查表','混合A/O/M不编多数；R/Q/缺答追问','三对构造回答与Q/R处理可照做','满意I删紧停；正反问暗改多条件','2014表2而非1984原表，25格差异保留'],
'R12':['需要到响应/责任/证据，尺度与目标来源分离','版本字段选B；关系/偏好不足不反推阈值','一行展开和成对矩阵局部数值/敏感性','序数乘9/3/1精确化；权重当伤害容限','Mazur局部舍入不冒重建全部调查'],
'R13':['HTA目标/操作/计划/前提与工作系统','表征碰撞选B进研究，按错误机制回任务','四子任务信息/失败表、编码对比和观察协议','专家记忆补偿；正常负荷冒异常接管','HSE安全走查与工作负荷边界明确'],
'R14':['功能分配与物料/能量/信息流及语义接口','表面不等组织；文档接口缺身份需补版本链','六职责与正常/失效路径、文档局部修订','零件树冒功能；异常直接恢复动作','NASA分解/接口范围与构造模型分开'],
'R15':['HOW/WHY目的手段与WHEN支撑区别','程序回答改为功能；形状嵌合另开路线','摩擦链及反问/前提/替代图逻辑可重建','横放时序冒FAST；零件当唯一基本功能','VA Canada范围限定经典局部视图'],
'R16':['证据能力、竞争解释、区分性取证与复查','ER5异条件不能排除H1；版本偏差先限传播','5条构造证据逐项能力/假设及文档行动','归责操作者便停；空载不偏移冒加载反证','HSE/HSG245选段与平台构造区分'],
'R17':['维度/选项/配对/整体判断不同层次','协议排2留2；总65W违50W回整体约束','8组合未知与独立有充分协议例并存','偏好当不可能；配对过冒整体过','Ritchey GMA/CCA范围不冒全部社会建模'],
'R18':['条件化自然机制到工程差异与区分试验','排外观复制，选条件界面策略；必要作用损失回返','自然事实/抽象/差异/候选与试验步骤贯通','湿软垫移干金属；一次效果不查凝固维护','Biomimicry机构与Bohn/Federle原研究选段'],
'R48':['原话到候选/承诺、来源/状态/变更分离','2<5退布局/6≥5局部过；有依据TBR与无依据分开','5mm规则、200ms串行预算与基线变更','权重反推安全阈值；旧通过跨配置复用','NASA C.2–4实际源段与平台字段分开']}
markers={
'R01':['VDI2221','分层承诺','每层的继续','一次完整夹具','两个实质','VDI2221','可交接'],
'R02':['Design Council','第一钻改变','怎样决定','一份有充分','两种典型','Design Council','交接包含'],
'R03':['Stanford','用学习问题','测试之后','一次从标签','两个实质','Stanford','交接产物'],
'R04':['NASA','从用途','双向追溯','构造分拣','两个失败','NASA','可交接'],
'R05':['VDI','左侧先','集成不是','正负号错误','两个实质','VDI','交接产物'],
'R06':['Stage-Gate','资源承诺','复审怎样','一次完整','两个失败','Stage-Gate','交接包括'],
'R07':['NIST','五类工作','实际量测','从含混','两个失败','NIST','交接包括'],
'R08':['GOV.UK','命题强度','分析会议','从六条','两种失败','GOV.UK','可交接包'],
'R09':['Arnett','进步诉求','跨事件','两个故事','两个失败','Arnett','交接应'],
'R10':['Handbook','领先于什么','推荐网络','五候选','两个反例','Handbook','交接为'],
'R11':['Hwang','正反问','类别怎样','逐回答','两个失败','Hwang','可交接'],
'R12':['QFD Institute','需要和解法','资料足够','一行展开','两个失败','Mazur','交接包括'],
'R13':['HSE','目标、子任务','如何依据','完整构造','两个实质','HSE','交接给'],
'R14':['NASA','作用','接口','六个构造','两个失败','NASA','交接包括'],
'R15':['VA Canada','HOW','替代原理','完整摩擦','两个实质','VA Canada','交接产物'],
'R16':['HSE','区分解释','行动和有效','沿既有','两个失败','HSE','交接包括'],
'R17':['Ritchey','维度怎样','下一步','三维八','两个失败','Ritchey','交接给'],
'R18':['Biomimicry','有条件','把“再做试验”','完整策略','两个实质','Bohn','可交接'],
'R48':['NASA Appendix','愿望','基线、变更','完整例二','两个典型','NASA Appendix','交接产物']}
methods=[];dims=['身份与边界准确','机制讲透','判断可操作','完整示范','反例与迁移','依据可追溯','阅读与交接']
for rid,v in detail.items():
 p=N/'稿件'/(rid+'.md');lines=p.read_text().splitlines();loc=[]
 for needle in markers[rid]:loc.append(next((i+1 for i,l in enumerate(lines)if needle in l),1))
 reasons=[v[4],v[0],v[1],v[2],v[3],v[4],'产物、近邻差别与其他情境边界具体，读者可找到下一步交接']
 ratings=[{'dimension':d,'rating':'局部'if rid=='R07'and d in['判断可操作','完整示范']else'充分','evidence':{'path':str(p.relative_to(ROOT)),'line':ln},'reason':reason}for d,ln,reason in zip(dims,loc,reasons)]
 methods.append({'method_id':rid,'manuscript_sha256':sha(p),'dimensions':ratings,'content_disposition':'需修订'if rid=='R07'else'受限方法教学候选通过本次内容审','scope':'within explicitly named sources/platform adaptations, not original standard/full algorithm or field/expert approval'})
# Independent arithmetic spot-checks relevant to the body, not schema tests.
def overlap(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
areas=[overlap(a,[40,0,60,80])for a in[[0,20,30,60],[20,30,80,50],[-35,30,-5,50]]];assert areas==[0,400,0]
A=np.array([[1,1.8,1.25],[1/1.8,1,1/1.8],[.8,1.8,1]]);w=(A/A.sum(axis=0)).mean(axis=1);assert np.allclose(w,[.420459068,.217086721,.362454211])
result={'reviewed_manifest_sha256':sha(N/'manifest.json'),'reviewer':'validation_deepening independent content agent','date':'2026-10-28','methods':methods,'findings':[{'id':'C-R07-01','severity':'P2-content-completeness','blocking':True,'method':'R07','location':{'path':'稿件/R07.md','line':markers['R07'][3]},'problem':'示例到偏差识别/补记录为止，未展示分析→设计响应→新配置确认的完整DFSS闭环','revision':'保留属性型例即可，补明确构造的请求/产物记录、原因区分、改版选择和独立确认记录及范围；不要求伪实测/Cp'},{'id':'C-R48-01','severity':'P3-precision','blocking':False,'method':'R48','problem':'TBR也不是已批准正式目标的表述容易把未决值标记和批准状态混成互斥','revision':'改为TBR标记本身不赋予批准状态，估计待解决与要求批准状态分别管理'}],'independent_numeric_checks':{'R01_overlap_mm2':areas,'R12_weights':w.tolist(),'R48_budget_ms':500-120-80-100,'R17_max_whole_W':20+25+20},'actual_review_scope':'read all19 manuscripts, claim mapping; source spot-checks NIST2.4.2, CI2021PDF9, NASA-C, LeadUserPDF85 and existing Kano variant/Pugh-QFD numeric bounds; not all full originals','original_manifest_entries_unchanged':all(sha(N/p)==h for p,h in before.items())}
assert result['original_manifest_entries_unchanged'];(O/'逐稿七维内容审核.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('19 content reviews;18 limited candidates,1 content revision requested; source bytes unchanged')
