"""ML-014 exact arithmetic teaching example. Invented losses/priors, no robot evidence."""
from fractions import Fraction as F
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'02-研究/ML-014-逐法深度研究/教学演算/VOI-二行动二状态.json'
LOSS={'M':{'normal':F(0),'difficult':F(100)},'S':{'normal':F(30),'difficult':F(40)}}
def optimal(p):
    values={a:(1-p)*v['normal']+p*v['difficult'] for a,v in LOSS.items()}
    a=min(values,key=values.get)
    return a,values[a],values

def analyse(prior,sensitivity,specificity,cost):
    if not all(F(0)<=x<=F(1) for x in (prior,sensitivity,specificity)) or cost<0:raise ValueError('invalid teaching probability/cost')
    action,current,losses=optimal(prior)
    perfect=(1-prior)*min(x['normal'] for x in LOSS.values())+prior*min(x['difficult'] for x in LOSS.values())
    rows=[];after=F(0)
    for obs,likelihood in [('positive',{'normal':1-specificity,'difficult':sensitivity}),('negative',{'normal':specificity,'difficult':1-sensitivity})]:
        prob=(1-prior)*likelihood['normal']+prior*likelihood['difficult']
        if prob==0:continue
        posterior=prior*likelihood['difficult']/prob
        chosen,value,_=optimal(posterior);after+=prob*value
        rows.append({'observation':obs,'probability':prob,'posterior_difficult':posterior,'chosen':chosen,'expected_loss':value})
    return {'prior':prior,'action_without_study':action,'current_losses':losses,'current_expected_loss':current,'perfect_information_expected_loss':perfect,'EVPI':current-perfect,'study_expected_loss':after,'EVSI':current-after,'study_cost':cost,'net_learning_value':current-after-cost,'branches':rows}

def run():
    main=analyse(F(1,2),F(4,5),F(4,5),F(4))
    assert main['current_expected_loss']==35 and main['EVPI']==15 and main['EVSI']==6 and main['net_learning_value']==2
    assert analyse(F(1,2),F(1,2),F(1,2),F(0))['EVSI']==0
    assert analyse(F(1,2),F(1),F(1),F(0))['EVSI']==15
    try:analyse(F(6,5),F(1),F(1),F(0))
    except ValueError:invalid_rejected=True
    else:raise AssertionError('bad probability accepted')
    record={'scope':'executed_mathematical_teaching_only_not_field_test','all_probabilities_and_losses':'invented_for_teaching_not_customer_or_case_data','loss_units':'arbitrary_teaching_units_not_currency','actions':{'M':'mechanical_route_label_only','S':'sensor_route_label_only'},'loss_table':LOSS,'result':main,'checks':{'uninformative_study_zero_EVSI':True,'perfect_study_equals_EVPI':True,'invalid_probability_rejected':invalid_rejected},'source_scope':'Platform original numerical exercise using decision-theoretic expected-loss definitions; does not reproduce the source paper code.','source_url':'https://arxiv.org/pdf/1905.00008','not_concluded':['No real route recommendation','No field sensitivity or specificity measured','No safety constraint may be waived on economic value']}
    OUT.write_text(json.dumps(record,ensure_ascii=False,indent=2,default=lambda x:str(x))+'\n')
    print('Teaching only: EVPI=15, EVSI=6, net=2; three boundary checks passed')
if __name__=='__main__':run()
