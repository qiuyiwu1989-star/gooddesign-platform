from pathlib import Path
import json,hashlib,itertools,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
f=ROOT/'02-研究/方法深化执行/MD-003-R14/教学包/01-功能与接口输入-v0.1.0.json';model=json.loads(f.read_text())
assert model['problem_id']=='TAP-TEACH-001'
orig=ROOT/'output/method-reader-review/upgrades/R17-v0.2.2';d=json.loads((orig/'case.input.json').read_text())
d['case_id']='TAP-TEACH-001-MORPH-0.1.0';d['scope']={'object':'构造割胶作业头的三个研究功能子问题','goal':'比较表面参考、相对约束和停止退出的组合；全部保留工程未知','hard_constraints':['只覆盖F-T02/F-T03/F-T06，其他功能沿R14共同包保留','表面参考不等生物组织边界','所有目标值未客户确认；不制造或批准设备'],'not_claimed':['客户真实需求','已验证割胶方案','最优结构','专业安全认证','全部功能已实现']}
ev='A-TAP-TEACH';d['evidence_registry']=[{'id':ev,'kind':'teaching_assumption','description':'本平台构造机制选项，不来自树种、客户或实测','locator':'scope/options; upstream binding in separate file'}]
sub=[('D-REF','F-T02','建立局部表面参考',['O-REF-M','O-REF-S']),('D-LIMIT','F-T03','约束相对切入作用',['O-LIM-G','O-LIM-C']),('D-STOP','F-T06','停止并退出/交接',['O-STOP-P','O-STOP-A'])]
d['requirements']=[{'id':fid,'statement':name,'kind':'functional','state':'teaching_assumption','mandatory':True,'evidence_refs':[ev]}for _,fid,name,_ in sub]
d['dimensions']=[{'id':did,'function':name,'requirement_refs':[fid],'option_ids':oids}for did,fid,name,oids in sub]
d['conditions']=[{'id':u['id'],'name':u['text'],'state':'unknown','value':None,'unit':None,'evidence_refs':[ev],'unknown_reason':'共享R48教学输入未给现场证据；不能自动补值'}for u in model['unknowns']]
opts=[('O-REF-M','D-REF','接触基准','通过接触关系获得局部参考','接触载荷/压陷未知'),('O-REF-S','D-REF','非接触表面测距','由表面返回信号估计参考','光学/介质/污染影响未知'),('O-LIM-G','D-LIMIT','几何相对限位','由相对几何约束限制位移','表面到组织边界映射未知'),('O-LIM-C','D-LIMIT','感测反馈约束','将状态估计用于相对运动约束','测量延迟/误差与生物限值未知'),('O-STOP-P','D-STOP','被动储能退出概念','探索由预置储能提供退出作用','方向/储能/卡阻能力未知'),('O-STOP-A','D-STOP','受控执行退出概念','探索执行器在抑制后退出并反馈','失能可用性/残能/控制可靠性未知')]
d['options']=[{'id':i,'dimension_id':dim,'label':name,'mechanism':mech,'provides':[name+'的研究原理'],'requires':[req],'interfaces':['R14相应接口需核查'],'evidence_refs':[ev]}for i,dim,name,mech,req in opts]
d['pair_judgments']=[]
for a,b in itertools.combinations(d['dimensions'],2):
 for x,y in itertools.product(a['option_ids'],b['option_ids']):
  d['pair_judgments'].append({'id':'PJ-'+x+'--'+y,'option_ids':[x,y],'state':'unknown','basis':'unresolved','reason':'命名可组合不证明接口、时序、载荷或失效行为兼容','evidence_refs':[ev],'condition_refs':['U-T01','U-T02','U-T04'],'verification_question':'核几何/时序/供能与组织作用边界，再判断此接口'})
d['whole_judgments']=[]
for n,ids in enumerate(itertools.product(*[x['option_ids']for x in d['dimensions']]),1):
 d['whole_judgments'].append({'id':f'WJ-TAP-{n:02d}','option_ids':list(ids),'state':'unknown','basis':'unresolved','reason':'只有机制假设；整体组织损伤、性能、异常恢复和资源未核','evidence_refs':[ev],'condition_refs':['U-T01','U-T02','U-T03','U-T04','U-T05'],'verification_question':'优先确认最危险的边界识别/限制/异常停止假设，而非合计性能分'})
d['selection_policy']={'decision':'comparison_only_not_unique_optimum','criteria':['仅按ID确定展示基线，不代表偏好或优越性','所有工程条件未决'],'selected_option_ids':[x['option_ids'][0]for x in d['dimensions']],'reason':'固定第一组合便于复查；全部候选均待研究，不建议工程采用'}
d['validation_plan']=[{'id':'VP-TAP-01','question':'表面参考能否为实际允许组织边界提供足够信息？','method':'先核目标树体/组织及测量原理，再设计受控非伤害研究；本轮未实施','conditions_to_fix':['树种组织','测量误差','客户/专业可接受边界','失效与保护'],'acceptance_basis':'等待实际场景、专业依据和客户确认，不生成阈值','status':'not_executed','condition_refs':['U-T01','U-T02','U-T04']}]
save(P/'教学包/01-形态矩阵输入-v0.1.0.json',d)
save(P/'教学包/00-上游绑定.json',{'problem_id':model['problem_id'],'source_R14':{'path':str(f.relative_to(ROOT)),'sha256':sha(f)},'R48_shared':model['upstream'],'assumptions':'all mechanism options are additional platform teaching assumptions, not new requirements','native_mcp_submitted':False})
# Execute existing read-only generic teaching evaluator; never invoke fixed native adapter.
python=ROOT/'.runtime/pipeline/bin/python';python=str(python)if python.exists()else sys.executable
r=subprocess.run([python,'-B',str(orig/'run_case.py'),str(P/'教学包/01-形态矩阵输入-v0.1.0.json')],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
out=json.loads(r.stdout);assert out['counts']=={'enumerated':8,'excluded':0,'conditional_research':8,'model_comparison_candidate':0}
save(P/'教学包/02-枚举实际输出.json',out)
concepts=[{'candidate_id':f'TAP-C{n:02d}','source_combination_id':x['id'],'option_ids':x['option_ids'],'state':x['state'],'name':' + '.join(next(o['label']for o in d['options']if o['id']==i)for i in x['option_ids']),'satisfied_requirements':[],'hard_constraint_results':{'approved_target_available':'unknown','internal_tissue_boundary':'unknown','power':'unknown','abnormal_stop_and_recovery':'unknown'},'comparison_only':True,'engineering_validated':False}for n,x in enumerate(out['combinations'],1)]
save(P/'教学包/03-交给R36的候选-v0.1.0.json',{'problem_id':model['problem_id'],'version':'0.1.0','source_input':{'file':'01-形态矩阵输入-v0.1.0.json','sha256':sha(P/'教学包/01-形态矩阵输入-v0.1.0.json')},'source_output':{'file':'02-枚举实际输出.json','sha256':sha(P/'教学包/02-枚举实际输出.json')},'source_R14':{'path':str(f.relative_to(ROOT)),'sha256':sha(f)},'scope':'three research functions, other functions remain in R14 common architecture; not full robot or full needs satisfaction','candidates':concepts,'handoff_rules':['unknown is not zero or same-as-datum','may decide cannot rank yet','no hard constraint can be offset by preferences','fixed display datum is not recommendation'],'customer_approved':False,'engineering_validated':False})
save(P/'教学包/04-实际执行记录.json',{'command':[python,'-B',str(orig/'run_case.py'),str(P/'教学包/01-形态矩阵输入-v0.1.0.json')],'exit_code':r.returncode,'input_sha256':sha(P/'教学包/01-形态矩阵输入-v0.1.0.json'),'output_sha256':sha(P/'教学包/02-枚举实际输出.json'),'evaluator_sha256':sha(orig/'run_case.py'),'schema_sha256':sha(orig/'input.schema.json'),'counts':out['counts'],'native_adapter_or_mcp_execution':False,'meaning':'recorded judgments enumerated; program did not discover physical compatibility'})
print('R17 handoff',sha(P/'教学包/03-交给R36的候选-v0.1.0.json'))
