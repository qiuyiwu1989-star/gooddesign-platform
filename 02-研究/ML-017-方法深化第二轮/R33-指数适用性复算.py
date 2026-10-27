"""Constructed, not measured material data: changing governing model reverses ranking."""
from pathlib import Path
import json,math
OUT=Path(__file__).resolve().parent/'教学复算';OUT.mkdir(exist_ok=True)
F,L,delta=100.,.3,.001
materials=[{'id':'A','E_Pa':70e9,'rho_kg_m3':2700.},{'id':'B','E_Pa':210e9,'rho_kg_m3':7800.}]
rows=[]
for m in materials:
 E,rho=m['E_Pa'],m['rho_kg_m3'];area=F*L/(E*delta);side=(4*F*L**3/(E*delta))**.25
 rows.append({**m,'tension_area_m2':area,'tension_mass_kg':rho*L*area,'cantilever_square_side_m':side,'cantilever_mass_kg':rho*L*side**2,'tension_deflection_m':F*L/(E*area),'cantilever_deflection_m':F*L**3/(3*E*(side**4/12))})
 assert math.isclose(rows[-1]['tension_deflection_m'],delta,rel_tol=1e-12)
 assert math.isclose(rows[-1]['cantilever_deflection_m'],delta,rel_tol=1e-12)
assert rows[1]['tension_mass_kg']<rows[0]['tension_mass_kg']
assert rows[0]['cantilever_mass_kg']<rows[1]['cantilever_mass_kg']
r={'scope':'synthetic_material_properties_teaching_algebra_not_selection_for_real_product','parameters_SI':{'F_N':F,'L_m':L,'max_deflection_m':delta},'models':{'tension':'delta=FL/EA; mass=rho*L*A; rank E/rho','square_cantilever':'delta=FL^3/(3EI), I=a^4/12; rank sqrt(E)/rho'},'rows':rows,'rank_tension':['B','A'],'rank_bending':['A','B'],'omitted_constraints':['strength','buckling','fatigue','minimum_section','temperature','corrosion','manufacturing','joints'],'engineering_validated':False}
(OUT/'R33-工况改变排名反转.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));print(json.dumps(r,ensure_ascii=False))
