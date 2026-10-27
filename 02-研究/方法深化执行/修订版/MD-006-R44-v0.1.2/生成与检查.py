"""Three bounded teaching adapters, not native MCP or semantic/physical validators."""
from pathlib import Path
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parent
DIRS={'R36':D.parent/'MD-005-R36-v0.1.1','R44':D,'R42':D.parent/'MD-007-R42-v0.1.2'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(rid,name,value):
 p=DIRS[rid]/'教学包'/name
 if rid=='R36':
  assert json.loads(p.read_text())==value;return p
 p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(value,ensure_ascii=False,indent=2));return p
def read(p):return json.loads(p.read_text())
UPSTREAM=json.loads((D/'上游冻结绑定.json').read_text())
problem=ROOT/UPSTREAM['problem']['path']
concepts=ROOT/UPSTREAM['concepts']['path']
assert digest(problem)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
assert digest(concepts)==UPSTREAM['concepts']['sha256']
r48path=ROOT/UPSTREAM['requirement_candidates']['path']
assert digest(r48path)==UPSTREAM['requirement_candidates']['sha256']
r48=read(r48path);assert r48['baseline_status']=='not_baselined'
p0,c0=read(problem),read(concepts);needs=[x['id']for x in p0['needs']];cids=[x['candidate_id']for x in c0['candidates']]
assert len(cids)==8 and all(x['state']=='conditional_research'for x in c0['candidates'])
BIND={'problem_id':p0['problem_id'],'problem_version':p0['version'],'source_problem_path':str(problem.relative_to(ROOT)),'source_problem_sha256':digest(problem),'source_concept_path':str(concepts.relative_to(ROOT)),'source_concept_sha256':digest(concepts),'customer_approved':False,'engineering_validated':False}
criteria=[{'id':'CR-BOUNDARY','need':'N-T01','label':'作用边界表达与支持证据','direction':'qualitative','unit':None,'target':None},{'id':'CR-RECOVERY','need':'N-T02','label':'异常停止退出与恢复依据','direction':'qualitative','unit':None,'target':None},{'id':'CR-STATE','need':'N-T03','label':'状态与数据时效可理解性','direction':'qualitative','unit':None,'target':None},{'id':'CR-SERVICE','need':'N-T04','label':'清理维护转场对完整作业影响','direction':'qualitative','unit':None,'target':None}]
CRITERIA_EXPECT=copy.deepcopy(criteria)
SOURCE_STATES={x['candidate_id']:x['state']for x in c0['candidates']}
SOURCE_HARD={x['candidate_id']:copy.deepcopy(x['hard_constraint_results'])for x in c0['candidates']}
main={'schema':'R36-teaching-input-1','binding':BIND,'datum':'TAP-C01','candidate_ids':cids,'criteria':criteria,'candidate_states':{x['candidate_id']:x['state']for x in c0['candidates']},'values':{cid:{x['id']:{'value':None,'evidence':[],'basis':'not_measured_or_modelled'}for x in criteria}for cid in cids},'hard_status':{x['candidate_id']:x['hard_constraint_results']for x in c0['candidates']},'recommendation':None,'new_customer_targets':{x:None for x in needs}}
def check_binding(i):
 b=i['binding']
 if b!=BIND:raise ValueError('shared_context_binding_or_status_changed')
def check_r36(i):
 check_binding(i)
 if set(i['candidate_ids'])!=set(cids):raise ValueError('upstream_candidate_omitted')
 if i['candidate_states']!=SOURCE_STATES:raise ValueError('source_candidate_states_changed_or_incomplete')
 if i['hard_status']!=SOURCE_HARD:raise ValueError('source_hard_status_changed_or_incomplete')
 if i['criteria']!=CRITERIA_EXPECT:raise ValueError('criterion_fields_or_mapping_changed')
 if i['binding']['source_concept_sha256']!=digest(concepts):raise ValueError('upstream_binding_mismatch')
 if i['datum']not in i['candidate_ids']:raise ValueError('datum_missing')
 if len(i['candidate_ids'])!=len(set(i['candidate_ids'])):raise ValueError('duplicate_candidate')
 expected={x['id']for x in i['criteria']}
 if expected!={x['id']for x in criteria}:raise ValueError('criterion_coverage_mismatch')
 if any(i['new_customer_targets'][x]is not None for x in needs):raise ValueError('customer_target_invented')
 if any(set(i['values'][cid])!=expected for cid in i['candidate_ids']):raise ValueError('missing_comparison_cell')
 if i['recommendation']is not None:raise ValueError('no_engineering_recommendation_supported')
 cells=[]
 for cid in i['candidate_ids']:
  for cr in i['criteria']:
   v=i['values'][cid][cr['id']]
   if v['value']is not None or v['evidence']:raise ValueError('fixed_fixture_unsupported_performance')
   cells.append({'candidate_id':cid,'criterion_id':cr['id'],'relation':'unknown','reason':'no_compatible_evidence_for_comparison','does_not_equal':'same_or_zero'})
 failed=[cid for cid,h in i['hard_status'].items()if any(v=='fail'for v in h.values())]
 return {'binding':i['binding'],'datum':i['datum'],'cells':cells,'unknown_cells':len(cells),'ranking':None,'recommendation':None,'status':'cannot_rank_missing_material','excluded_from_implementation_due_to_explicit_hard_fail':failed,'engineering_candidates':[],'next_research':[{'need':x['need'],'criterion':x['id'],'candidate_ids':i['candidate_ids'],'action':'clarify_criterion_or_collect_compatible_evidence'}for x in i['criteria']],'scope':'structure_and_fixed_unknown_preservation_only_not_physical_comparison'}
r36=check_r36(main);put('R36','01-绑定输入.json',main);put('R36','02-主链逐格比较与补证队列.json',r36)
# This small unrelated constructed fixture shows actual comparative arithmetic.
mini={'problem_id':'DATUM-TEACH-001','provenance':'synthetic_counts_not_tapping_robot_data','criteria':{'adjust_operations':{'direction':'lower','unit':'count'},'modules':{'direction':'lower','unit':'count'},'cleaning':{'direction':'qualitative','unit':None}},'values':{'A':{'adjust_operations':3,'modules':2,'cleaning':None},'B':{'adjust_operations':2,'modules':4,'cleaning':None},'C':{'adjust_operations':1,'modules':3,'cleaning':None}}}
def comparemini(datum):
 out=[]
 for cid,vs in mini['values'].items():
  rr={k:'unknown'if v is None or mini['values'][datum][k]is None else('same'if v==mini['values'][datum][k]else'better'if v<mini['values'][datum][k]else'worse')for k,v in vs.items()}
  net=sum({'better':1,'same':0,'worse':-1}.get(v,0)for v in rr.values());out.append({'candidate':cid,'relations':rr,'descriptive_net_known_only':net,'unknown_count':sum(v=='unknown'for v in rr.values()),'engineering_recommendation':None})
 return {'datum':datum,'rows':out,'interpretation':'net_is_not_utility_or_optimality; unknown counted separately; no recommendation'}
mini['runs']=[comparemini(x)for x in ['A','B','C']]
assert mini['runs'][0]['rows'][2]['descriptive_net_known_only']==0
assert mini['runs'][1]['rows'][2]['descriptive_net_known_only']==2
assert mini['runs'][2]['rows'][1]['descriptive_net_known_only']==-2
put('R36','03-独立构造datum复算.json',mini)
# R44: plans only, with two distinct questions and explicit uncovered needs.
r44input={'schema':'R44-teaching-input-1','binding':BIND,'source_r36':{'path':'../MD-005-R36-v0.1.1/教学包/02-主链逐格比较与补证队列.json','sha256':digest(DIRS['R36']/'教学包/02-主链逐格比较与补证队列.json')},'hypotheses':[{'id':'H-R44-01','need':'N-T01','question':'表面参考是否足以支持待研究的作用边界表达？','alternative':'表面几何与隐藏组织边界不相同，表面代理可能无法支持目标声明','prototype_id':'P-SURROGATE','learning_scope':'局部代理材料与参考关系；不能确认真实树体内部边界','observation_plan':['记录已知代理几何与参考输出及其对应关系','检查偏差是否随表面状态改变；实际材料、测量方法待定'],'measurement_unit_proposal':'待依据具体变量确认；不改源需求unit','threshold':None},{'id':'H-R44-03','need':'N-T03','question':'状态样例中的时效标记是否帮助区分陈旧与当前信息？','alternative':'使用者可能忽视标记或错误理解时效','prototype_id':'P-PAPER','learning_scope':'状态理解研究；不能确认控制实时性或机械安全','observation_plan':['拟让目标角色判断当前与陈旧状态并说明依据','记录误解及无法判断；资格、同意与样本待定'],'measurement_unit_proposal':'任务表现与解释编码待确认','threshold':None}],'prototypes':[{'id':'P-SURROGATE','status':'planned_not_built','capabilities':['proxy_geometry_relation'],'cannot_answer':['true_tree_tissue_accuracy','system_safety']},{'id':'P-PAPER','status':'planned_not_built','capabilities':['state_comprehension'],'cannot_answer':['physical_cutting','control_latency']}],'capability_needed':{'H-R44-01':'proxy_geometry_relation','H-R44-03':'state_comprehension'},'coverage':{'planned_learning_needs':['N-T01','N-T03'],'uncovered':['N-T02','N-T04']},'execution_status':'not_executed','participant_count':None,'observations':[],'findings':[],'customer_approved':False}
REQUIRED_CAPABILITY=copy.deepcopy(r44input['capability_needed'])
PROTOTYPES_EXPECT=copy.deepcopy(r44input['prototypes'])
HYP_EXPECT={h['id']:{k:copy.deepcopy(v)for k,v in h.items()if k!='prototype_id'}for h in r44input['hypotheses']}
def check_r44(i):
 check_binding(i)
 if i['capability_needed']!=REQUIRED_CAPABILITY:raise ValueError('caller_cannot_redefine_required_capability')
 if i['prototypes']!=PROTOTYPES_EXPECT:raise ValueError('prototype_capability_or_scope_redefined')
 if any({k:v for k,v in h.items()if k!='prototype_id'}!=HYP_EXPECT.get(h['id'])for h in i['hypotheses']):raise ValueError('hypothesis_mapping_changed')
 if set(i['coverage']['planned_learning_needs'])!={'N-T01','N-T03'}or set(i['coverage']['uncovered'])!={'N-T02','N-T04'}:raise ValueError('learning_coverage_changed')
 ids=[h['id']for h in i['hypotheses']]
 if len(ids)!=len(set(ids)):raise ValueError('duplicate_hypothesis_id')
 if set(ids)!={'H-R44-01','H-R44-03'}:raise ValueError('missing_or_unsupported_hypothesis')
 if i['source_r36']['path']!='../MD-005-R36-v0.1.1/教学包/02-主链逐格比较与补证队列.json':raise ValueError('source_r36_path_mismatch')
 if i['source_r36']['sha256']!=digest(DIRS['R36']/'教学包/02-主链逐格比较与补证队列.json'):raise ValueError('source_r36_changed')
 if i['execution_status']!='not_executed'or i['observations']or i['findings']or i['participant_count']is not None:raise ValueError('fabricated_execution_or_observation')
 if i['customer_approved']:raise ValueError('customer_approval_invented')
 if any(h['threshold']is not None for h in i['hypotheses']):raise ValueError('threshold_invented')
 if any(h['need']not in needs for h in i['hypotheses']):raise ValueError('dangling_need')
 prot={p['id']:p for p in i['prototypes']}
 if any(p['status']!='planned_not_built'for p in prot.values()):raise ValueError('prototype_build_invented')
 cap=[]
 for h in i['hypotheses']:
  if h['prototype_id']not in prot:raise ValueError('prototype_reference_missing')
  ok=i['capability_needed'][h['id']]in prot[h['prototype_id']]['capabilities']
  cap.append({'hypothesis':h['id'],'prototype':h['prototype_id'],'capability_match':ok,'state':'planned_only'if ok else'cannot_answer_return_to_prototype_design'})
 return {'binding':i['binding'],'hypotheses':i['hypotheses'],'capability_review':cap,'coverage':i['coverage'],'readiness':'not_ready','readiness_gaps':['材料与边界口径','测量方法与阈值依据','原型及资源','目标角色与研究同意','取样与干扰控制'],'planned_interpretation_states':['supports_limited_hypothesis','contradicts_hypothesis','inconclusive','test_invalid'],'observations':[],'findings':[],'next_decision':None,'execution_status':'not_executed','scope':'plan_and_fixed_capability_check_only_not_empirical_test'}
r44=check_r44(r44input);put('R44','01-假设与原型输入.json',r44input);put('R44','02-能力与解释分支计划.json',r44);put('R44','03-空观察表.json',{'rows':[],'required_fields_when_executed':['task_id','hypothesis_id','prototype_version','participant_or_operator_role','context','raw_record_path','raw_record_sha256','observation','interpretation_separate','anomaly'],'not_actual_data':True})
# R42: source items are hypotheses, not approved requirements.
r42input={'schema':'R42-teaching-input-1','binding':BIND,'source_r44':{'path':'../MD-006-R44-v0.1.2/教学包/02-能力与解释分支计划.json','sha256':digest(DIRS['R44']/'教学包/02-能力与解释分支计划.json')},'source_requirement_candidates':{'path':str(r48path.relative_to(ROOT)),'sha256':digest(r48path)},'configuration_id':'CFG-TAP-RESEARCH-0.1','items':[{'source_need':n,'source_requirement_candidate':'RQ-T'+n[-2:],'identity':'research_hypothesis_not_baselined_requirement','approved_target':None,'unit':None}for n in needs],'activities':[{'id':'V-P01','source_need':'N-T01','type':'proposed_analysis_or_test','objective':'研究如何形成可检验的边界要求','configuration_id':'CFG-TAP-RESEARCH-0.1','threshold':None,'resources':'unknown','result':None},{'id':'VAL-P03','source_need':'N-T03','type':'proposed_use_context_research','objective':'形成目标操作者状态理解的确认问题','configuration_id':'CFG-TAP-RESEARCH-0.1','threshold':None,'resources':'unknown','result':None}],'coverage':{'planned':['N-T01','N-T03'],'uncovered':['N-T02','N-T04']},'ready':False,'results':[],'engineering_pass':False}
NEED_REQUIREMENT_EXPECT={x['need_id']:x['id']for x in r48['candidates']}
def check_r42(i):
 check_binding(i)
 if len(i['items'])!=len({x['source_need']for x in i['items']}):raise ValueError('duplicate_source_item_id')
 if any(NEED_REQUIREMENT_EXPECT.get(x['source_need'])!=x['source_requirement_candidate']for x in i['items']):raise ValueError('need_requirement_pairing_changed')
 if i['source_requirement_candidates']['sha256']!=digest(r48path):raise ValueError('source_requirement_candidates_changed')
 if {x['source_requirement_candidate']for x in i['items']}!={x['id']for x in r48['candidates']}:raise ValueError('requirement_candidate_omitted')
 if i['source_r44']['sha256']!=digest(DIRS['R44']/'教学包/02-能力与解释分支计划.json'):raise ValueError('source_r44_changed')
 if {x['source_need']for x in i['items']}!=set(needs):raise ValueError('source_item_omitted')
 if any(len(i['coverage'][k])!=len(set(i['coverage'][k]))for k in ['planned','uncovered']):raise ValueError('duplicate_coverage_id')
 planned,unc=set(i['coverage']['planned']),set(i['coverage']['uncovered'])
 if planned&unc or planned|unc!=set(needs):raise ValueError('coverage_partition_invalid')
 if i['ready']or i['results']or i['engineering_pass']:raise ValueError('readiness_or_pass_invented')
 if any(x['approved_target']is not None or x['unit']is not None or x['identity']!='research_hypothesis_not_baselined_requirement'for x in i['items']):raise ValueError('requirement_baseline_invented')
 if any(x['source_need']not in planned for x in i['activities']):raise ValueError('activity_coverage_mismatch')
 if {x['source_need']for x in i['activities']}!=planned:raise ValueError('planned_activity_omitted')
 if any(x['threshold']is not None or x['result']is not None for x in i['activities']):raise ValueError('target_or_result_invented')
 if any(x['configuration_id']!=i['configuration_id']for x in i['activities']):raise ValueError('configuration_mismatch')
 return {'binding':i['binding'],'configuration_id':i['configuration_id'],'source_item_count':len(i['items']),'approved_requirement_count':0,'verification_conformance_claims':[],'validation_effectiveness_claims':[],'candidate_activities':i['activities'],'coverage':i['coverage'],'ready':False,'results':[],'engineering_pass':False,'next_actions':['确认需求身份与口径','确定配置、测量和资源','补异常恢复与完整作业场景','实际执行后再生成原始证据和偏差报告'],'change_rule':'source requirement/configuration/intended_use changes require impact review; old evidence not transferred automatically','scope':'coverage_and_fixed_state_check_not_requirements_compliance_or_real_use_validation'}
r42=check_r42(r42input);put('R42','01-验证候选与覆盖输入.json',r42input);put('R42','02-未就绪计划与证据边界.json',r42);put('R42','03-证据与偏差空表.json',{'results':[],'anomalies':[],'fields_when_executed':['claim_id','config_id','environment','method','instrument_calibration','raw_evidence_sha256','observed_result','discrepancy_id','reviewed_conclusion_scope'],'engineering_pass':False})
# Execute five distinct classes per method; retain actual mutations and outputs.
checks=[]
def probe(rid,name,kind,fn,base,mutate,expected_error=None,assert_output=None):
 v=copy.deepcopy(base);mutate(v)
 try:
  out=fn(v)
  if expected_error:raise AssertionError('expected rejection '+expected_error)
  if assert_output:assert_output(out)
  observed='accepted_with_bounded_state'
 except ValueError as e:
  if str(e)!=expected_error:raise
  out={'error':str(e)};observed='rejected'
 record={'case':name,'class':kind,'status':'pass','expected_error':expected_error,'observed':observed,'output':out,'scope':'executed_python_fixed_fixture_check_not_real_prototype_or_engineering_test'}
 put(rid,'检查/'+name+'-输入.json',v);put(rid,'检查/'+name+'-输出.json',record);checks.append({'method':rid,**record})
probe('R36','normal-all-unknown','normal',check_r36,main,lambda x:None,assert_output=lambda o:(_ for _ in ()).throw(AssertionError())if o['unknown_cells']!=32 or o['ranking']is not None else None)
probe('R36','missing-datum','missing_material',check_r36,main,lambda x:x.update(datum='NOPE'),'datum_missing')
probe('R36','not-applicable-no-criteria','not_applicable',check_r36,main,lambda x:x.update(criteria=[]),'criterion_fields_or_mapping_changed')
probe('R36','boundary-hard-fail','boundary',check_r36,main,lambda x:x['hard_status']['TAP-C01'].update(power='fail'),'source_hard_status_changed_or_incomplete')
probe('R36','conflict-pretend-recommendation','conflict',check_r36,main,lambda x:x.update(recommendation='TAP-C01'),'no_engineering_recommendation_supported')
probe('R36','unknown-filled-zero','boundary',check_r36,main,lambda x:x['values']['TAP-C01']['CR-BOUNDARY'].update(value=0),'fixed_fixture_unsupported_performance')
probe('R44','normal-plan-only','normal',check_r44,r44input,lambda x:None)
probe('R44','missing-hypothesis','missing_material',check_r44,r44input,lambda x:x['hypotheses'].pop(),'missing_or_unsupported_hypothesis')
probe('R44','paper-cannot-answer-mechanism','not_applicable',check_r44,r44input,lambda x:x['hypotheses'][0].update(prototype_id='P-PAPER'),assert_output=lambda o:(_ for _ in ()).throw(AssertionError())if o['capability_review'][0]['state']!='cannot_answer_return_to_prototype_design'else None)
probe('R44','threshold-filled','boundary',check_r44,r44input,lambda x:x['hypotheses'][0].update(threshold=1),'hypothesis_mapping_changed')
probe('R44','fake-observation','conflict',check_r44,r44input,lambda x:x['observations'].append({'claim':'用户试用有效'}),'fabricated_execution_or_observation')
probe('R44','fake-participant-count','conflict',check_r44,r44input,lambda x:x.update(participant_count=5),'fabricated_execution_or_observation')
probe('R42','normal-not-ready','normal',check_r42,r42input,lambda x:None)
probe('R42','missing-uncovered','missing_material',check_r42,r42input,lambda x:x['coverage'].update(uncovered=[]),'coverage_partition_invalid')
probe('R42','wrong-configuration','not_applicable',check_r42,r42input,lambda x:x['activities'][0].update(configuration_id='CFG-OLD'),'configuration_mismatch')
probe('R42','hypothesis-as-approved-requirement','boundary',check_r42,r42input,lambda x:x['items'][0].update(approved_target=1),'requirement_baseline_invented')
probe('R42','fake-pass','conflict',check_r42,r42input,lambda x:x.update(engineering_pass=True),'readiness_or_pass_invented')
probe('R42','source-item-omitted','missing_material',check_r42,r42input,lambda x:x['items'].pop(),'requirement_candidate_omitted')
probe('R36','false-engineering-binding','conflict',check_r36,main,lambda x:x['binding'].update(engineering_validated=True),'shared_context_binding_or_status_changed')
probe('R36','source-candidate-omitted','missing_material',check_r36,main,lambda x:x['candidate_ids'].pop(),'upstream_candidate_omitted')
probe('R44','false-engineering-binding','conflict',check_r44,r44input,lambda x:x['binding'].update(engineering_validated=True),'shared_context_binding_or_status_changed')
probe('R44','uncovered-needs-hidden','missing_material',check_r44,r44input,lambda x:x['coverage'].update(uncovered=[]),'learning_coverage_changed')
probe('R42','false-engineering-binding','conflict',check_r42,r42input,lambda x:x['binding'].update(engineering_validated=True),'shared_context_binding_or_status_changed')
probe('R42','old-source-version','boundary',check_r42,r42input,lambda x:x['source_r44'].update(sha256='0'*64),'source_r44_changed')
for field,value in [('need','N-T04'),('target',9),('unit','mm'),('direction','higher')]:
 probe('R36','criterion-'+field+'-drift','conflict',check_r36,main,lambda x,f=field,v=value:x['criteria'][0].update({f:v}),'criterion_fields_or_mapping_changed')
probe('R36','hard-status-erased','missing_material',check_r36,main,lambda x:x.update(hard_status={}),'source_hard_status_changed_or_incomplete')
probe('R36','candidate-states-erased','missing_material',check_r36,main,lambda x:x.update(candidate_states={}),'source_candidate_states_changed_or_incomplete')
def disguise_paper(x):
 x['capability_needed']['H-R44-01']='state_comprehension';x['hypotheses'][0]['prototype_id']='P-PAPER'
probe('R44','caller-redefines-capability-to-match-paper','conflict',check_r44,r44input,disguise_paper,'caller_cannot_redefine_required_capability')
def swap_requirements(x):
 x['items'][0]['source_requirement_candidate'],x['items'][1]['source_requirement_candidate']=x['items'][1]['source_requirement_candidate'],x['items'][0]['source_requirement_candidate']
probe('R42','same-sets-swapped-need-requirement-pairs','conflict',check_r42,r42input,swap_requirements,'need_requirement_pairing_changed')
probe('R44','duplicate-hypothesis','conflict',check_r44,r44input,lambda x:x['hypotheses'].append(copy.deepcopy(x['hypotheses'][0])),'duplicate_hypothesis_id')
probe('R44','wrong-source-path-right-sha','conflict',check_r44,r44input,lambda x:x['source_r36'].update(path='NO-SUCH-PATH'),'source_r36_path_mismatch')
probe('R42','duplicate-coverage','conflict',check_r42,r42input,lambda x:x['coverage']['planned'].append('N-T01'),'duplicate_coverage_id')
probe('R42','duplicate-source-item','conflict',check_r42,r42input,lambda x:x['items'].append(copy.deepcopy(x['items'][0])),'duplicate_source_item_id')
for rid in DIRS:
 own=[x for x in checks if x['method']==rid];put(rid,'04-实际检查汇总.json',{'method':rid,'executed_cases':len(own),'passed':len(own),'cases':own,'engineering_tests_executed':0,'new_participants':0,'qualification':'fixed_teaching_fixture_structure_only'})
print(json.dumps({'R36_cells':len(r36['cells']),'R36_unknown':r36['unknown_cells'],'R36_ranking':r36['ranking'],'R44_ready':r44['readiness'],'R42_ready':r42['ready'],'actual_fixed_fixture_checks':len(checks),'all_pass':True},ensure_ascii=False))
