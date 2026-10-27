from pathlib import Path
import json,math,copy
P=Path(__file__).resolve().parent
base={'id':'R33-TEACH-001','origin':'synthetic_not_database_or_measured','F_N':100.,'L_m':.3,'deflection_limit_m':.001,'max_service_C':50.,'geometry_free':True,'model':'axial','materials':[{'id':'A','E_Pa':70e9,'rho_kg_m3':2700.,'allowable_stress_Pa':300e6,'temperature_limit_C':120.,'manufacturable':True,'cost_per_kg':None},{'id':'B','E_Pa':210e9,'rho_kg_m3':7800.,'allowable_stress_Pa':900e6,'temperature_limit_C':80.,'manufacturable':True,'cost_per_kg':None}]}
def calc(d):
 if d.get('origin')!='synthetic_not_database_or_measured':raise ValueError('unsupported property provenance')
 if any(d.get(k)is None for k in ['F_N','L_m','deflection_limit_m','max_service_C']):return {'status':'unknown_constraints','ranking':None}
 if type(d.get('max_service_C'))not in(int,float)or not math.isfinite(d['max_service_C']):raise ValueError('finite nonboolean service temperature required')
 if type(d.get('geometry_free'))is not bool:raise ValueError('explicit geometry boolean required')
 if not d['geometry_free']:return {'status':'not_applicable_fixed_geometry','ranking':None}
 if d['model']not in ['axial','square_cantilever']:raise ValueError('unsupported model, e.g. panel needs different exponent')
 F,L,de=d['F_N'],d['L_m'],d['deflection_limit_m']
 if any(type(v)not in (int,float)or not math.isfinite(v)or v<=0 for v in [F,L,de]):raise ValueError('positive finite physical quantities required')
 rows=[]
 for m in d['materials']:
  needed=['E_Pa','rho_kg_m3','allowable_stress_Pa','temperature_limit_C','manufacturable']
  if any(m.get(k)is None for k in needed):rows.append({'id':m['id'],'state':'unknown','reason':'missing required material/processing evidence'});continue
  E,rho=m['E_Pa'],m['rho_kg_m3']
  if any(type(v)not in(int,float)or not math.isfinite(v)for v in [E,rho,m['allowable_stress_Pa'],m['temperature_limit_C']]):raise ValueError('invalid material property shape')
  if min(E,rho,m['allowable_stress_Pa'])<=0:raise ValueError('invalid property')
  if d['max_service_C']>m['temperature_limit_C']or m['manufacturable']is not True:rows.append({'id':m['id'],'state':'excluded','reason':'temperature/process constraint'});continue
  if d['model']=='axial':
   area=max(F*L/(E*de),F/m['allowable_stress_Pa']);disp=F*L/(E*area);stress=F/area;mass=rho*L*area;index=E/rho;geom={'area_m2':area}
  else:
   side=max((4*F*L**3/(E*de))**.25,(6*F*L/m['allowable_stress_Pa'])**(1/3));disp=4*F*L**3/(E*side**4);stress=6*F*L/side**3;mass=rho*L*side**2;index=math.sqrt(E)/rho;geom={'square_side_m':side}
  assert disp<=de*(1+1e-12)and stress<=m['allowable_stress_Pa']*(1+1e-12)
  rows.append({'id':m['id'],'state':'constructed_feasible_only','geometry':geom,'mass_kg':mass,'deflection_m':disp,'stress_Pa':stress,'stiffness_index':index,'cost_comparison':'unknown'})
 feasible=[r for r in rows if r['state']=='constructed_feasible_only'];return {'status':'constructed_model_only','rows':rows,'ranking_by_mass':[r['id']for r in sorted(feasible,key=lambda r:r['mass_kg'])],'engineering_validated':False,'cost_rank':None}
cases=[]
def add(n,d,e):
 r=calc(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常轴向',base,'constructed_model_only');assert cases[-1]['actual']['ranking_by_mass']==['B','A']
x=copy.deepcopy(base);x['model']='square_cantilever';add('弯曲改变排名',x,'constructed_model_only');assert cases[-1]['actual']['ranking_by_mass']==['A','B']
x=copy.deepcopy(base);x['materials'][0]['E_Pa']=None;add('缺物性',x,'constructed_model_only');assert cases[-1]['actual']['rows'][0]['state']=='unknown'
x=copy.deepcopy(base);x['geometry_free']=False;add('固定几何不适用',x,'not_applicable_fixed_geometry')
x=copy.deepcopy(base);x['max_service_C']=80;add('温度等界',x,'constructed_model_only');assert len(cases[-1]['actual']['ranking_by_mass'])==2
x=copy.deepcopy(base);x['max_service_C']=100;add('温度筛除名义最优B',x,'constructed_model_only');assert cases[-1]['actual']['ranking_by_mass']==['A']
x=copy.deepcopy(base);x['id']='DISPLAY-SUPPORT-TEACH';x.update(F_N=50.,L_m=.2,model='square_cantilever');add('展示支架不同情境',x,'constructed_model_only')
try:x=copy.deepcopy(base);x['model']='bending_panel';calc(x);raise AssertionError('wrong model accepted')
except ValueError:cases.append({'name':'弯曲板不套方梁指数','actual':'rejected','passed':True})
for n,mut in [('old-service-NaN',lambda d:d.update(max_service_C=float('nan'))),('service-Inf',lambda d:d.update(max_service_C=float('inf'))),('service-bool',lambda d:d.update(max_service_C=True)),('load-bool',lambda d:d.update(F_N=True)),('geometry-string-false',lambda d:d.update(geometry_free='false')),('property-bool',lambda d:d['materials'][0].update(E_Pa=True))]:
 q=copy.deepcopy(base);mut(q)
 try:calc(q);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
(P/'教学包/01-输入.json').write_text(json.dumps(base,ensure_ascii=False,indent=2)+'\n');(P/'教学包/02-实际复算.json').write_text(json.dumps({'cases':cases,'count':len(cases),'scope':'synthetic material properties, closed-form static stiffness/strength only, not purchasing decision'},ensure_ascii=False,indent=2)+'\n');print(len(cases),'passed')
