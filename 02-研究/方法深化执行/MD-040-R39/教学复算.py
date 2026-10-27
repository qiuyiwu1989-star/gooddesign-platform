# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy,statistics,math
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
VALUES=[[75,86,67,98],[87,78,56,91],[77,89,78,8],[95,65,77,95],[78,78,59,94],[56,79,67,94],[79,80,66,85],[71,80,73,95]]
base={'origin':'NIST illustrative fictitious starter_motor example not tree trials','controls':['I1-turns','I2-wire-gauge','I3-ferric-content'],'noise':['E1-temperature','E2-battery-voltage'],'service_controllable_noise':False,'outer_conditions':[[-1,-1],[1,-1],[-1,1],[1,1]],'responses':VALUES,'response_unit':'percent theoretical maximum torque','field_noise_distribution':None,'tolerance_cost_model':None,'target_mean':None,'claim_unique_winner':False,'actual_confirmation':[]}
def check(i):
 for k in ['origin','controls','noise','outer_conditions','response_unit']:
  if i[k]!=base[k]:raise ValueError('control_noise_scope_or_units_changed')
 if i['service_controllable_noise']or i['claim_unique_winner']or i['actual_confirmation']or i['field_noise_distribution']is not None or i['tolerance_cost_model']is not None or i['target_mean']is not None:raise ValueError('unsupported_control_distribution_target_cost_or_confirmation')
 if i['responses']!=VALUES or len(i['responses'])!=8 or any(len(r)!=4 for r in i['responses']):raise ValueError('published_table_changed')
 if any(type(v)not in(int,float)or not math.isfinite(v)for r in i['responses']for v in r):raise ValueError('invalid_response')
 rows=[{'inner_row':k+1,'mean':statistics.mean(r),'sample_sd_across_outer_conditions':statistics.stdev(r),'range':[min(r),max(r)],'equal_weight_scenario_mean_not_field_expectation':True}for k,r in enumerate(i['responses'])]
 bestmean=max(rows,key=lambda x:x['mean'])['inner_row'];bestsd=min(rows,key=lambda x:x['sample_sd_across_outer_conditions'])['inner_row']
 nondom=[a['inner_row']for a in rows if not any(b['mean']>=a['mean']and b['sample_sd_across_outer_conditions']<=a['sample_sd_across_outer_conditions']and(b['mean']>a['mean']or b['sample_sd_across_outer_conditions']<a['sample_sd_across_outer_conditions'])for b in rows)]
 return {'rows':rows,'highest_mean_row':bestmean,'lowest_scatter_row':bestsd,'nondominated_on_declared_two_metrics':nondom,'unique_winner':None,'field_failure_probability':None,'tolerance_tightening_economic_choice':None,'reason':'no target, field distribution or cost function','engineering_validated':False}
put('01-内外因素与公开教学表.json',base);out=check(base);assert out['highest_mean_row']==4 and out['lowest_scatter_row']==7;put('02-均值散布与权衡.json',out);cases=[]
def t(name,kind,mut,expected):
 q=copy.deepcopy(base);mut(q)
 try:o=check(q);state='accepted'
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};state='rejected'
 cases.append({'name':name,'class':kind,'input':q,'output':o,'actual':state,'expected':expected,'pass':state==expected})
t('normal','正常',lambda x:None,'accepted');t('missing_noise_corner','缺材料',lambda x:x['responses'][0].pop(),'rejected');t('lab_noise_as_field_control','不适用',lambda x:x.update(service_controllable_noise=True),'rejected');t('claim_unique_from_mean','冲突',lambda x:x.update(claim_unique_winner=True),'rejected');t('unknown_cost_to_zero','缺材料',lambda x:x.update(tolerance_cost_model=0),'rejected');t('invent_noise_distribution','冲突',lambda x:x.update(field_noise_distribution='uniform'),'rejected');t('bool_response','边界',lambda x:x['responses'][0].__setitem__(0,True),'rejected');t('fake_confirmation','冲突',lambda x:x['actual_confirmation'].append('passed'),'rejected')
assert all(x['pass']for x in cases);put('03-实际检查.json',cases)
put('04-迁移桌面检查.json',{'context':'tapping contact robustness research','possible_controls':['fixture compliance setting','relative motion setting'],'noise_hypotheses':['bark state','contamination','wear'],'bark_state_is_service_control':False,'field_distribution':None,'study_proposal':'safe surrogate crossing control settings with selected noise conditions; preserve per-condition outcomes','cost_tradeoff':'tighter manufacturing tolerance may add cost, no cost curve available','actual_target_experiments':0})
print('R39:8 checks passed')
