from pathlib import Path
import json,math,hashlib,re
p=Path(__file__).parent
out=[]
def rec(i,name,inputs,result,checks):
 assert all(checks.values()),(i,name,checks)
 out.append({'method_id':i,'example':name,'provenance':'explicit_assumption_constructed_not_measured_or_customer_approved','input':inputs,'computed':result,'checks':checks})
rec('R22','局部材料质量',{'steel_cm3':10,'polymer_cm3':90,'fixture_g':20}, {'mass_g':10*7.8+90*1.2+20},{'under300g':206<300})
rec('R23','转换窗口',{'force_push_N':12,'force_release_N':.5,'transition_s':.1,'window_s':.2},{'margin_s':.1},{'push':12>=10,'release':.5<=1,'window':.1<=.2})
rec('R24','下降资源',{'m_kg':1,'g_m_s2':10,'h_m':.1,'eta':.5,'required_J':.2},{'available_J':.5,'margin_J':.3},{'energy':.5>.2,'time':.4<=1})
r=.0005;gamma=.072;mu=.001;L=.1;dp=2*gamma/r;Q=math.pi*r**4*dp/(8*mu*L)
rec('R27','理想流体迁移',{'r_m':r,'gamma_N_m':gamma,'mu_Pa_s':mu,'L_m':L}, {'capillary_Pa':dp,'Q_m3_s':Q,'Q_mL_s':Q*1e6,'vertical_01m_Pa':981},{'target':Q*1e6>.05,'upright_fails':981>dp,'viscosity10x_fails':Q*1e5<.05})
rec('R29','批量反转',{'n':[5,10,30]},{str(n):[24*n,18*n+30,15*n+90] for n in [5,10,30]},{'n10V2':210<240,'n30V3':540<570})
rec('R30','顺序调节',{'p1':1,'p2':7/6},{'F1_N':2,'F2_mm':.5+3*(7/6),'wrong_F2_mm':.5+3*4/3},{'target':math.isclose(.5+3*7/6,4),'within':7/6<=2})
pts=[{'theta_deg':t,'A_mm':[40*math.cos(math.radians(t)),40*math.sin(math.radians(t))],'B_mm':[40*math.cos(math.radians(t))+100,40*math.sin(math.radians(t))]} for t in [30,90,150]]
rec('R32','平行四边形',{'links_mm':[100,40,100,40]},pts,{'side_lengths':all(math.isclose(math.hypot(*q['A_mm']),40) for q in pts),'horizontal':all(math.isclose(q['A_mm'][1],q['B_mm'][1]) for q in pts)})
materials={'A':(70e9,2700,300e6),'B':(210e9,7800,900e6)};rr={}
for k,(E,rho,sig) in materials.items():
 area=max(100*.3/(E*.001),100/sig);b=max((4*100*.3**3/(E*.001))**.25,(6*100*.3/sig)**(1/3));rr[k]={'axial_area_m2':area,'axial_mass_kg':rho*area*.3,'beam_side_m':b,'beam_mass_kg':rho*b*b*.3}
rec('R33','材料排名反转',{'F_N':100,'L_m':.3,'delta_m':.001},rr,{'axial_B':rr['B']['axial_mass_kg']<rr['A']['axial_mass_kg'],'beam_A':rr['A']['beam_mass_kg']<rr['B']['beam_mass_kg']})
rec('R34','动作时',{'A':[4,4,2],'B':[10,10],'B2':[4,2,2]},{'A_s':10,'B_s':20,'B2_s':8},{'B2_faster':8<10<20})
w=math.sqrt(1000);amp=lambda m,k,c:1/math.sqrt((k-m*w*w)**2+(c*w)**2)
rec('WB04','共同参数冲突',{'omega_rad_s':w,'F_N':1,'c_Ns_m':2},{'A_m':amp(2,1000,2),'B_m':amp(1,1000,2),'C_m':amp(1,2000,2)},{'B_fails':amp(1,1000,2)>.003,'C_meets':amp(1,2000,2)<.003})
rec('WB05','清理支撑',{'cycles':10,'residue_increment':1,'limit':3,'clean_s':2},{'clean_after':[3,6,9],'total_s':16},{'no_clean_fails':4>3,'schedule':max([1,2,3,1,2,3,1,2,3,1])<=3})
rec('WB06','增刚共振',{'m_kg':1,'c_Ns_m':2,'omega':w},{str(k):{'static_m':1/k,'omega_n':math.sqrt(k),'zeta':1/math.sqrt(k),'X_m':amp(1,k,2)} for k in [500,1000,2000]},{'B_worse':amp(1,1000,2)>amp(1,500,2),'C_meets':amp(1,2000,2)<.003})
(p/'示例/本轮构造算例实际复算.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
# one source map per draft: original evidence clauses and baseline identity, never source full text
au=json.loads((p/'质量缺口台账.json').read_text());maps=[];dim=[]
for item in au['items']:
 i=item['method_id'];f=p/'稿件'/f'{i}.md';s=f.read_text();lines=s.splitlines();head=[{'line':n,'heading':l} for n,l in enumerate(lines,1) if l.startswith('#')];ev=[{'line':n,'text':l} for n,l in enumerate(lines,1) if l.startswith('E') or l.startswith('P4/7/9')]
 maps.append({'method_id':i,'draft':str(f.relative_to(p)),'baseline':item['baseline'],'baseline_manifest_sha256':item['manifest_sha256'],'key_claim_source_locators':ev,'source_vs_adaptation':'本文证据项绑定的作者/机构主张与教学构造分开；数值/例子/编排/图非作者实测','read_scope':'selected original sections; detailed text locators in evidence clauses; no whole-monograph claim'})
 d={k:{'assessment':'局部' if (i in ['WB01','WB02','WB03','WB04','WB05'] and k=='机制及前提') else '充分','locations':head,'note':'作者自查，待独立逐项内容审核；充分仅针对本文声明的受限范围，不作专家认证'} for k in ['身份边界与邻近法','机制及前提','判断回返与操作','完整构造或公开例','实质失败与迁移','来源与适配区分','可读性与交接']}
 dim.append({'method_id':i,'dimensions':d})
 item['status']='authored_candidate_pending_independent_content_review'
(p/'来源与逐主张定位.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2));(p/'七维作者自查.json').write_text(json.dumps(dim,ensure_ascii=False,indent=2));(p/'质量缺口台账.json').write_text(json.dumps(au,ensure_ascii=False,indent=2))
