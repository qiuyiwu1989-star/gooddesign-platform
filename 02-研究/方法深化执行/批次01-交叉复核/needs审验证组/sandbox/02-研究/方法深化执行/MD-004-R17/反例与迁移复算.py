from pathlib import Path
import copy,hashlib,itertools,json,subprocess,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OLD=ROOT/'output/method-reader-review/upgrades/R17-v0.2.2'
PYTHON=str(ROOT/'.runtime/pipeline/bin/python')if(ROOT/'.runtime/pipeline/bin/python').exists()else sys.executable
BASE=json.loads((P/'教学包/01-形态矩阵输入-v0.1.0.json').read_text());RESULTS=[]
def save(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(name,category,d,exit_code,expected_counts=None,err=None):
 inp=P/'教学包/检查输入'/(name+'.json');out=P/'教学包/检查输出'/(name+'.json');save(inp,d)
 r=subprocess.run([PYTHON,'-B',str(OLD/'run_case.py'),str(inp)],capture_output=True,text=True);v=json.loads(r.stdout);save(out,v)
 assert r.returncode==exit_code,(name,r.returncode,r.stdout,r.stderr)
 if expected_counts:assert v['counts']==expected_counts,(name,v['counts'])
 if err:assert err in v['error'],(name,v)
 RESULTS.append({'id':name,'category':category,'input':str(inp.relative_to(P)),'input_sha256':sha(inp),'output':str(out.relative_to(P)),'output_sha256':sha(out),'exit_code':r.returncode,'expected_counts':expected_counts,'expected_error_contains':err,'passed':True})
counts={'enumerated':8,'excluded':0,'conditional_research':8,'model_comparison_candidate':0}
run('normal-all-unknown','normal',BASE,0,counts)
d=copy.deepcopy(BASE);d['pair_judgments'].pop();run('missing-pair','missing_material',d,2,err='pair_matrix_incomplete')
d=copy.deepcopy(BASE);d['mode']='certified_production';run('not-production-mode','not_applicable',d,2,err='teaching_assumptions_not_engineering')
d=copy.deepcopy(BASE);d['whole_judgments']=[];run('pairwise-never-global','boundary',d,0,counts)
d=copy.deepcopy(BASE);d['pair_judgments'][0].update(state='incompatible',basis='logical',condition_refs=[],reason='只为测试构造的符号排除条件，不是设备实证');run('selected-conflict','conflict',d,2,err='selected_combination_is_excluded')
d=copy.deepcopy(BASE);d['conditions'][0].update(value=0,unit='mm');run('unknown-not-zero','boundary',d,2,err="0 is not of type 'null'")
d=copy.deepcopy(BASE);d['whole_judgments'][0]['id']=d['pair_judgments'][0]['id'];run('global-judgment-id-collision','conflict',d,2,err='duplicate_global_judgment_id')
# Independent information-only model. Format conversion explicitly excluded by protocol.
d=copy.deepcopy(BASE);ev='A-DOC';d['case_id']='DOC-TEACH-001-MORPH';d['scope']={'object':'教学记录与归档协议','goal':'比较相同介质内的交接','hard_constraints':['协议禁止隐含打印/扫描/格式转换'],'not_claimed':['现实中无法转换','可读性已验证','生产接口可用']};d['evidence_registry']=[{'id':ev,'kind':'teaching_assumption','description':'人为约定本练习不做格式转换','locator':'scope'}];d['requirements']=[{'id':i,'statement':s,'kind':'functional','state':'teaching_assumption','mandatory':True,'evidence_refs':[ev]}for i,s in [('FD1','形成记录'),('FD2','归档记录')]];d['dimensions']=[{'id':'DD1','function':'形成记录','requirement_refs':['FD1'],'option_ids':['PAPER','DIGITAL']},{'id':'DD2','function':'归档记录','requirement_refs':['FD2'],'option_ids':['PAPER-S','DIGITAL-S']}];d['options']=[{'id':i,'dimension_id':dim,'label':i,'mechanism':'协议声明的'+m+'处理','provides':[m],'requires':[m],'interfaces':[m],'evidence_refs':[ev]}for i,dim,m in [('PAPER','DD1','paper'),('DIGITAL','DD1','digital'),('PAPER-S','DD2','paper'),('DIGITAL-S','DD2','digital')]];d['conditions']=[{'id':'C-DOC','name':'实际可读性与保存能力','state':'unknown','value':None,'unit':None,'evidence_refs':[ev],'unknown_reason':'未研究真实任务与接口'}];d['pair_judgments']=[];d['whole_judgments']=[]
for i,(a,b) in enumerate(itertools.product(['PAPER','DIGITAL'],['PAPER-S','DIGITAL-S'])):
 match=a.split('-')[0]==b.split('-')[0];j={'id':'P-DOC'+str(i),'option_ids':[a,b],'state':'compatible_within_model'if match else'incompatible','basis':'logical','reason':'仅协议介质一致'if match else'本协议没有转换支路','evidence_refs':[ev],'condition_refs':[],'verification_question':'如加入转换应建立新协议版本'};d['pair_judgments'].append(j)
 if match:d['whole_judgments'].append({'id':'W-DOC'+str(i),'option_ids':[a,b],'state':'unknown','basis':'unresolved','reason':'介质一致不证明可读性及真实流程有效','evidence_refs':[ev],'condition_refs':['C-DOC'],'verification_question':'观察实际输入输出与读取任务'})
d['selection_policy']={'decision':'comparison_only_not_unique_optimum','criteria':['仅固定展示基线'],'selected_option_ids':['PAPER','PAPER-S'],'reason':'不声称更好'};d['validation_plan']=[{'id':'V-DOC','question':'记录能否实际读回？','method':'另做真实任务观察；未执行','conditions_to_fix':['任务与接口'],'acceptance_basis':'需实际任务定义','status':'not_executed','condition_refs':['C-DOC']}]
run('cross-context-document','transfer',d,0,{'enumerated':4,'excluded':2,'conditional_research':2,'model_comparison_candidate':0})
# Resource arithmetic is a separate artificial model, not an approved robot requirement.
powers={'O-REF-M':5,'O-REF-S':20,'O-LIM-G':0,'O-LIM-C':25,'O-STOP-P':0,'O-STOP-A':20};dims=[x['option_ids']for x in BASE['dimensions']];cap=50
pairs=[{'options':[a,b],'sum_W':powers[a]+powers[b],'within_artificial_budget':powers[a]+powers[b]<=cap}for da,db in itertools.combinations(dims,2)for a,b in itertools.product(da,db)]
whole=[{'options':list(ids),'sum_W':sum(powers[x]for x in ids),'within_artificial_budget':sum(powers[x]for x in ids)<=cap,'engineering_compatibility':'unknown'}for ids in itertools.product(*dims)]
assert len(pairs)==12 and all(p['within_artificial_budget']for p in pairs)
assert len(whole)==8 and sum(not x['within_artificial_budget']for x in whole)==1
save(P/'教学包/06-独立构造资源反例.json',{'scope':'artificial_arithmetic_demo_not_robot_data_or_customer_requirement','assumed_powers_W':powers,'assumed_limit_W':cap,'pair_checks':pairs,'whole_checks':whole,'finding':'all 12 pairs fit, one 3-option combination exceeds; resource pass never establishes physical fit','customer_approved':False,'engineering_validated':False})
save(P/'教学包/07-反例与迁移实际记录.json',{'scope':'actual read-only teaching evaluator runs and separate arithmetic; not field validation','evaluator_sha256':sha(OLD/'run_case.py'),'script_sha256':sha(Path(__file__)),'cases':RESULTS,'passed':len(RESULTS),'arithmetic':{'pair_checks':12,'whole_checks':8,'pair_all_fit':True,'whole_over_limit':1},'engineering_validated':False})
print('R17 actual cases',len(RESULTS),'and pair/global arithmetic PASS')
