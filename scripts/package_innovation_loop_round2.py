"""Freeze anonymized reviewer packets only after all original reports are present."""
import hashlib,json
from pathlib import Path
from collect_innovation_loop_round2 import collect,BASE
from innovation_loop_evaluation import build_anonymous_package

def package():
 audit=collect()
 if audit['missing'] or audit['failed']:raise ValueError('all 24 actual eligible outputs required for this package')
 out=BASE/'reviewer';priv=BASE/'private';priv.mkdir(exist_ok=True)
 if (priv/'mapping.json').exists():raise ValueError('review package already frozen')
 records=[]
 for r in audit['records']:
  p=BASE/r['output_ref'];records.append({'run_id':r['run_id'],'text':p.read_text(),'source_path':str(p),'source_filename':p.name})
 result=build_anonymous_package(records,20261031)
 mapping=result['private_mapping'];lookup={r['run_id']:r['task_id'] for r in audit['records']};tasks_by_anon={m['anonymous_id']:lookup[m['run_id']] for m in mapping['mapping']}
 papers=result['reviewer_package']['papers']
 for p in papers:p['task_id']=tasks_by_anon[p['anonymous_id']]
 common={}
 for task in ['rubber-v1','gear-v1','polish-v1']:
  p=json.loads((BASE/'inputs'/(task+'-A.json')).read_text());common[task]={k:p[k] for k in ['title','input_status','requirement']}
 refs={'experience':json.loads((BASE/'inputs/rubber-v1-B.json').read_text())['experience'],'methods':json.loads((BASE/'inputs/rubber-v1-C.json').read_text())['methods']}
 for n,rows in [(1,papers),(2,list(reversed(papers)))]:
  dest=out/f'packet-{n}.json';dest.write_text(json.dumps({'common_tasks':common,'neutral_reference_material':refs,'papers':rows,'notice':'只读本包及rubric；不查原目录/映射/其他评审，AI有限遮盲。'},ensure_ascii=False,indent=2)+'\n')
 (priv/'mapping.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n')
 (out/'package-pins.json').write_text(json.dumps({'files':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'packet-1.json',out/'packet-2.json',out/'rubric.md']},'mapping_separate':True,'os_isolation_enforced':False,'hard_blind':False,'rubric_detail_frozen_before_review_not_all_generation':True},indent=2))
 print('24 outputs packaged, two order-balanced reviewer packets')
if __name__=='__main__':package()
