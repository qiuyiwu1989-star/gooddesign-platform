"""Bounded lead-user screening of explicitly constructed evidence; not field qualification."""
from pathlib import Path
import copy,hashlib,json
P=Path(__file__).resolve().parent;ROOT=P.parents[2];OUT=P/'教学包';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):p=OUT/n;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');return p
S=ROOT/'02-研究/方法深化执行/MD-001-R48/教学包/00-共享教学输入-v0.1.0.json';shared=json.loads(S.read_text());assert sha(S)=='c9d262d505656bcaf6c76edee99e3615440f5e2d1c6ef4067e9c1b15a2ddcd70'
binding={'path':str(S.relative_to(ROOT)),'problem_id':shared['problem_id'],'version':shared['version'],'sha256':sha(S),'upstream_review':'first_batch_changes_requested_not_expert_approved'}
assumptions=[{'id':'A-TREND','text':'仅为练习假定：多数普通用户尚未面对的复杂条件持续作业需求趋势，不声称真实市场存在或增长。'}, {'id':'A-A','text':'虚构A名气大、购买早，但本趋势领先=false、显著收益=false。'}, {'id':'A-B','text':'虚构B在假定趋势上领先=true、显著收益=true，未自行开发产品。'}, {'id':'A-C','text':'虚构C已经改装，但趋势领先未知；显著收益=true。'}, {'id':'A-D','text':'虚构D属于类比领域，领先/收益=true，但目标场景适用性未知。'}, {'id':'A-E','text':'虚构E有自研成果和显著收益，但在所选趋势不领先。'}]
def trait(v,ev):return {'value':v,'state':'unknown'if v is None else'declared_teaching','assumption_refs':[ev]}
profiles=[]
for i,a,b,sol,domain,fit in [('A',False,False,False,'target',True),('B',True,True,False,'target',True),('C',None,True,True,'target',True),('D',True,True,True,'analog',None),('E',False,True,True,'target',True)]:
 profiles.append({'id':'LU-'+i,'profile_provenance':'fictional_profile_not_real_person','ahead_of_named_trend':trait(a,'A-'+i),'high_expected_benefit':trait(b,'A-'+i),'self_developed_solution':trait(sol,'A-'+i),'domain':domain,'transfer_fit':trait(fit,'A-'+i),'outreach_performed':False,'rights_status':'not_negotiated_no_real_participant'})
case={'schema':'lead-user-teaching-0.1.0','problem_id':'TAP-TEACH-001','mode':'constructed_only','source_binding':binding,'trend':{'id':'TREND-TEACH-01','definition':'变化条件下持续作业需求（人为假设）','provenance':'teaching_assumption_not_market_evidence','assumption_refs':['A-TREND']},'assumptions':assumptions,'profiles':profiles,'customer_approved':False,'field_research_conducted':False}
save('01-趋势与候选输入.json',case)
def check(d):
 if d.get('mode')!='constructed_only'or d.get('field_research_conducted')is not False or d.get('customer_approved')is not False:raise ValueError('unsupported_field_or_approval_claim')
 if d.get('source_binding')!=binding or d.get('problem_id')!=binding['problem_id']:raise ValueError('upstream_binding_mismatch')
 if d.get('trend',{}).get('id')!='TREND-TEACH-01' or d['trend'].get('provenance')!='teaching_assumption_not_market_evidence':raise ValueError('trend_identity_or_evidence_mismatch')
 evidence={a['id']for a in d['assumptions']}
 if len(evidence)!=len(d['assumptions']):raise ValueError('duplicate_assumption_id')
 if not set(d['trend']['assumption_refs'])<=evidence:raise ValueError('dangling_trend_evidence')
 ids=set();out=[]
 for p in d.get('profiles',[]):
  if p['id']in ids:raise ValueError('duplicate_profile_id')
  ids.add(p['id'])
  if p.get('profile_provenance')!='fictional_profile_not_real_person':raise ValueError('fiction_promoted_to_real_person')
  if p.get('domain')not in {'target','analog'} or p.get('outreach_performed')is not False:raise ValueError('unsupported_profile_scope')
  for name in ['ahead_of_named_trend','high_expected_benefit','self_developed_solution','transfer_fit']:
   t=p[name]
   if not t.get('assumption_refs') or not set(t['assumption_refs'])<=evidence:raise ValueError('missing_or_dangling_trait_evidence')
   if t['state']=='unknown':
    if t['value']is not None:raise ValueError('unknown_must_remain_null')
   elif t['state']!='declared_teaching'or type(t['value'])is not bool:raise ValueError('invalid_trait_state')
  ahead=p['ahead_of_named_trend']['value'];benefit=p['high_expected_benefit']['value'];fit=p['transfer_fit']['value']
  if ahead is False or benefit is False:state='not_definition_match_in_named_teaching_trend'
  elif ahead is None or benefit is None:state='needs_qualification_evidence'
  elif p['domain']=='analog'and fit is not True:state='analog_lead_candidate_transfer_unresolved'
  else:state='definition_match_only_in_constructed_context'
  out.append({'profile_id':p['id'],'decision':state,'self_development_is_required':False,'real_lead_user_confirmed':False,'next':'核趋势及收益依据、场景迁移与共创安排；不是营销名单或实际邀请'})
 if not out:raise ValueError('missing_profiles')
 return {'results':out,'real_people':0,'field_qualification':False,'claim_scope':'declared criteria with evidence references only; no free-text understanding'}
save('02-资格判断与排除.json',check(case))
save('03-推荐链与共创交接.json',{'source_binding':binding,'networking_plan':[{'from':'专家线索','to':'目标领域极端经历者','reason':'寻找领先需要及显著收益材料','performed':False},{'from':'目标领域线索','to':'类比领域有相似功能挑战者','reason':'扩展原理，但检查迁移条件','performed':False}],'workshop_plan':{'participants':'用户、相关专家、设计团队分别记录，不把专家自动标领先用户','contribution_log_fields':['贡献人/来源身份','已有方案与新概念区分','材料使用范围','保密/许可/权属待协商','目标用户验证问题'],'rights':'本包无真实参与者，无协议或权利转移；具体条款须由实际双方和适当专业人员确定'},'handoff':'R19/R17可研究机制；普通目标人群采用和维护须另验证','real_communication_sent':False})
results=[]
def run(name,kind,x,expected):
 f=save('检查输入-'+name+'.json',x)
 try:o=check(x);actual='accepted'
 except Exception as e:o={'error':str(e)};actual='rejected'
 assert actual==expected,(name,actual)
 results.append({'id':name,'category':kind,'actual':actual,'expected':expected,'input':f.name,'input_sha256':sha(f),'output':o})
run('normal','normal',case,'accepted')
a=copy.deepcopy(case);a['profiles'][1]['high_expected_benefit']['assumption_refs']=[];run('missing-benefit-evidence','missing',a,'rejected')
a=copy.deepcopy(case);a['mode']='field_certification';run('not-field-certifier','not_applicable',a,'rejected')
a=copy.deepcopy(case);a['profiles'][2]['ahead_of_named_trend']['value']=False;run('unknown-not-false','boundary',a,'rejected')
a=copy.deepcopy(case);a['source_binding']['version']='WRONG';run('version-conflict','conflict',a,'rejected')
a=copy.deepcopy(case);a['profiles'][1]['self_developed_solution']['value']=False;run('non-innovator-can-match','boundary',a,'accepted');assert results[-1]['output']['results'][1]['decision']=='definition_match_only_in_constructed_context'
a=copy.deepcopy(case);a['profiles'].append(a['profiles'][0]);run('duplicate-person','conflict',a,'rejected')
# New, independent document-workflow teaching trend; no inherited rubber field qualification.
transfer={'scenario':'DOC-LU-TEACH-001','scope':'authored_cross_context_desktop_example','trend_assumption':'复杂版本交接需要（未核真实趋势）','profiles':[{'id':'DOC-A','ahead':True,'benefit':True,'self_innovation':False},{'id':'DOC-B','ahead':False,'benefit':True,'self_innovation':True}],'decisions':['definition_match_in_assumed_context','not_match_in_named_trend'],'not_transferred':['rubber-specific conditions','customer facts','qualification of real persons']}
assert transfer['profiles'][0]['ahead']and transfer['profiles'][0]['benefit'];assert not transfer['profiles'][1]['ahead'];save('05-不同情境桌面迁移.json',transfer)
save('04-实际检查记录.json',{'tests':results,'passed':len(results),'failure_count':0,'another_context':'authored_desktop_two_trait_logic_only','script_sha256':sha(Path(__file__)),'not_claimed':['automatic real-world qualification','field user research','customer acceptance']})
print('R10',len(results),'fixed checks; B qualifies within assumed definition without self-innovation')
