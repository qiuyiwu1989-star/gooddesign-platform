"""Fixed second-batch teaching models. All new outputs only in MD014/015/016.
Representation collisions, declared logic and evidence bookkeeping are not human/engineering validation.
"""
from pathlib import Path
import copy,hashlib,json
ROOT=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
DIRS={'R13':P,'R15':P.parent/'MD-015-R15','R16':P.parent/'MD-016-R16'}
def save(rid,name,o):
 p=DIRS[rid]/'教学包'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,ensure_ascii=False,indent=2));return p
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shared=ROOT/'02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json'
expected='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
assert SHA(shared)==expected
CONTEXT={'problem_id':'TAP-TEACH-001','version':'0.1.0','sha256':expected,'path':str(shared.relative_to(ROOT)),'status':'constructed_research_not_customer_evidence'}
# The second batch consumes only the frozen shared context; first-batch method outputs remain pending corrections.
FIRST={'R36':'MD-005-R36/教学包/02-主链逐格比较与补证队列.json','R44':'MD-006-R44/教学包/02-能力与解释分支计划.json','R42':'MD-007-R42/教学包/02-未就绪计划与证据边界.json'}
first=[{'method':rid,'path':str((P.parent/rel).relative_to(ROOT)),'sha256':SHA(P.parent/rel),'use':'read_only_context_of_pending_fidelity_corrections_not_validated_dependency','status':'pending_root_coordinated_revision'}for rid,rel in FIRST.items()]
base13={'schema':'R13-fixed-lesson-1','binding':CONTEXT,'first_batch_status_reference':first,'provenance':'constructed_teaching_not_field_observation','population':{'target_population_known':False,'participants':None,'anthropometric_parameters':None,'experience_groups':['novice_hypothesis','experienced_hypothesis']},'tasks':[{'id':'HF-T01','phase':'normal_monitoring','action':'识别当前作业状态','information':['state','measurement_freshness'],'physical_demands':'unknown','cognitive_demands':'监视与状态解释，实际负荷未知'},{'id':'HF-T02','phase':'abnormal_takeover','action':'识别陈旧信息并请求抑制','information':['measurement_freshness','validity','stop_request_ack'],'physical_demands':'unknown','cognitive_demands':'从监视切换为异常判断，能力与时限未知'},{'id':'HF-T03','phase':'abnormal_takeover','action':'核对停止状态与恢复前提','information':['actual_stop','residual_energy','reauthorization'],'physical_demands':'unknown','cognitive_demands':'区分请求与实际状态，实际表现未知'},{'id':'HF-T04','phase':'maintenance','action':'清理与更换后交接','information':['isolation_status','maintenance_scope','reauthorization'],'physical_demands':'姿态、力、可达性均未知','cognitive_demands':'维护责任与交接，实际负荷未知'}],'states':[{'id':'S-CURRENT','semantic':'current_information'},{'id':'S-STALE','semantic':'stale_information'}],'representations':{'A':{'S-CURRENT':'绿灯','S-STALE':'绿灯'},'B':{'S-CURRENT':'绿灯；当前记录','S-STALE':'绿灯；记录陈旧，状态待核'}} ,'records':[],'conclusion':'not_empirically_evaluated','engineering_validated':False}
TASK_EXPECT={x['id']:(x['phase'],x['action'],tuple(x['information']))for x in base13['tasks']}
def check13(d):
 if d['binding']!=CONTEXT:raise ValueError('context_binding_changed')
 if d['provenance']!='constructed_teaching_not_field_observation':raise ValueError('provenance_changed')
 if d['population']!=base13['population']:raise ValueError('unsupported_population_claim')
 got={x['id']:(x['phase'],x['action'],tuple(x['information']))for x in d['tasks']}
 if got!=TASK_EXPECT or d['tasks']!=base13['tasks'] or len(d['tasks'])!=len(TASK_EXPECT):raise ValueError('task_or_information_mapping_changed')
 if d['states']!=base13['states']:raise ValueError('fixed_state_semantics_changed')
 if any(set(x)!= {'S-CURRENT','S-STALE'}for x in d['representations'].values()):raise ValueError('state_representation_missing')
 if d['records']or d['conclusion']!='not_empirically_evaluated'or d['engineering_validated']:raise ValueError('fabricated_user_or_engineering_result')
 comparisons=[]
 for variant,r in d['representations'].items():
  collision=len(set(r.values()))<len(r);comparisons.append({'variant':variant,'representation_collision':collision,'can_distinguish_declared_states_by_encoding':not collision,'human_understanding':'unknown','workload':'unknown','reaction_time':None})
 return {'method':'R13','state':'research_design_only','tasks':d['tasks'],'representation_analysis':comparisons,'measured_user_outcomes':[],'target_population_known':False,'research_questions':['目标角色能否理解时效标记','异常时能否区分请求与实际停止','维护姿态/力/可达性与职责是什么'],'not_claimed':['B更易用','新手反应更快','设备更安全'],'pending':['现场人群与任务记录','实际负荷与姿态数据','角色资格及参与同意','专业/用户复核']}
out13=check13(base13);save('R13','01-构造任务与信息输入.json',base13);save('R13','02-表征区分实际分析.json',out13)
# R15: a simplified classical HOW/WHY teaching view for one assumed friction mechanism.
base15={'schema':'R15-fixed-lesson-1','problem_id':'CLAMP-FAST-TEACH-001','version':'0.1.0','provenance':'platform_constructed_selected_friction_principle','diagram_type':'simplified_classical_how_why_teaching_view_not_full_technical_or_customer_FAST','how_direction':'left_to_right','why_direction':'right_to_left','not_clock_sequence':True,'nodes':[{'id':'H0','function':'稳定工件状态','scope':'outside_higher'},{'id':'B1','function':'约束切向滑动','scope':'inside_basic'},{'id':'S1','function':'产生接触摩擦','scope':'inside_secondary'},{'id':'L0','function':'施加法向作用','scope':'outside_lower'},{'id':'SUP1','function':'保持接触条件','scope':'inside_support'}],'edges':[{'id':'E01','purpose':'H0','means':'B1','kind':'means_purpose','how':'怎样稳定工件状态？通过约束切向滑动（本视图的一条局部路径）。','why':'为什么约束切向滑动？用于稳定工件状态。'},{'id':'E02','purpose':'B1','means':'S1','kind':'means_purpose','how':'怎样约束切向滑动？研究接触摩擦作用。','why':'为什么产生接触摩擦？用于约束切向滑动。'},{'id':'E03','purpose':'S1','means':'L0','kind':'means_purpose','how':'怎样产生接触摩擦？在本假设接触原理下施加法向作用。','why':'为什么施加法向作用？为研究接触摩擦提供条件。'}],'support':[{'function_id':'SUP1','supports':['B1','S1'],'relation':'enabling_condition_not_timeline','why_needed':'接触状态影响此原理是否能形成所研究作用，不是可随便删掉的外观特征'}],'unknowns':[{'id':'UF1','topic':'摩擦与材料条件','value':None},{'id':'UF2','topic':'允许接触载荷与结构','value':None},{'id':'UF3','topic':'真实约束效果及损伤','value':None}],'engineering_validated':False}
NODES={x['id']:(x['function'],x['scope'])for x in base15['nodes']};EDGES={x['id']:(x['purpose'],x['means'],x['kind'],x['how'],x['why'])for x in base15['edges']}
def check15(d):
 if (d['problem_id'],d['version'],d['provenance'],d['diagram_type'])!=(base15['problem_id'],base15['version'],base15['provenance'],base15['diagram_type']):raise ValueError('fixed_FAST_scope_or_type_changed')
 if d['how_direction']!='left_to_right'or d['why_direction']!='right_to_left'or not d['not_clock_sequence']:raise ValueError('logic_direction_or_temporal_confusion')
 if {x['id']:(x['function'],x['scope'])for x in d['nodes']}!=NODES or len(d['nodes'])!=len(NODES):raise ValueError('node_identity_or_scope_changed')
 for e in d['edges']:
  if e['purpose']not in NODES or e['means']not in NODES:raise ValueError('dangling_FAST_edge')
 if {x['id']:(x['purpose'],x['means'],x['kind'],x['how'],x['why'])for x in d['edges']}!=EDGES or len(d['edges'])!=len(EDGES):raise ValueError('declared_means_purpose_or_question_changed')
 if d['support']!=base15['support']:raise ValueError('support_function_lost_or_changed')
 if d['unknowns']!=base15['unknowns']or d['engineering_validated']:raise ValueError('unknown_or_validation_upgraded')
 return {'method':'R15','state':'declared_logic_review_record_only','diagram_type':d['diagram_type'],'scope_boundary':['H0','L0'],'HOW_path':['H0','B1','S1','L0'],'WHY_path':['L0','S1','B1','H0'],'edge_reviews':[{'id':x['id'],'how':x['how'],'why':x['why'],'reviewed_as':'one_assumed_means_purpose_path_not_proven_sufficient'}for x in d['edges']],'support':d['support'],'alternative_not_on_selected_path':{'mechanism':'形状嵌合','reason':'另一路原理应另画与核查，不被本摩擦视图逻辑排除'},'unknowns':d['unknowns'],'causal_or_engineering_sufficiency':'not_checked'}
out15=check15(base15);save('R15','01-构造FAST图与问答输入.json',base15);save('R15','02-逐边问答与范围输出.json',out15)
# R16: an artificial investigation with competing explanations, not a real incident.
base16={'schema':'R16-fixed-lesson-1','event_id':'RCA-TEACH-001','version':'0.1.0','provenance':'constructed_incident_not_customer_accident','event':'教学中工件在作业时出现一次相对偏移；原因未确认','evidence':[{'id':'ER1','kind':'constructed_operator_statement','content':'当时认为已经夹紧','limit':'事后表达，不等于当时状态或实际夹持力'},{'id':'ER2','kind':'constructed_control_log','content':'夹紧请求已发送','limit':'不是实际夹持完成或接触力记录'},{'id':'ER3','kind':'constructed_post_event_photo','content':'事后看见相对滑移痕迹','limit':'支持发生过相对运动，不唯一支持某个原因'},{'id':'ER4','kind':'constructed_interface_spec','content':'绿灯仅表示请求已发出','limit':'显示语义不等于已观察到使用者错误解释'}],'timeline':[{'index':1,'event':'发出夹紧请求','evidence':['ER2']},{'index':2,'event':'参与角色认为已夹紧','evidence':['ER1']},{'index':3,'event':'教学偏移事件','evidence':['ER3']}],'hypotheses':[{'id':'HRCA1','claim':'实际保持作用不足','support':['ER3'],'counterevidence':[],'unknowns':['实际接触状态和力记录','材料与载荷'],'status':'unconfirmed'},{'id':'HRCA2','claim':'请求指示可能被解释为实际夹紧','support':['ER1','ER2','ER4'],'counterevidence':[],'unknowns':['当时决策过程与其他信息','是否直接影响本次动作'],'status':'unconfirmed'},{'id':'HRCA3','claim':'对象状态变化可能影响保持','support':[],'counterevidence':[],'unknowns':['对象几何/材料变化','是否与以往工况相同'],'status':'unconfirmed'}],'actions':[{'id':'AR1','hypotheses':['HRCA1'],'proposal':'取得实际接触/保持与工况记录后再决定设计措施','owner_role':'待指定技术研究角色','completed':False},{'id':'AR2','hypotheses':['HRCA2'],'proposal':'区分请求与实际状态，并研究使用者是否理解','owner_role':'待指定界面/人因研究角色','completed':False},{'id':'AR3','hypotheses':['HRCA3'],'proposal':'核对象和工况变化及竞争解释','owner_role':'待指定现场研究角色','completed':False}],'confirmed_root_causes':[],'post_action':{'comparable_exposures':0,'events':0,'benefit_claim':None},'engineering_validated':False}
base16['evidence'].append({'id':'ER5','kind':'constructed_different_condition_check','content':'另一对象、无作业载荷的构造检查没有出现偏移','limit':'与事件条件不同，只能形成范围很窄的反向线索，不能排除事件时保持不足，也不计作同类暴露'})
base16['hypotheses'][0]['counterevidence']=['ER5']
base16['timeline'].append({'index':4,'event':'在不同对象/无作业载荷下的后续构造检查','evidence':['ER5']})
EV={x['id']:(x['kind'],x['content'],x['limit'])for x in base16['evidence']};HYP={x['id']:(x['claim'],tuple(x['support']),tuple(x['counterevidence']),tuple(x['unknowns']),x['status'])for x in base16['hypotheses']}
def check16(d):
 if (d['event_id'],d['version'],d['provenance'],d['event'])!=(base16['event_id'],base16['version'],base16['provenance'],base16['event']):raise ValueError('incident_scope_or_provenance_changed')
 if {x['id']:(x['kind'],x['content'],x['limit'])for x in d['evidence']}!=EV or len(d['evidence'])!=len(EV):raise ValueError('evidence_identity_content_or_limit_changed')
 for x in d['timeline']:
  if not set(x['evidence'])<=set(EV):raise ValueError('dangling_timeline_evidence')
 if d['timeline']!=base16['timeline']:raise ValueError('fixed_timeline_changed')
 for h in d['hypotheses']:
  if not set(h['support']+h['counterevidence'])<=set(EV):raise ValueError('dangling_causal_evidence')
 if {x['id']:(x['claim'],tuple(x['support']),tuple(x['counterevidence']),tuple(x['unknowns']),x['status'])for x in d['hypotheses']}!=HYP or len(d['hypotheses'])!=len(HYP):raise ValueError('competing_cause_or_support_mapping_changed')
 if d['confirmed_root_causes']or d['engineering_validated']:raise ValueError('unconfirmed_root_or_engineering_claim')
 if d['actions']!=base16['actions']:raise ValueError('action_mapping_or_completion_changed')
 pa=d['post_action']
 if any(type(pa[k])is not int for k in ['events','comparable_exposures']):raise ValueError('exposure_counts_must_be_integers')
 if pa['events']<0 or pa['comparable_exposures']<0 or pa['events']>pa['comparable_exposures']:raise ValueError('invalid_exposure_counts')
 if pa['benefit_claim']is not None:raise ValueError('effectiveness_claim_unestablished')
 rate=None if pa['comparable_exposures']==0 else pa['events']/pa['comparable_exposures']
 return {'method':'R16','state':'competing_explanations_unconfirmed','hypotheses':d['hypotheses'],'confirmed_root_causes':[],'immediate_vs_underlying':'偏移现象、实际作用与组织/信息条件分开；本例未确认因果链','action_queue':d['actions'],'follow_up':{'event_rate_for_declared_exposure':rate,'sufficient_for_effectiveness_claim':False,'reason':'no_comparable_exposure'if rate is None else'counts_alone_do_not_establish_causal_effect'},'requires':['事件原始记录与条件','支持和反证的区分性观察','措施实际实施证据','同类暴露与复查记录'],'not_claimed':['真实事故根因','操作员过失','措施已有效']}
out16=check16(base16);save('R16','01-构造事件与竞争解释输入.json',base16);save('R16','02-证据边界与行动输出.json',out16)
# Independent second-context desktop checks; no field observations.
transfer13={'scenario':'文件导出状态界面','state_map_A':{'preview':'完成','file_saved':'完成'},'state_map_B':{'preview':'预览已生成，尚未保存','file_saved':'文件已保存'},'provenance':'constructed_encoding_check_not_user_study'}
transfer13['computed_collision_A']=len(set(transfer13['state_map_A'].values()))<2;transfer13['computed_collision_B']=len(set(transfer13['state_map_B'].values()))<2
assert transfer13['computed_collision_A']and not transfer13['computed_collision_B']
save('R13','03-不同情境表征复算.json',transfer13)
transfer15={'scenario':'文档特定版本回查','provenance':'constructed_desktop_logic_review_not_unique_FAST','selected_HOW_path':['回查特定版本','标识具体版本','保存指纹与索引'],'WHY_reverse':['保存指纹与索引','标识具体版本','回查特定版本'],'review':['仅一条局部逻辑路径，不等于完整归档流程','若只有先扫描再上传，属于时间/流程关系，不能自动替代HOW/WHY','权限、可读性和长期保存为其他需研究功能'],'engineering_validated':False}
assert list(reversed(transfer15['selected_HOW_path']))==transfer15['WHY_reverse'];save('R15','03-不同情境逻辑复核.json',transfer15)
transfer16={'scenario':'导出文件无法打开的构造事件','provenance':'constructed_competing_explanations_desktop_review','competing_causes':['生成格式不完整','传输中断','阅读环境不支持'],'why_no_single_root':'同一无法打开现象与三种解释都相容；需文件原件、传输记录及环境对照','evidence_gaps':['源/目标文件和SHA','实际错误消息与版本','同文件在另一环境的结果'],'confirmed_causes':[],'real_incident':False};save('R16','03-不同情境竞争解释复核.json',transfer16)
# Execute fixed-model mutations and save actual inputs, outputs, and expected observations.
records=[]
def probe(rid,name,kind,base,fn,mutation,error=None,predicate=None):
 d=copy.deepcopy(base);mutation(d)
 try:
  out=fn(d)
  if error:raise AssertionError('expected rejection '+error)
  if predicate:assert predicate(out)
  status='accepted_with_bounded_state'
 except ValueError as e:
  assert str(e)==error,(name,str(e),error);out={'error':str(e)};status='rejected'
 save(rid,'检查/'+name+'-输入.json',d);save(rid,'检查/'+name+'-输出.json',{'status':status,'output':out})
 records.append({'method':rid,'case':name,'class':kind,'expected_error':error,'actual':status,'passed':True})
probe('R13','normal-encoding-not-usability','normal',base13,check13,lambda d:None,predicate=lambda o:o['representation_analysis'][0]['representation_collision']and not o['representation_analysis'][1]['representation_collision'])
probe('R13','missing-abnormal-task','missing_material',base13,check13,lambda d:d['tasks'].pop(1),'task_or_information_mapping_changed')
probe('R13','use-as-production-evidence','not_applicable',base13,check13,lambda d:d.update(provenance='production_user_study'),'provenance_changed')
probe('R13','invent-average-body-dimension','boundary',base13,check13,lambda d:d['population'].update(anthropometric_parameters={'reach_mm':700}),'unsupported_population_claim')
probe('R13','pretend-B-more-usable','conflict',base13,check13,lambda d:d.update(conclusion='B_has_better_usability'),'fabricated_user_or_engineering_result')
probe('R13','missing-state-encoding','missing_material',base13,check13,lambda d:d['representations']['B'].pop('S-STALE'),'state_representation_missing')
probe('R13','tamper-task-info-mapping','conflict',base13,check13,lambda d:d['tasks'][0].update(information=['actual_stop']),'task_or_information_mapping_changed')
probe('R15','normal-declared-logic','normal',base15,check15,lambda d:None)
probe('R15','missing-WHY-answer','missing_material',base15,check15,lambda d:d['edges'][0].update(why=''),'declared_means_purpose_or_question_changed')
probe('R15','mistake-for-process-timeline','not_applicable',base15,check15,lambda d:d.update(not_clock_sequence=False),'logic_direction_or_temporal_confusion')
probe('R15','reverse-HOW','boundary',base15,check15,lambda d:d.update(how_direction='right_to_left'),'logic_direction_or_temporal_confusion')
probe('R15','change-edge-kind','conflict',base15,check15,lambda d:d['edges'][1].update(kind='temporal_before'),'declared_means_purpose_or_question_changed')
probe('R15','remove-support-function','missing_material',base15,check15,lambda d:d.update(support=[]),'support_function_lost_or_changed')
probe('R15','hide-scope-boundary','boundary',base15,check15,lambda d:d['nodes'][0].update(scope='inside_basic'),'node_identity_or_scope_changed')
probe('R16','normal-competing-causes','normal',base16,check16,lambda d:None,predicate=lambda o:o['follow_up']['event_rate_for_declared_exposure']is None)
probe('R16','missing-evidence','missing_material',base16,check16,lambda d:d['evidence'].pop(),'evidence_identity_content_or_limit_changed')
probe('R16','fiction-as-customer-incident','not_applicable',base16,check16,lambda d:d.update(provenance='customer_confirmed_incident'),'incident_scope_or_provenance_changed')
probe('R16','zero-exposure-benefit','boundary',base16,check16,lambda d:d['post_action'].update(benefit_claim='已根治'),'effectiveness_claim_unestablished')
probe('R16','declare-one-root','conflict',base16,check16,lambda d:d['confirmed_root_causes'].append('HRCA2'),'unconfirmed_root_or_engineering_claim')
probe('R16','swap-cause-support-mapping','conflict',base16,check16,lambda d:d['hypotheses'][0].update(support=['ER1']),'competing_cause_or_support_mapping_changed')
probe('R16','action-completed-without-evidence','boundary',base16,check16,lambda d:d['actions'][0].update(completed=True),'action_mapping_or_completion_changed')
for rid in DIRS:
 rr=[x for x in records if x['method']==rid];save(rid,'04-实际检查汇总.json',{'method':rid,'cases':rr,'executed':len(rr),'passed':len(rr),'scope':'fixed_declarations_and_bookkeeping_only_not_semantic_or_engineering_validator','actual_human_participants':0,'actual_field_trials':0})
print(json.dumps({'cases':len(records),'passed':len(records),'R13':'encoding_collision_is_not_usability','R15':'declared_how_why_not_clock','R16':'no_confirmed_cause_zero_exposure_no_rate'},ensure_ascii=False))
