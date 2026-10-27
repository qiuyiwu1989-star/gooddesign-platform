# -*- coding: utf-8 -*-
from pathlib import Path
import json
D=Path(__file__).resolve().parent
learning=[{'id':'D1','request_job':'J101','requested_version':'v1','selected_version':'v1','artifact_job':'J101','artifact_version':'v1'},{'id':'D2','request_job':'J102','requested_version':'v2','selected_version':'v2','artifact_job':'J101','artifact_version':'v1'},{'id':'D3','request_job':'J103','requested_version':'v3','selected_version':'v3','artifact_job':'J102','artifact_version':'v2'}]
confirmation=[{'id':'C1','request_job':'J201','requested_version':'v4','selected_version':'v4','artifact_job':'J201','artifact_version':'v4'},{'id':'C2','request_job':'J202','requested_version':'v5','selected_version':'v5','artifact_job':'J201','artifact_version':'v4'},{'id':'C3','request_job':'J203','requested_version':'v6','selected_version':'v6','artifact_job':None,'artifact_version':'v6'}]
def identity_gate(r):
 fields=['request_job','requested_version','selected_version','artifact_job','artifact_version']
 if any(type(r.get(k))is not str or not r[k]for k in fields):return 'withhold_missing_identity'
 return 'release_identity_only'if r['request_job']==r['artifact_job']and r['requested_version']==r['selected_version']==r['artifact_version']else'withhold_mismatch'
L=[{'id':r['id'],'selection_matches':r['selected_version']==r['requested_version'],'disposition':identity_gate(r)}for r in learning];C=[{'id':r['id'],'actual':identity_gate(r),'expected':e}for r,e in zip(confirmation,['release_identity_only','withhold_mismatch','withhold_missing_identity'])];assert all(z['actual']==z['expected']for z in C);assert all(z['selection_matches']for z in L)
out={'origin':'all_authored_records_not_real_measurements','CTQ':'request and returned artifact job/version identities match before delivery marking','learning_records':learning,'analysis':L,'H1_selection_mismatch':'not_supported_in_these_records','H2_return_binding_mismatch':'fits_D2_D3_not_proof_of_real_implementation_root_cause','design_choice':{'A_prompt_only':'does_not_enforce_CTQ','B_identity_binding_and_gate':'selected_for_teaching'},'confirmation_records':confirmation,'confirmation':C,'confirmation_inputs':'different identities from learning, fixed after gate definition; not field trial','not_claimed':['real_defect_rate','Cp_Cpk_sigma','readable_or_correct_content','complete_concurrency_validation']}
(D/'R07-构造闭环.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print('3 independent authored confirmation inputs matched fixed expectations')
