"""Authored graph-transformation lesson; not 77-card reproduction or automatic creativity scoring."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包'
SHARED=B.parent/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json';SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70';assert hashlib.sha256(SHARED.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','problem_version':'0.1.0','sha256':SHA,'use':'context_only_not_validated_engineering_input'}
BASE_EDGES=[['structure','reference','supports'],['structure','actuator','supports'],['reference','actuator','reference_signal']]
HINTS={'OWN-H1':'分离可替换的参考模块：平台自写操作提示，不是官方卡号','OWN-H2':'把单一作用点展开为分布接触：平台自写提示','OWN-H3':'只改变外观标识：作为机制不变反例'}
data={'binding':BIND,'origin':'authored_teaching_graphs','baseline':{'id':'BASE-01','function':'研究参考与作用的关系','edges':BASE_EDGES},'variants':[{'id':'V-SEPARATE','hint_id':'OWN-H1','parent':'BASE-01','edges':[['structure','module','supports'],['module','reference','supports'],['structure','actuator','supports'],['reference','actuator','reference_signal']],'declared_hard_state':'unknown','engineering_validated':False},{'id':'V-DISTRIBUTE','hint_id':'OWN-H2','parent':'BASE-01','edges':BASE_EDGES+[['actuator','contactA','acts_on'],['actuator','contactB','acts_on']],'declared_hard_state':'unknown','engineering_validated':False},{'id':'V-COSMETIC','hint_id':'OWN-H3','parent':'BASE-01','edges':BASE_EDGES,'appearance':'different_color','declared_hard_state':'unknown','engineering_validated':False}],'hint_catalog':HINTS,'engineering_recommendation':None,'physical_results':[]}
def save(n,x):(P/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
def check(d):
 if d.get('binding')!=BIND or d.get('origin')!='authored_teaching_graphs':raise ValueError('context_or_origin_mismatch')
 if d.get('hint_catalog')!=HINTS:raise ValueError('hint_identity_or_scope_changed')
 if d.get('engineering_recommendation')is not None or d.get('physical_results'):raise ValueError('engineering_result_invented')
 if d.get('baseline',{}).get('id')!='BASE-01'or d['baseline'].get('edges')!=BASE_EDGES:raise ValueError('baseline_changed')
 vv=d.get('variants');
 if not isinstance(vv,list)or not vv:raise ValueError('no_variants')
 if len({v['id']for v in vv})!=len(vv):raise ValueError('duplicate_variant_id')
 out=[];base={tuple(e)for e in BASE_EDGES}
 for v in vv:
  if v.get('parent')!='BASE-01'or v.get('hint_id')not in HINTS:raise ValueError('variant_lineage_not_closed')
  if v.get('engineering_validated')is not False or v.get('declared_hard_state')not in ['unknown','fail']:raise ValueError('unsupported_hard_pass_or_validation')
  if not isinstance(v.get('edges'),list)or any(not isinstance(e,list)or len(e)!=3 or any(not isinstance(z,str)or not z for z in e)for e in v['edges']):raise ValueError('edge_shape_invalid')
  g={tuple(e)for e in v['edges']}
  if len(g)!=len(v['edges']):raise ValueError('duplicate_edge')
  delta={'added':[list(x)for x in sorted(g-base)],'removed':[list(x)for x in sorted(base-g)]}
  changed=g!=base;state='excluded_by_declared_teaching_hard_fail'if v['declared_hard_state']=='fail'else'mechanism_graph_changed_research_only'if changed else'no_mechanism_change_in_declared_graph'
  out.append({'variant':v['id'],'hint':v['hint_id'],'delta':delta,'state':state,'physical_feasibility':'unknown','novelty_or_value_score':None})
 return {'binding':BIND,'trace':out,'changed_graphs':sum(bool(r['delta']['added']or r['delta']['removed'])for r in out),'engineering_candidates':[],'scope':'graph difference under authored labels, not physical causality, creativity quality or product novelty'}
save('01-基线提示与变体输入.json',data);out=check(data);save('02-变换链与筛除输出.json',out)
save('03-完整研究交接.json',{'binding':BIND,'keep':['V-SEPARATE','V-DISTRIBUTE'],'keep_scope':'仅保留两种不同图关系继续研究，不是工程选优','not_counted_as_new_mechanism':['V-COSMETIC'],'open_interfaces':['模块连接与重复定位','接触分配和污染','状态可观测性与异常恢复'],'next_methods':['R17组织可组合选项','R36按证据比较','R44研究危险假设'],'no_customer_targets':True})
checks=[]
def probe(n,k,mut,expected):
 a=copy.deepcopy(data);mut(a)
 try:r=check(a);s='accepted'
 except ValueError as e:r={'error':str(e)};s='rejected'
 assert s==expected,(n,s)
 checks.append({'name':n,'class':k,'input':a,'expected':expected,'actual':s,'output':r})
probe('normal-three-variants','正常',lambda x:None,'accepted')
probe('missing-baseline','缺材料',lambda x:x.pop('baseline'),'rejected')
probe('claim-real-engineering','不适用',lambda x:x['variants'][0].update(engineering_validated=True),'rejected')
probe('cosmetic-not-new-mechanism','边界',lambda x:x.update(variants=[x['variants'][2]]),'accepted');assert checks[-1]['output']['changed_graphs']==0
probe('explicit-hard-fail','冲突',lambda x:x['variants'][0].update(declared_hard_state='fail'),'accepted');assert checks[-1]['output']['trace'][0]['state']=='excluded_by_declared_teaching_hard_fail'
probe('unregistered-hint','缺材料',lambda x:x['variants'][0].update(hint_id='official-card-999'),'rejected')
probe('wrong-parent','冲突',lambda x:x['variants'][0].update(parent='OTHER'),'rejected')
probe('duplicate-variant','边界',lambda x:x['variants'].append(x['variants'][0]),'rejected')
probe('unknown-not-pass','冲突',lambda x:x['variants'][0].update(declared_hard_state='pass'),'rejected')
probe('no-ranking','不适用',lambda x:x.update(engineering_recommendation='V-SEPARATE'),'rejected')
save('04-实际检查结果.json',{'executed':True,'checks':checks,'passed':len(checks),'field_trials':0,'official_card_library_reproduced':False})
t={'scenario':'DOC-GRAPH-TEACH-001','origin':'constructed_desktop','baseline_edges':[['record','recipient','direct_transfer']],'variant_edges':[['record','version_index','indexed'],['version_index','recipient','lookup']],'cosmetic_edges':[['record','recipient','direct_transfer']],'physical_or_user_results':[]}
t['mechanism_graph_difference']=set(map(tuple,t['variant_edges']))!=set(map(tuple,t['baseline_edges']));t['cosmetic_graph_difference']=set(map(tuple,t['cosmetic_edges']))!=set(map(tuple,t['baseline_edges']));assert t['mechanism_graph_difference']and not t['cosmetic_graph_difference'];save('05-迁移桌面检查.json',t)
print(json.dumps({'method':'R19','tests':len(checks),'changed_graphs':out['changed_graphs'],'engineering_candidates':[]},ensure_ascii=False))
