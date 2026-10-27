# -*- coding: utf-8 -*-
"""C/K relative-status and countermodel lesson, not a general formal CK theorem prover."""
from pathlib import Path
import copy,hashlib,json
B=Path(__file__).resolve().parent;P=B/'教学包';SP=B.parent/'MD-001-R48/教学包/00-共享教学输入-v0.1.0.json';SHA='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70';assert hashlib.sha256(SP.read_bytes()).hexdigest()==SHA
BIND={'problem_id':'TAP-TEACH-001','problem_version':'0.1.0','sha256':SHA,'use':'context_only_not_validated_requirement'}
data={'binding':BIND,'origin':'authored_finite_countermodel_not_tree_data','concept':{'id':'C0','proposition':'仅凭表面观测唯一识别隐藏状态，并满足待研究的完整用途','properties':['observe_surface','infer_hidden_uniquely','operate_safely'],'initial_status':'unresolved_relative_to_K0'},'K0':[{'id':'K-S1','scope':'proxy_model','statement':'已有一对象的表面观测记录','logical_status':'true_in_constructed_model'}],'additional_model_objects':[{'id':'O-A','surface':'SAME-SIGNAL','hidden':'H-A'},{'id':'O-B','surface':'SAME-SIGNAL','hidden':'H-B'}],'unknowns':['实际树体中信号与组织的关系','独立观测如何取得','操作安全与全用途'],'confirmed_design':False,'engineering_validated':False,'proposed_additional_observable_result':None}
def save(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2))
def check(d):
 if d.get('binding')!=BIND or d.get('origin')!='authored_finite_countermodel_not_tree_data':raise ValueError('context_or_origin_changed')
 if d.get('concept')!=data['concept']or d.get('K0')!=data['K0']:raise ValueError('concept_or_initial_knowledge_changed')
 if d.get('unknowns')!=data['unknowns']or d.get('confirmed_design')is not False or d.get('engineering_validated')is not False or d.get('proposed_additional_observable_result')is not None:raise ValueError('unsupported_conjunction_or_result')
 rows=d.get('additional_model_objects')
 if not isinstance(rows,list)or len(rows)<2:raise ValueError('insufficient_countermodel_objects')
 if len({r.get('id')for r in rows})!=len(rows):raise ValueError('duplicate_object')
 groups={}
 for r in rows:
  if set(r)!={'id','surface','hidden'}or any(not isinstance(r[k],str)or not r[k]for k in r):raise ValueError('object_identity_or_observation_missing')
  groups.setdefault(r['surface'],set()).add(r['hidden'])
 ambiguity={s:sorted(v)for s,v in groups.items()if len(v)>1}
 return {'binding':BIND,'K1_derivation':{'operator':'K_to_K','rule':'same observable symbol maps to multiple hidden symbols','ambiguous_observations':ambiguity,'surface_only_uniqueness':'refuted_in_constructed_countermodel'if ambiguity else'not_refuted_in_supplied_rows_not_proven_for_real_world'},'concept_status_change':{'C0':'not_confirmed; component uniqueness refuted in this model'if ambiguity else'unresolved_outside_supplied_rows','C1':'reformulated_with_additional_independent_information; unresolved','not_global_truth':'countermodel is authored, not evidence about actual tree tissue'},'property_ledger':[{'property':'observe_surface','status':'represented_in_proxy_model'},{'property':'infer_hidden_uniquely','status':'refuted_in_this_model'if ambiguity else'not_established_for_target'},{'property':'operate_safely','status':'unknown'}],'whole_design_confirmed':False,'next_K_questions':['什么独立信息能区分同表面不同隐藏状态','目标工况下能否获取且如何校核','完整用途还有哪些属性未获支持'],'physical_or_customer_claims':[]}
save('01-概念知识与有限模型输入.json',data);o=check(data);save('02-知识扩展与属性支持实际推演.json',o)
save('03-四类操作与一次重构.json',{'binding':BIND,'C_to_C':{'operation':'在仅表面与增加独立信息两个方向分割研究概念','result':'概念分割，不是已知解集合枚举'},'K_to_K':o['K1_derivation'],'C_to_K':{'operation':'用构造反模型给表面唯一性这一子命题确定否定状态','scope':'only a subclaim in this model; not finished engineering design'},'K_to_C':{'operation':'从观测歧义重构C1，提出需要独立信息的新属性','result':'new unresolved design concept'},'knowledge_before_after':['K0只有局部代理记录，不能证明全属性','K1加入同观测异状态反模型，限定子命题状态改变'],'original_theory_reconstruction':'selected introductory concepts only, no full axiomatic implementation'})
checks=[]
def probe(n,k,mut,expected):
 x=copy.deepcopy(data);mut(x)
 try:r=check(x);s='accepted'
 except ValueError as e:r={'error':str(e)};s='rejected'
 assert s==expected,(n,s);checks.append({'name':n,'class':k,'input':x,'expected':expected,'actual':s,'output':r})
probe('normal-countermodel','正常',lambda x:None,'accepted');assert checks[-1]['output']['K1_derivation']['ambiguous_observations']
probe('missing-model-object','缺材料',lambda x:x['additional_model_objects'].pop(),'rejected')
probe('proxy-as-tree-evidence','不适用',lambda x:x.update(origin='real_tree_measurement'),'rejected')
probe('partial-property-not-whole','边界',lambda x:x.update(confirmed_design=True),'rejected')
probe('duplicate-object','冲突',lambda x:x['additional_model_objects'].append(x['additional_model_objects'][0]),'rejected')
probe('different-signal-no-global-proof','边界',lambda x:x['additional_model_objects'][1].update(surface='OTHER-SIGNAL'),'accepted');assert checks[-1]['output']['whole_design_confirmed']is False
probe('unknown-safety-not-proven','冲突',lambda x:x.update(unknowns=[]),'rejected')
probe('future-calibration-result-invented','不适用',lambda x:x.update(proposed_additional_observable_result='works'),'rejected')
probe('swap-problem-context','冲突',lambda x:x['binding'].update(problem_id='OTHER'),'rejected')
probe('K0-logical-status-invented','边界',lambda x:x['K0'][0].update(logical_status='true_for_all_trees'),'rejected')
save('04-实际检查结果.json',{'executed':True,'passed':len(checks),'checks':checks,'real_experiments':0,'scope':'finite mapping arithmetic and fixed concept/status checks, not automatic CK design'})
t={'scenario':'DOC-CK-TEACH-001','origin':'constructed_desktop','objects':[{'display_name':'report','content_sha':'AAA'},{'display_name':'report','content_sha':'BBB'}],'question':'仅凭同名能否唯一识别版本','result':'存在同名异内容的构造反例；增加指纹是新的研究/实现要求，不自动证明权限和可靠交接','engineering_validated':False};assert t['objects'][0]['display_name']==t['objects'][1]['display_name']and t['objects'][0]['content_sha']!=t['objects'][1]['content_sha'];save('05-迁移桌面检查.json',t)
print(json.dumps({'method':'R20','tests':len(checks),'countermodel':o['K1_derivation']['ambiguous_observations'],'whole_design_confirmed':False},ensure_ascii=False))
