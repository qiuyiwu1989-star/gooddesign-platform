"""Recalculate displayed comparisons from Mazur 2013 Fig2; no invented client scores."""
from pathlib import Path
import hashlib,json,math
P=Path(__file__).resolve().parent;O=P/'教学包';O.mkdir(exist_ok=True)
source=P/'private-sources/QFDI-MEMBERSHIP2013.pdf'
def normalize(t):
 # Published displayed fractions: row1 1,1 4/5,1 1/4; row2 5/9,1,5/9; row3 4/5,1 4/5,1.
 A=[[1,9/5,t],[5/9,1,5/9],[1/t,9/5,1]];col=[sum(row[j]for row in A)for j in range(3)];N=[[row[j]/col[j]for j in range(3)]for row in A];w=[sum(row)/3 for row in N]
 assert math.isclose(sum(w),1,rel_tol=1e-12)
 return {'matrix':A,'normalized_column_row_average':w,'ordering':sorted(range(3),key=lambda i:w[i],reverse=True)}
base=normalize(5/4);published=[.421,.216,.363]
max_difference=max(abs(x-y)for x,y in zip(base['normalized_column_row_average'],published))
assert max_difference<.002
# t=1 is an algebraically derived tie for N1/N3 given the other displayed comparisons.
tie=normalize(1);assert abs(tie['normalized_column_row_average'][0]-tie['normalized_column_row_average'][2])<1e-12
# Invert the displayed preference solely as a counterfactual; not a plausible confidence interval.
flipped=normalize(4/5);assert base['ordering']==[0,2,1] and flipped['ordering']==[2,0,1]
r={'scope':'published_non_rubber_case_partial_recalculation_from_displayed_rounded_ratios','source':{'url':'https://static1.squarespace.com/static/5eb315d2b0e6914ba0419e47/t/5eb87c450e4d61663a0a7eb6/1589148741728/mazur_2013_qfd_for_membership_organizations.pdf','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'locator':'PDF page10 / printed page9 / Figure2'},'need_labels_paraphrased':['质量方法改进','质量实践改进','组织改进'],'base':base,'reported_displayed_row_averages':published,'reproduction_tolerance':.002,'observed_max_difference':max_difference,'not_exact_replication':'published comparison fractions and sums are display-rounded; original participant matrices not available','sensitivity':{'algebraic_tie_t':1,'tie':tie,'counterfactual_inverted_display_ratio':flipped,'not_a_confidence_interval':True,'not_new_survey_data':True},'not_claimed':['QFD full deployment replication','eigenvector/CR replication','client importance','engineering targets','rubber robot ranking']}
(O/'07-公开案例局部复算与敏感性.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'base':base['normalized_column_row_average'],'tie_ratio':1,'rank_before':base['ordering'],'counterfactual_rank':flipped['ordering']},ensure_ascii=False))
