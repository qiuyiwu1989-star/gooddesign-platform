"""Descriptive internal AI ratings. No significance, expert or 80-point claims."""
import collections,hashlib,json,statistics
from pathlib import Path
from collect_innovation_loop_round2 import collect,BASE
DIMS=['problem','evidence','mechanism','feasibility','validation']
def require(condition,message):
 if not condition:raise ValueError(message)

def summarize():
 audit=collect();require(audit['succeeded']==24 and audit['failed']==0 and audit['missing']==0,'incomplete_actual_outputs')
 mapping=json.loads((BASE/'private/mapping.json').read_text())['mapping'];amap={x['anonymous_id']:x['run_id'] for x in mapping};expected=set(amap);runs={r['run_id']:r for r in audit['records']};rows=[]
 reviews=[]
 for i in [1,2]:
  path=BASE/f'reviewer/review-{i}.json';r=json.loads(path.read_text());papers=r['papers'];require(len(papers)==24 and {p['anonymous_id'] for p in papers}==expected and len({p['anonymous_id'] for p in papers})==24,'review_identity_mismatch')
  reviews.append({'reviewer':i,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'blindness_statement':r['blindness_statement']})
  for p in papers:
   require(set(p['scores'])==set(DIMS),'invalid_score_dimensions')
   require(all(type(v) is int and 0<=v<=4 for v in p['scores'].values()),'invalid_score_range')
   meta=runs[amap[p['anonymous_id']]];rows.append({'reviewer':i,'run_id':meta['run_id'],'task_id':meta['task_id'],'arm':meta['arm'],'replicate':meta['replicate'],'scores':p['scores'],'hard_errors':p['hard_errors'],'rationale':p['rationale']})
 summary=[]
 for arm in 'ABCD':
  picked=[r for r in rows if r['arm']==arm];summary.append({'arm':arm,'ratings':len(picked),'dimension_means':{d:round(statistics.mean(r['scores'][d] for r in picked),3) for d in DIMS},'dimension_ranges':{d:[min(r['scores'][d] for r in picked),max(r['scores'][d] for r in picked)] for d in DIMS}})
 differences=[]
 for task in ['rubber-v1','gear-v1','polish-v1']:
  for reviewer in [1,2]:
   for arm in 'BCD':
    base=[r for r in rows if r['task_id']==task and r['reviewer']==reviewer and r['arm']=='A'];treatment=[r for r in rows if r['task_id']==task and r['reviewer']==reviewer and r['arm']==arm]
    differences.append({'task':task,'reviewer':reviewer,'arm_vs_A':arm,'dimension_delta':{d:statistics.mean(r['scores'][d] for r in treatment)-statistics.mean(r['scores'][d] for r in base) for d in DIMS}})
 disagreements=[]
 for run in runs:
  pair=[r for r in rows if r['run_id']==run];require(len(pair)==2,'missing_review_pair')
  delta={d:pair[1]['scores'][d]-pair[0]['scores'][d] for d in DIMS}
  if any(delta.values()):disagreements.append({'run_id':run,'reviewer2_minus_reviewer1':delta})
 result={'scope':'single exploratory internal AI pilot','reports':24,'ai_reviews':48,'reviews':reviews,'arms':summary,'rows':rows,'paired_descriptive_deltas':differences,'reviewer_disagreements':disagreements,'confirmed_hard_errors_by_reviewers':sum(bool(r['hard_errors']) for r in rows),'domain_effectiveness_established':False,'statistical_significance_claimed':False,'overall_score_80_claimed':False,'elapsed_token_fee_matched':False,'limitations':['three platform research proposals, no customer confirmation','six bounded v0.4 source contexts not representative of full 560-project library','not retrieval/end-to-end engine comparison','same declared model family, exact provider build and hidden compute unavailable','detailed rubric frozen before review but after some generation','order-balanced limited AI blinding; not OS-enforced isolation','per-run elapsed missing; 600s cap compliance not certified','high rating compression; no sensitive business benefit threshold']}
 (BASE/'descriptive-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(summary,ensure_ascii=False,indent=2));print('disagreements',len(disagreements))
if __name__=='__main__':summarize()
