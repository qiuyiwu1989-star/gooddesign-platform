from pathlib import Path
import json,math,copy
P=Path(__file__).resolve().parent
base={'id':'WB06-SDOF-TEACH-001','origin':'independent_linear_oscillator_not_Wen_full_dynamic_algorithm','configuration':'single_linear_mode_fixed_mounting_TEACH-1','mass_kg':1.,'stiffness_N_m':500.,'damping_Ns_m':2.,'force_N':1.,'omega_rad_s':math.sqrt(1000.),'valid_omega_range_rad_s':[1.,50.],'known_nonlinear_contact':False,'modal_measurement_evidence':None,'customer_approved':False,'engineering_validated':False}
def calc(d):
 if d.get('origin')!=base['origin']or d.get('configuration')!=base['configuration']or d.get('customer_approved')is not False or d.get('engineering_validated')is not False or d.get('modal_measurement_evidence')is not None:raise ValueError('configuration/provenance/validation unsupported')
 if type(d.get('known_nonlinear_contact'))is not bool:raise ValueError('explicit applicability boolean')
 if d['known_nonlinear_contact']:return {'status':'linear_model_not_applicable','engineering_pass':False,'next':'obtain actual contact/nonlinear model and evidence'}
 if d.get('valid_omega_range_rad_s')!=[1.,50.]:raise ValueError('unversioned validity range')
 vals=[d.get(k)for k in ['mass_kg','stiffness_N_m','damping_Ns_m','force_N','omega_rad_s']]
 if any(v is None for v in vals):return {'status':'model_or_excitation_unknown','engineering_pass':False}
 if any(type(v)not in(int,float)or not math.isfinite(v)or v<=0 for v in vals):raise ValueError('positive finite nonboolean quantities required')
 m,k,c,F,w=vals
 if not 1<=w<=50:return {'status':'outside_declared_model_band','engineering_pass':False}
 wn=math.sqrt(k/m);z=c/(2*math.sqrt(k*m));amp=F/math.hypot(k-m*w*w,c*w);static=F/k
 sensitivity={'domega_dk':wn/(2*k),'domega_dm':-wn/(2*m)};eps=.001;fd=(math.sqrt((k+eps)/m)-math.sqrt((k-eps)/m))/(2*eps);assert abs(fd-sensitivity['domega_dk'])<1e-8
 scan=[{'omega_rad_s':v,'response_m':F/math.hypot(k-m*v*v,c*v)}for v in range(1,51)]
 return {'status':'linear_response_research_only','natural_omega_rad_s':wn,'natural_frequency_Hz':wn/(2*math.pi),'damping_ratio':z,'static_displacement_m':static,'response_at_declared_excitation_m':amp,'dynamic_to_static_ratio':amp/static,'sensitivity':sensitivity,'finite_difference_domega_dk':fd,'frequency_scan':scan,'engineering_pass':False,'calibration':'not_measured','response_acceptance':None}
cases=[]
def add(n,d,e):
 r=calc(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常绑定工况',base,'linear_response_research_only')
x=copy.deepcopy(base);x['stiffness_N_m']=1000.;add('静刚度变好但接近共振冲突',x,'linear_response_research_only');assert cases[-1]['actual']['static_displacement_m']<cases[0]['actual']['static_displacement_m']and cases[-1]['actual']['response_at_declared_excitation_m']>cases[0]['actual']['response_at_declared_excitation_m']
x=copy.deepcopy(base);x['omega_rad_s']=None;add('缺激励不补零',x,'model_or_excitation_unknown')
x=copy.deepcopy(base);x['known_nonlinear_contact']=True;add('非线性接触不适用',x,'linear_model_not_applicable')
x=copy.deepcopy(base);x['omega_rad_s']=51.;add('模型频段边界外',x,'outside_declared_model_band')
for n,mut in [('零刚度',lambda d:d.update(stiffness_N_m=0)),('NaN频率',lambda d:d.update(omega_rad_s=float('nan'))),('换安装配置仍用旧模型',lambda d:d.update(configuration='different_mount')),('伪实测模态',lambda d:d.update(modal_measurement_evidence='measured_and_verified'))]:
 x=copy.deepcopy(base);mut(x)
 try:calc(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x['id']='DISPLAY-DYNAMICS-TEACH';x['mass_kg']=2.;add('展示机构另一情境',x,'linear_response_research_only')
for n,d in [('01-工况模型输入.json',base),('02-模态响应灵敏度实际复算.json',{'cases':cases,'count':len(cases),'measurement_plan':['define actual mounting/load/temperature','identify mass/stiffness/damping from independent measurements','measure excitation spectrum','compare transfer function and residual over declared band','rebuild for contact/nonlinear/time-varying regimes'],'actual_test_data':[]})]:(P/'教学包'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
