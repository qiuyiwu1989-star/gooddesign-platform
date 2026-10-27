"""Original tiny teaching calculations, not full method implementations or engineering tests."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
results={'mode':'platform_teaching_assumptions','engineering_validated':False,'checks':{}}
# R24: energy is necessary but not sufficient for usable return motion.
available=.2*9.81*.05*.6;required=3*.03
assert available<required
results['checks']['R24']={'m_kg':.2,'vertical_drop_m':.05,'efficiency_assumption':.6,'available_J':available,'force_N':3,'stroke_m':.03,'required_J':required,'budget':'insufficient','orientation_not_checked':True}
# R30: row FR / column DP; exact declared zeros only, no empirical identification.
def classify(a):
 if any(v is None for row in a for v in row):return 'unknown'
 n=len(a);off=[(i,j) for i in range(n) for j in range(n) if i!=j and a[i][j]!=0]
 if not off:return 'diagonal_declared'
 if all(i>j for i,j in off):return 'lower_triangular_declared'
 if all(i<j for i,j in off):return 'upper_triangular_declared'
 return 'coupled_in_current_order'
matrices=[[[1,0],[0,1]],[[1,0],[1,1]],[[1,1],[1,1]],[[1,None],[0,1]]]
labels=[classify(a) for a in matrices];assert labels==['diagonal_declared','lower_triangular_declared','coupled_in_current_order','unknown']
results['checks']['R30']={'row':'FR','column':'DP','matrices':matrices,'classification':labels,'information_axiom_not_computed':True}
# R31: directed dependency A->B, B->A, B->C; brute-force mutual reachability for this finite fixture.
nodes=['A','B','C'];edges={('A','B'),('B','A'),('B','C')}
def reachable(a,b):
 pending=[a];seen=set()
 while pending:
  x=pending.pop()
  if x==b:return True
  if x in seen:continue
  seen.add(x);pending.extend(v for u,v in edges if u==x)
 return False
components=[];remaining=set(nodes)
while remaining:
 a=sorted(remaining)[0];comp={b for b in remaining if reachable(a,b) and reachable(b,a)};components.append(sorted(comp));remaining-=comp
assert components==[['A','B'],['C']]
results['checks']['R31']={'convention':'row impacts column','nodes':nodes,'edges':sorted(edges),'matrix':[[int((a,b) in edges) for b in nodes] for a in nodes],'strong_components':components,'condensed_order':[['A','B'],['C']],'physical_coupling_not_modified':True}
# R32: generic planar rigid-link count only, not geometry/synthesis/full trajectory verification.
results['checks']['R32']={'moving_bodies':3,'lower_pairs':4,'generic_planar_DOF':3*3-2*4,'special_geometry_redundancy_not_proven':True,'full_motion_scan_executed':False}
assert results['checks']['R32']['generic_planar_DOF']==1
# R33: fictional materials, axial elastic stiffness-only model; no commercial material recommendation.
materials=[{'id':'A','E_Pa':70e9,'rho_kg_m3':2700,'temperature_limit_C':150},{'id':'B','E_Pa':200e9,'rho_kg_m3':7800,'temperature_limit_C':120},{'id':'C','E_Pa':110e9,'rho_kg_m3':4500,'temperature_limit_C':60}]
for m in materials:
 m['temperature_pass']=m['temperature_limit_C']>=80;m['index_E_over_rho']=m['E_Pa']/m['rho_kg_m3'];m['minimum_mass_kg_stiffness_only']=m['rho_kg_m3']*1000*1**2/(m['E_Pa']*.001)
ranked=sorted([m for m in materials if m['temperature_pass']],key=lambda m:m['index_E_over_rho'],reverse=True)
assert [m['id'] for m in ranked]==['A','B']
results['checks']['R33']={'F_N':1000,'L_m':1,'delta_max_m':.001,'temperature_C':80,'materials':materials,'screened_ranking':[m['id'] for m in ranked],'other_constraints_unchecked':['strength','buckling','fatigue','corrosion','processing']}
# R36: hard constraints are not compensated by relative preference marks.
rows=[{'candidate':'C1','hard':None,'marks':[1,1]},{'candidate':'C2','hard':False,'marks':[1,1]},{'candidate':'C3','hard':True,'marks':[0,None]}]
for x in rows:x['state']='blocked_hard_failure' if x['hard'] is False else 'hold_hard_unknown' if x['hard'] is None else 'incomplete_comparison' if None in x['marks'] else 'comparison_complete'
assert [r['state'] for r in rows]==['hold_hard_unknown','blocked_hard_failure','incomplete_comparison']
results['checks']['R36']={'fixtures':rows,'recommendations':[],'weighted_optimization_not_run':True}
(OUT/'教学小算例-实际输出.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print('6 tiny teaching checks passed; no full-method or engineering certification')
