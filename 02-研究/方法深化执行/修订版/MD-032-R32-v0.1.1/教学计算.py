# -*- coding: utf-8 -*-
from pathlib import Path
import json,math,copy
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
def point(t):t=math.radians(t);return[40*math.cos(t),40*math.sin(t)]
base={'origin':'independent_planar_rigid_geometry_fixture','length_unit':'mm','angle_unit':'degree','topology':'four_bar_4R','poses':[{'input_deg':t,'A':point(t),'B':[point(t)[0]+100,point(t)[1]],'body_orientation_deg':0}for t in[30,90,150]],'tolerance_mm':1e-7,'scan_start':30,'scan_end':150,'scan_step_deg':1,'selected_branch':'parallelogram','switch_at_deg':None,'obstacle':{'center':[0,80],'radius_mm':5,'identity':'constructed_circle_not_actual_tree_or_person'},'physical_envelope_known':False,'engineering_pass':False}
def norm(x):return math.hypot(*x)
def sub(a,b):return[a[0]-b[0],a[1]-b[1]]
def center(pts):
 p,q,r=pts;a,b=[2*(q[j]-p[j])for j in range(2)];c,d=[2*(r[j]-p[j])for j in range(2)];u=sum(v*v for v in q)-sum(v*v for v in p);v=sum(z*z for z in r)-sum(z*z for z in p);det=a*d-b*c
 if abs(det)<1e-10:raise ValueError('collinear_three_position_points')
 return[(u*d-b*v)/det,(a*v-u*c)/det]
def circles(A,r,O,s):
 V=sub(O,A);d=norm(V)
 if d==0 or d>r+s+1e-9 or d<abs(r-s)-1e-9:raise ValueError('no_regular_circle_intersection')
 u=[v/d for v in V];a=(r*r-s*s+d*d)/(2*d);h=math.sqrt(max(0,r*r-a*a));M=[A[j]+a*u[j]for j in range(2)]
 return[[M[0]-h*u[1],M[1]+h*u[0]],[M[0]+h*u[1],M[1]-h*u[0]]]
def segment_distance(C,A,B):
 V=sub(B,A);den=sum(v*v for v in V);t=max(0,min(1,sum(sub(C,A)[j]*V[j]for j in range(2))/den))if den else 0;return norm(sub(C,[A[j]+t*V[j]for j in range(2)]))
def examine(i):
 if i['origin']!=base['origin']or i['topology']!='four_bar_4R':raise ValueError('unsupported_topology_or_origin')
 if i['length_unit']!='mm'or i['angle_unit']!='degree':raise ValueError('units')
 if i['engineering_pass']or i['physical_envelope_known']:raise ValueError('unsupported_physical_claim')
 if i['tolerance_mm']!=base['tolerance_mm']or i['obstacle']!=base['obstacle']:raise ValueError('fixed_tolerance_or_obstacle_changed')
 if len(i['poses'])!=3:raise ValueError('need_three_poses')
 for p in i['poses']:
  if type(p.get('input_deg'))not in(int,float)or not math.isfinite(p['input_deg'])or any(type(x)not in(int,float)or not math.isfinite(x)for x in p['A']+p['B']):raise ValueError('pose_numeric')
  if norm(sub(p['A'],point(p['input_deg'])))>1e-7 or norm(sub(sub(p['B'],p['A']),[100,0]))>1e-7 or p['body_orientation_deg']!=0:raise ValueError('fixed_pose_constraint_conflict')
 O1=center([p['A']for p in i['poses']]);O2=center([p['B']for p in i['poses']]);r=norm(sub(i['poses'][0]['A'],O1));s=norm(sub(i['poses'][0]['B'],O2));c=norm(sub(i['poses'][0]['B'],i['poses'][0]['A']))
 start,end,step=i['scan_start'],i['scan_end'],i['scan_step_deg']
 if any(type(v)not in(int,float)or not math.isfinite(v)for v in [start,end,step])or step<=0 or end<start or step>1 or end-start>360:raise ValueError('invalid_scan_range')
 if i['selected_branch']!='parallelogram':raise ValueError('unsupported_branch')
 rows=[];toggle=[];minclear=float('inf')
 count=math.ceil((end-start)/step)
 for k in range(count+1):
  t=min(end,start+k*step);A=point(t);solutions=circles(A,c,O2,s);expected=[A[0]+100,A[1]];idx=min(range(2),key=lambda j:norm(sub(solutions[j],expected)));other=solutions[1-idx];B=solutions[idx]
  if i['switch_at_deg']is not None and t>=i['switch_at_deg']:B=other
  jac=abs(math.sin(math.radians(t)));acute=math.degrees(math.asin(min(1,jac)))
  if jac<1e-8:toggle.append(t)
  clear=min(segment_distance(i['obstacle']['center'],a,b)-i['obstacle']['radius_mm']for a,b in [(O1,A),(A,B),(B,O2),(O2,O1)]);minclear=min(minclear,clear)
  rows.append({'input_deg':t,'A':A,'B':B,'two_assembly_solutions':solutions,'normalized_loop_jacobian':jac,'acute_transmission_angle_deg':acute,'obstacle_clearance_line_model_mm':clear})
 branchjump=i['switch_at_deg']is not None
 result={'synthesized_pivots_mm':[O1,O2],'link_lengths_mm':{'ground':norm(sub(O2,O1)),'crank':r,'coupler':c,'rocker':s},'generic_DOF_count':3*(4-1)-2*4,'DOF_caveat':'generic count; singular configurations require local constraint analysis','three_pose_residual_max_mm':max(abs(norm(sub(p['A'],O1))-r)for p in i['poses']),'scan':rows,'sample_count':len(rows),'singular_angles_detected_deg':toggle,'min_acute_transmission_deg':min(z['acute_transmission_angle_deg']for z in rows),'min_constructed_obstacle_clearance_mm':minclear,'branch_switch_requested':branchjump,'sampled_path_status':'reject_toggle_or_branch_switch'if toggle or branchjump else'sampled_geometry_only_no_certificate','real_collision_clearance':'unknown','continuous_no_singularity_proof':False,'engineering_pass':False}
 return result
put('01-三位姿与约束输入.json',base);put('02-尺寸分支与扫描.json',examine(base))
checks=[]
def test(name,kind,mut,expect):
 q=copy.deepcopy(base);mut(q)
 try:o=examine(q);actual=o['sampled_path_status']
 except(ValueError,KeyError,TypeError)as e:o={'error':str(e)};actual='rejected'
 checks.append({'name':name,'class':kind,'input':q,'actual':actual,'expected':expect,'pass':actual==expect,'summary':{k:v for k,v in o.items()if k!='scan'}})
test('normal_three_pose_and_scan','正常',lambda x:None,'sampled_geometry_only_no_certificate')
test('three_pose_but_toggle_between','边界',lambda x:x.update(scan_start=150,scan_end=210),'reject_toggle_or_branch_switch')
test('three_pose_but_branch_jump','冲突',lambda x:x.update(switch_at_deg=90),'reject_toggle_or_branch_switch')
test('missing_pose','缺材料',lambda x:x['poses'].pop(),'rejected')
test('unsupported_spatial_topology','不适用',lambda x:x.update(topology='spatial_6R'),'rejected')
test('unit_mismatch','冲突',lambda x:x.update(length_unit='m'),'rejected')
test('claim_real_envelope','缺材料',lambda x:x.update(physical_envelope_known=True),'rejected')
test('coarse_scan','边界',lambda x:x.update(scan_step_deg=100),'rejected')
test('pose_inconsistent','冲突',lambda x:x['poses'][1]['B'].__setitem__(1,45),'rejected')
assert all(z['pass']for z in checks);put('03-实际检查.json',checks)
put('04-另一情境迁移.json',{'context':'folding display tray orientation','possible_topology':'planar parallelogram fourbar','shared_property':'ideal coupler orientation remains constant on chosen branch away from toggle','differences':['payload','thickness','pinch envelope','support stiffness','travel limits'],'engineering_pass':False,'actual_scope':'desk kinematic analogy only; no prototype or safety experiment'})
print(json.dumps({'checks':len(checks),'all_pass':True,'normal_samples':121}))
