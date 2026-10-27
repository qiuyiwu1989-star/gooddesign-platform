from pathlib import Path
import json,copy
P=Path(__file__).resolve().parent
KEYS={'DO','DI','DE','DP','DC','DM','DA'}
EDGES=[('DO','DE'),('DE','DM'),('DI','DM'),('DM','DP'),('DP','DC'),('DC','DA'),('DO','DA')]
base={'id':'WB03-PLAN-TEACH-001','origin':'platform_relationship_fixture_not_author_algorithm','domains':{'DO':'研究指定任务在目标环境下的作用与维护负担','DI':'保留未知、少干预而不牺牲必要作用','DE':'户外污物和工况需取证','DP':'先补证再比较，未执行现场步骤','DC':'作用头/恢复/维护接口研究','DM':'候选方法不依赖已知不存在的洁净设施','DA':'验证应针对目标环境和目标作用'},'relations':[{'from':a,'to':b,'basis':'authored research dependency, not source-prescribed graph'}for a,b in EDGES],'target_context':'field','validation_plan_context':'field','cleanroom_available':False,'method_requires_cleanroom':False,'maintenance_frequency':None,'acceptance_target':None,'customer_approved':False,'engineering_validated':False,'unknowns':['actual field conditions','maintenance workload','accepted performance thresholds']}
def check(d):
 if d.get('origin')!='platform_relationship_fixture_not_author_algorithm'or d.get('customer_approved')is not False or d.get('engineering_validated')is not False:raise ValueError('scope/approval')
 if type(d.get('domains'))is not dict or set(d['domains'])!=KEYS or any(type(v)is not str or not v.strip()for v in d['domains'].values()):return {'status':'missing_planning_domain','ready':False}
 rel=d.get('relations')
 if type(rel)is not list or len(rel)!=len(EDGES)or {(r.get('from'),r.get('to'))for r in rel}!=set(EDGES)or any(not r.get('basis')for r in rel):return {'status':'missing_relationship_review','ready':False}
 if any(type(d.get(k))is not bool for k in ['cleanroom_available','method_requires_cleanroom']):raise ValueError('explicit context capability booleans required')
 if d['method_requires_cleanroom']and not d['cleanroom_available']:return {'status':'environment_method_conflict','ready':False,'revision':'change method or substantiate provision/goal change; no silent environment substitution'}
 if d.get('target_context')not in ['field','document_repository']or d.get('validation_plan_context')!=d['target_context']:return {'status':'goal_verification_context_conflict','ready':False}
 if d.get('unknowns')!=base['unknowns']or d.get('maintenance_frequency')is not None or d.get('acceptance_target')is not None:raise ValueError('unknowns/targets changed without new evidence')
 return {'status':'declared_relationships_consistent_only','ready':False,'unresolved':d['unknowns'],'quality_validated':False,'not_checked':'free text semantics and actual operational feasibility'}
cases=[]
def add(n,d,e):
 r=check(d);assert r['status']==e;cases.append({'name':n,'input':d,'actual':r,'passed':True})
add('正常关系研究仍未验证',base,'declared_relationships_consistent_only')
x=copy.deepcopy(base);x['domains'].pop('DA');add('缺质量检验域',x,'missing_planning_domain')
x=copy.deepcopy(base);x['relations']=[];add('七框填满无关系不适用',x,'missing_relationship_review')
x=copy.deepcopy(base);x['method_requires_cleanroom']=True;add('野外依赖洁净冲突',x,'environment_method_conflict')
x=copy.deepcopy(base);x['validation_plan_context']='lab';add('实验室计划冒目标环境边界',x,'goal_verification_context_conflict')
for n,mut in [('无证据维护次数填零',lambda d:d.update(maintenance_frequency=0)),('未知删除',lambda d:d.update(unknowns=[])),('伪工程验证',lambda d:d.update(engineering_validated=True))]:
 x=copy.deepcopy(base);mut(x)
 try:check(x);raise AssertionError(n+' accepted')
 except ValueError as e:cases.append({'name':n,'actual':'rejected','reason':str(e),'passed':True})
x=copy.deepcopy(base);x.update(id='DOC-PLAN-TEACH',target_context='document_repository',validation_plan_context='document_repository');x['domains']['DO']='研究资料来源和版本可核对';x['domains']['DE']='资料库权限和版本环境待核';add('资料规划不同情境',x,'declared_relationships_consistent_only')
for n,d in [('01-七域关系输入.json',base),('02-冲突修订实际检查.json',{'cases':cases,'count':len(cases),'revision_example':'洁净依赖冲突可返回DM改变候选，或回DO/DE补证；不是自动批准购设施或改目标'})]:(P/'教学包'/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
print(len(cases),'passed')
