"""Version-bound categorical mapping, not automatic need priority or real user classification."""
from pathlib import Path
import copy,hashlib,itertools,json,collections
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OUT=P/'教学包';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):p=OUT/n;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return p
SH=ROOT/'02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json';shared=json.loads(SH.read_text());assert sha(SH)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
upstream={'problem_id':shared['problem_id'],'version':shared['version'],'sha256':sha(SH),'review_state':'first_batch_changes_requested_not_expert_approved'}
doc_context={'problem_id':'DOC-KANO-TEACH-001','version':'0.1.0','scope':'independent constructed document-version visibility feature; no real participant'}
docp=save('06-独立文档情境输入.json',doc_context)
doc_binding={'problem_id':doc_context['problem_id'],'version':doc_context['version'],'sha256':sha(docp),'review_state':'constructed_not_expert_approved'}
ANS=['like','must_be','neutral','live_with','dislike'];TABLE=[['Q','A','A','A','O'],['R','I','I','I','M'],['R','I','I','I','M'],['R','I','I','I','M'],['R','R','R','R','Q']]
registry=json.loads((P/'来源取得记录.json').read_text());source=next(x for x in registry if x['id']=='JSSD-2014');raw=P/source['raw'];assert sha(raw)==source['sha256']
matrix={'matrix_version':'JSSD2014-table2-transcription-v1','source_title':'Hwang, Tsai, Mitsuhashi, Miyazaki (2014), THE APPLICATION OF KANO MODEL ON EXPLORING THE ATTRACTIVE ATTRIBUTES OF COMMUNITY CULTURE PRODUCTS','source_url':source['url'],'source_sha256':sha(raw),'locator':'PDF page4 / printed page30 / Table2','scope':'selected empirical-paper table version, NOT original 1984 full-text reconstruction','orientation':{'rows':'functional/presence','columns':'dysfunctional/absence'},'answer_order':ANS,'cells':TABLE,'labels':{'A':'attractive','O':'one_dimensional','M':'must_be','I':'indifferent','R':'reverse','Q':'questionable'},'visual_transcription_check':'author Agent viewed rendered PDF page4; independent check pending','text_table_discrepancy':'nearby prose says five questionable combinations, displayed Table2 has two Q cells; implementation follows this displayed Table2, not the inconsistent prose'}
mp=save('00-分类矩阵版本.json',matrix);MATRIX_SHA=sha(mp)
question={'feature_id':'K-T01','feature_version':'0.1.0','need_id':'N-T03','description':'作业状态信息可见（研究特性假设）','functional':'若提供这项作业状态信息，你感觉如何？','dysfunctional':'若不提供这项作业状态信息，你感觉如何？','single_feature':True,'questionnaire_language':'Chinese platform wording not source-validated translation','comprehension_pretest':'not_performed','customer_approved':False,'real_responses':[]}
save('01-问卷草稿与未知.json',{'problem_id':shared['problem_id'],'source_binding':upstream,'question':question,'outcome':'requires_real_pretest_and_sampling; no Kano class for this client feature','safety_or_mandatory_requirements':'not determined by Kano preferences'})
fixture={'schema':'kano-table-fixture-0.1.0','mode':'constructed_answer_pairs_only','source_binding':upstream,'matrix_version':matrix['matrix_version'],'matrix_sha256':MATRIX_SHA,'orientation':matrix['orientation'],'single_feature':True,'comprehension_scope':'declared_for_test_not_actual_pretest','safety_override_requested':False,'pairs':[{'id':f'PAIR-{i+1:02d}','functional':a,'dysfunctional':b,'segment':'matrix_coverage_not_person_sample','provenance':'synthetic_rule_coverage'}for i,(a,b)in enumerate(itertools.product(ANS,ANS))]}
save('02-全回答对夹具.json',fixture)
def classify(d):
 if d.get('mode')!='constructed_answer_pairs_only':raise ValueError('unsupported_real_survey_mode')
 if d.get('source_binding')not in [upstream,doc_binding]:raise ValueError('upstream_identity_mismatch')
 if d.get('matrix_version')!=matrix['matrix_version']or d.get('matrix_sha256')!=MATRIX_SHA or d.get('orientation')!=matrix['orientation']:raise ValueError('matrix_version_hash_or_orientation_mismatch')
 if d.get('single_feature')is not True:raise ValueError('compound_feature_requires_research')
 if d.get('safety_override_requested'):raise ValueError('kano_cannot_override_hard_requirement')
 ids=set();result=[]
 for r in d['pairs']:
  if r['id']in ids:raise ValueError('duplicate_response_id')
  ids.add(r['id'])
  if r.get('provenance')!='synthetic_rule_coverage':raise ValueError('response_not_constructed')
  a,b=r.get('functional'),r.get('dysfunctional')
  if a is None or b is None:result.append({'id':r['id'],'category':None,'disposition':'incomplete_do_not_impute'});continue
  if a not in ANS or b not in ANS:raise ValueError('invalid_answer')
  c=TABLE[ANS.index(a)][ANS.index(b)];result.append({'id':r['id'],'category':c,'disposition':'recheck_question_or_opposing_preference'if c in {'Q','R'}else'table_mapping_only','segment':r['segment']})
 return {'matrix_version':matrix['matrix_version'],'mappings':result,'meaning':'categorical rule coverage, not frequency in people or priority scores','safety_or_mandatory_status_changed':False,'customer_conclusions':[]}
normal=classify(fixture);save('03-完整分类输出.json',normal);assert len(normal['mappings'])==25
counts=dict(collections.Counter(x['category']for x in normal['mappings']));assert counts=={'Q':2,'A':3,'O':1,'R':7,'I':9,'M':3}
save('04-规则覆盖与解释.json',{'coverage_counts_not_survey_counts':counts,'all_25_pairs_exercised':True,'questionable_policy':'保留并复核题意，不填成无差异或删除后宣称全有效','reverse_policy':'核解释及分群，不能自动反向设计','mixed_segment_policy':'本轮没有真实细分人群结果，不能把夹具分组当客户人群','satisfaction_coefficients':'not_computed_without_valid_respondent_dataset','priority_scores':'not_created'})
tests=[]
def run(name,cat,x,expect):
 p=save('检查输入-'+name+'.json',x)
 try:o=classify(x);actual='accepted'
 except Exception as e:o={'error':str(e)};actual='rejected'
 assert actual==expect,(name,actual);tests.append({'id':name,'category':cat,'expected':expect,'actual':actual,'input':p.name,'input_sha256':sha(p),'output':o})
run('normal-all25','normal',fixture,'accepted')
a=copy.deepcopy(fixture);a['pairs'][0]['functional']=None;run('missing-answer-not-neutral','missing',a,'accepted');assert tests[-1]['output']['mappings'][0]['category']is None
for name,cat,mut in [('unsupported-production-survey','not_applicable',lambda a:a.update(mode='real_survey_conclusions')),('compound-feature','boundary',lambda a:a.update(single_feature=False)),('orientation-swapped','conflict',lambda a:a.update(orientation={'rows':'dysfunctional/absence','columns':'functional/presence'})),('version-mismatch','conflict',lambda a:a.update(matrix_version='KANO1984-original')),('invalid-answer','boundary',lambda a:a['pairs'][0].update(functional='probably')),('safety-override','not_applicable',lambda a:a.update(safety_override_requested=True)),('duplicate-response','conflict',lambda a:a['pairs'].append(a['pairs'][0]))]:
 a=copy.deepcopy(fixture);mut(a);run(name,cat,a,'rejected')
# Different feature context, same explicit mapping rules; no true participant assertions.
a=copy.deepcopy(fixture);a['source_binding']=doc_binding;a['pairs']=[{'id':'DOC-P1','functional':'like','dysfunctional':'neutral','segment':'document_case','provenance':'synthetic_rule_coverage'},{'id':'DOC-P2','functional':'dislike','dysfunctional':'like','segment':'document_case','provenance':'synthetic_rule_coverage'}];run('document-feature-mapping','transfer',a,'accepted');assert [x['category']for x in tests[-1]['output']['mappings']]==['A','R']
save('05-反例与迁移实际检查.json',{'script_sha256':sha(Path(__file__)),'tests':tests,'passed':len(tests),'not_claimed':['real pretest','population proportions','automatic text understanding','cross-industry validity']})
print('R11 25 answer-pair mappings and',len(tests),'checks; no customer category/score inferred')
