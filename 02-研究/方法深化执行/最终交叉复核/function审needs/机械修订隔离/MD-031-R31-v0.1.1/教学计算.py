# -*- coding: utf-8 -*-
from pathlib import Path
import json,copy
D=Path(__file__).resolve().parent;P=D/'教学包';P.mkdir(exist_ok=True)
def put(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
base={'origin':'constructed_task_information_model','objects':['A-reference-study','B-geometry-study','C-integration-study','D-test-plan'],'convention':'row_provides_to_column','dependency_type':'task_information','matrix':[[0,1,0,0],[1,0,1,0],[0,0,0,1],[0,0,0,0]],'edge_evidence':[{'from':0,'to':1,'basis':'constructed A output is B input'},{'from':1,'to':0,'basis':'constructed B feedback revises A'},{'from':1,'to':2,'basis':'constructed B output is C input'},{'from':2,'to':3,'basis':'constructed C output is D input'}],'interface_costs':None,'claim_physical_decoupling':False}
def examine(i):
 if i['origin']!=base['origin']or i['dependency_type']!='task_information':raise ValueError('wrong_model_type')
 if i['claim_physical_decoupling']or i['interface_costs']is not None:raise ValueError('unsupported_physical_or_cost_claim')
 names=i['objects'];N=len(names);A=i['matrix']
 if len(set(names))!=N or N==0 or len(A)!=N or any(len(r)!=N for r in A):raise ValueError('shape_or_identity')
 if i['convention']not in ['row_provides_to_column','row_receives_from_column']:raise ValueError('missing_direction')
 if any(v is not None and(type(v)is not int or v not in [0,1])for r in A for v in r):raise ValueError('invalid_entry')
 if any(type(e.get(k))is not int or not 0<=e[k]<N for e in i['edge_evidence']for k in ['from','to']):raise ValueError('edge_endpoint_strict_integer_id_required')
 E={(r,c)if i['convention']=='row_provides_to_column'else(c,r)for r in range(N)for c in range(N)if A[r][c]==1}
 evidence={(e['from'],e['to'])for e in i['edge_evidence']if e.get('basis')}
 if E!=evidence or len(evidence)!=len(i['edge_evidence']):raise ValueError('matrix_evidence_direction_mismatch')
 if any(not(0<=r<N and 0<=c<N)for r,c in E):raise ValueError('dangling_edge')
 R=[[a==b or(a,b)in E for b in range(N)]for a in range(N)]
 for k in range(N):
  for a in range(N):
   for b in range(N):R[a][b]=R[a][b]or(R[a][k]and R[k][b])
 unseen=set(range(N));groups=[]
 while unseen:
  a=min(unseen);g=sorted(b for b in unseen if R[a][b]and R[b][a]);groups.append(g);unseen-=set(g)
 gi={n:k for k,g in enumerate(groups)for n in g};CE={(gi[a],gi[b])for a,b in E if gi[a]!=gi[b]};pending=set(range(len(groups)));order=[]
 while pending:
  ready=sorted(k for k in pending if not any(b==k and a in pending for a,b in CE));assert ready
  order.extend(ready);pending-=set(ready)
 unknown=any(v is None for r in A for v in r)
 return {'edge_direction':'provider_to_recipient','SCC':[[names[k]for k in g]for g in groups],'condensation_edges':[list(e)for e in sorted(CE)],'known_graph_order':[[names[k]for k in groups[g]]for g in order],'complete_order':None if unknown else [[names[k]for k in groups[g]]for g in order],'unknown_relations':unknown,'interface_costs':None,'schedule_benefit':None,'physical_decoupling':False,'qualification':'graph calculation only; cyclic group needs iteration planning, not automatically a physical module'}
put('01-输入与边证据.json',base);out=examine(base);put('02-矩阵强连通与缩点.json',out)
checks=[]
def test(name,kind,mut,expect):
 q=copy.deepcopy(base);mut(q)
 try:o=examine(q);actual='unknown'if o['unknown_relations']else'accepted'
 except (ValueError,KeyError,TypeError)as e:o={'error':str(e)};actual='rejected'
 checks.append({'name':name,'class':kind,'input':q,'expected':expect,'actual':actual,'pass':actual==expect,'output':o})
def transpose(x):x['matrix']=[list(r)for r in zip(*x['matrix'])]
def equivalent(x):transpose(x);x['convention']='row_receives_from_column'
test('positive','正常',lambda x:None,'accepted');test('transpose_without_legend','冲突',transpose,'rejected');test('transpose_with_legend','边界',equivalent,'accepted');test('unknown_edge','缺材料',lambda x:x['matrix'][3].__setitem__(0,None),'unknown');test('missing_evidence','缺材料',lambda x:x['edge_evidence'].pop(),'rejected');test('physical_interface_mixed','不适用',lambda x:x.update(dependency_type='physical_contact'),'rejected');test('invent_interface_cost','冲突',lambda x:x.update(interface_costs=0),'rejected');test('bool_entry','冲突',lambda x:x['matrix'][0].__setitem__(1,True),'rejected')
assert all(x['pass']for x in checks);put('03-实际检查.json',checks)
put('04-另一情境迁移.json',{'context':'document research-review-publication','nodes':['author','reviewer','publisher'],'directed_edges':['author->reviewer','reviewer->author','reviewer->publisher'],'desktop_conclusion':'author/reviewer feedback pair precedes publication in declared graph','scope':'mapping only; not actual organizational productivity measurement','interface_costs':None,'physical_modules_claimed':False})
print(json.dumps({'checks':len(checks),'all_pass':True}))
