from pathlib import Path
import json,math,re,hashlib
ROOT=Path('/Volumes/邱懿武/邱懿武认知大脑/好设计平台');P=Path(__file__).parent;F=ROOT/'02-研究/ML-021-内容质量深化/function'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((F/'manifest.json').read_text());bad=[x['path'] for x in m['files'] if sha(F/x['path'])!=x['sha256']];assert not bad
rows=[]
def record(method,scope,values,ok):
 assert ok,(method,values)
 rows.append(dict(method_id=method,scope=scope,values=values,result='consistent_with_declared_example'))
# Independent elementary models, not imports of author assertions or scripts.
record('R21/R25','间隙与库仑代理',[10.6-10-2*.2,.4*5,.1*5],math.isclose(10.6-10-.4,.2) and .4*5>1>.1*5)
record('R22','局部材料质量及附件反例',[10*7.8+90*1.2+20,10*7.8+90*1.2+120],10*7.8+90*1.2+20<300<10*7.8+90*1.2+120)
record('R23/R28','时间分离及变更分支',[.1<=.2,.3>.2,.3<=.4],.1<=.2 and .3>.2 and .3<=.4)
record('R24','可用能量不等于力/轨迹证明',{'gross_J':1*10*.1,'usable_J':1*10*.1*.5,'margin_J':1*10*.1*.5-.2},math.isclose(1*10*.1*.5-.2,.3))
r=.5e-3;dp=2*.072/r;q=math.pi*r**4*dp/(8*.001*.1)*1e6
record('R27','维持压差的理想牛顿管流；非真实胶乳',{'pressure_Pa':dp,'flow_ml_s':q,'vertical_net_Pa':dp-1000*9.81*.1,'viscosity_10x_ml_s':q/10},q>.05 and q/10<.05 and dp<981)
record('R29','批量10选择V2，临界20平手',{'n10':[240,210,240],'n20':[480,390,390],'n30':[720,570,540]},18*10+30<min(24*10,15*10+90) and 18*20+30==15*20+90)
p1=2/2;p2=(4-.5*p1)/3
record('R30','三角映射顺序与超范围目标',{'p1':p1,'p2':p2,'reverse_order_displacement':.5+3*4/3,'8mm_p2':(8-.5)/3},math.isclose(.5*p1+3*p2,4) and (8-.5)/3>2)
edges={('A','B'),('B','A'),('B','C'),('C','D')};reach=set(edges)
for k in 'ABCD':
 for i in 'ABCD':
  for j in 'ABCD':
   if (i,k) in reach and (k,j) in reach:reach.add((i,j))
record('R31','独立可达闭包而非读取作者SCC',{'mutual_pairs':sorted((i,j) for i,j in reach if i!=j and (j,i) in reach)},set((i,j) for i,j in reach if i!=j and (j,i) in reach)=={('A','B'),('B','A')})
err=0
for d in range(30,151):
 a=(40*math.cos(math.radians(d)),40*math.sin(math.radians(d)));b=(a[0]+100,a[1]);err=max(err,abs(math.hypot(*a)-40),abs(math.hypot(b[0]-100,b[1])-40),abs(b[0]-a[0]-100))
record('R32','独立121点几何检查，非连续一般机构证明',{'points':121,'max_length_error_mm':err,'cross_180_in_150_210':True},err<1e-10)
mat={}
for name,E,rho,stress in [('A',70e9,2700,300e6),('B',210e9,7800,900e6)]:
 area=max(30/(E*.001),100/stress);b=max((4*100*.3**3/(E*.001))**.25,(180/stress)**(1/3));mat[name]={'axial_mass_kg':area*rho*.3,'beam_mass_kg':b*b*.3*rho}
record('R33','独立力学重算与控制项比较',mat,mat['B']['axial_mass_kg']<mat['A']['axial_mass_kg'] and mat['A']['beam_mass_kg']<mat['B']['beam_mass_kg'])
record('R34','装配动作和服务约束分别裁决',{'A_s':sum([4,4,2]),'B_s':sum([10,10]),'B2_s':sum([4,2,2]),'B_service_constraint':False},sum([4,2,2])<sum([4,4,2])<sum([10,10]))
w=1000**.5;amp=lambda m,k,c:1/((k-m*w*w)**2+(c*w)**2)**.5
record('WB04/WB06','同工况线性幅值；非原作者非线性算法',{'WB04_A':amp(2,1000,2),'WB04_B':amp(1,1000,2),'WB04_C':amp(1,2000,2),'WB06_k500':amp(1,500,2),'required_c_at_resonance':1/(.003*w)},amp(1,1000,2)>.003>amp(1,2000,2) and amp(1,1000,2)>amp(1,500,2))
res=0;clean=[];states=[]
for n in range(1,11):
 res+=1;states.append(res)
 if n in (3,6,9):res=0;clean.append(n)
record('WB05','逐次状态递推，不把10/3取整当依据',{'states_before_clean':states,'clean_after':clean,'total_s':10+2*len(clean)},max(states)<=3 and 10+2*len(clean)==16)
s=(P/'private-sources/matrix.html').read_text();cells=[]
for i,j,expect in [(14,1,[1,8,40,15]),(1,14,[28,27,18,40]),(14,2,[40,26,27,1]),(14,14,[])]:
 raw=re.search(rf'if\(principlesSelect1 == {i} && principlesSelect2 == {j}\) \{{ zasady = (\[[^\]]*\]); \}}',s).group(1)
 vals=[int(x) for x in re.findall(r'\d+',raw)];assert vals==expect;cells.append({'improving':i,'worsening':j,'principles':vals})
record('R22','官方原HTML四格独立定点读取，未做UI/历史版考证',{'source_sha':sha(P/'private-sources/matrix.html'),'cells':cells},sha(P/'private-sources/matrix.html')=='43b46003d45fc27face50c0e4dcd75c0b10dafed029beddfdadbfee46f362c35')
r35=json.loads((ROOT/'02-研究/方法深化执行/MD-035-R35/教学包/02-迭代敏感性与几何重分析.json').read_text());vals=[]
for c in r35['cases']:
 a=c['result'];vals.append({'label':c['label'],'final':a['final'],'binary':a['thresholded_reanalysis']})
record('R35','只读原数值记录与正文表，未重跑有限元优化器',vals,not vals[0]['final']['converged_design_change'] and vals[2]['final']['converged_design_change'] and vals[0]['binary']['volume_fraction']>.45 and vals[2]['binary']['compliance']>2e6)
# Datum arithmetic counted only as comparison, not utility.
A=(3,2);B=(2,4);C=(1,3);C2=(1,2)
sgn=lambda x,y:sum((b>a)-(b<a) for a,b in zip(x,y))
record('R36','逐准则相对符号与改版支配',{'B_vs_A':sgn(B,A),'C_vs_A':sgn(C,A),'C_vs_B':sgn(C,B),'C2_vs_A':sgn(C2,A)},sgn(B,A)==0 and sgn(C,A)==0 and sgn(C,B)==2 and C2[0]<A[0] and C2[1]==A[1])
(P/'独立复算记录.json').write_text(json.dumps({'reviewer':'needs independent Agent','scope':'content arithmetic/source extraction, not engineering validation','author_manifest_sha256':sha(F/'manifest.json'),'manifest_files_unchanged':len(m['files']),'checks':rows},ensure_ascii=False,indent=2))
print('independent groups',len(rows),'author files unchanged',len(m['files']))
