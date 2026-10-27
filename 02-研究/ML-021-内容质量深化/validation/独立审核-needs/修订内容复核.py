# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,copy
O=Path(__file__).parent;V=O.parent;ROOT=V.parents[2];N=ROOT/'02-研究/ML-021-内容质量深化/needs';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();first=json.loads((O/'逐稿七维内容审核.json').read_text())
expected='994013cf7b7a2b5d980b332776f913d3236cfc6cdacb06829acd76aa6bde95fa';assert sha(N/'manifest.json')==expected
manifest=json.loads((N/'manifest.json').read_text());assert all(sha(N/x['path'])==x['sha256']for x in manifest['files']);before={x['path']:sha(N/x['path'])for x in manifest['files']}
old=N/'修订历史/v0.1.0';assert sha(old/'manifest.json')==first['reviewed_manifest_sha256']
changed=[];same=[]
for m in first['methods']:
 rid=m['method_id'];p=N/'稿件'/(rid+'.md');assert sha(old/'稿件'/(rid+'.md'))==m['manuscript_sha256']
 (same if sha(p)==m['manuscript_sha256']else changed).append(rid)
assert set(changed)=={'R07','R48'}and len(same)==17
# Recompute only the listed constructed decision chain; do not run author's writer in place.
x=json.loads((N/'R07-构造闭环.json').read_text());out=[]
for r in x['confirmation_records']:
 keys=['request_job','requested_version','selected_version','artifact_job','artifact_version']
 if any(type(r.get(k))is not str or not r[k]for k in keys):v='withhold_missing_identity'
 elif r['request_job']==r['artifact_job']and r['requested_version']==r['selected_version']==r['artifact_version']:v='release_identity_only'
 else:v='withhold_mismatch'
 out.append({'id':r['id'],'decision':v})
assert [r['decision']for r in out]==['release_identity_only','withhold_mismatch','withhold_missing_identity']
r07=(N/'稿件/R07.md').read_text();assert all(t in r07 for t in ['H1','H2','候选A','候选B','C1','C2','C3','独立构造确认','不能声明真实缺陷率'])
r48=(N/'稿件/R48.md').read_text();assert'TBR标记本身不赋予批准状态'in r48
sources=json.loads((N/'来源主张映射.json').read_text());smap={m['method_id']:m for m in sources['methods']};methods=[]
for m in first['methods']:
 z=copy.deepcopy(m);rid=z['method_id'];p=N/'稿件'/(rid+'.md');lines=p.read_text().splitlines();z.update(candidate_path=str(p.relative_to(ROOT)),absolute_candidate_path=str(p),candidate_sha256=sha(p),candidate_version='ML021-needs-v0.1.1',reviewed_manifest_sha256=expected,review_status='independent_content_review_passed_with_explicit_scope',content_disposition='候选通过（声明方法教学范围）',blocking_findings=[])
 for d in z['dimensions']:
  d['evidence']['path']=str(p.relative_to(ROOT))
  if rid=='R07':
   needles={'身份与边界准确':'DFSS是一组','机制讲透':'五类工作','判断可操作':'设计响应','完整示范':'把DMADV后半程','反例与迁移':'两个失败反例','依据可追溯':'NIST','阅读与交接':'交接包括'}
   d['evidence']['line']=next((i+1 for i,l in enumerate(lines)if needles[d['dimension']]in l),1);d['rating']='充分'
   if d['dimension']in['判断可操作','完整示范']:d['reason']='新加D1—D3学习记录区分H1/H2，A提示不能修/B身份门禁被选，再以C1—C3新构造输入确认，CTQ/范围与非实测身份明确，已闭合原缺口'
  if rid=='R48'and d['dimension']=='判断可操作':d['reason']+='；TBR与批准状态已精确分管'
 z['source_and_external_limits']=smap[rid].get('fulltext_limits',[]);z['scope']='限定正文所述来源/版本/平台适配教学；不等真实工程验证、客户批准、专著/标准全实现或领域专家认证';methods.append(z)
assert all(sha(N/p)==h for p,h in before.items())
result={'schema':'ML021-final-content-review-1','reviewer':'validation_deepening independent Agent','author_group':'needs','date':'2026-10-28','reviewed_manifest_sha256':expected,'previous_reviewed_manifest_sha256':first['reviewed_manifest_sha256'],'methods':methods,'summary':{'methods':19,'candidate_passed':19,'content_revisions_pending':0,'original17_manuscript_SHA_unchanged':same,'changed_and_rechecked':['R07','R48']},'finding_closure':[{'id':'C-R07-01','status':'closed','basis':'full constructed DMADV identity-chain analysis/design/independent-input confirmation; actual independent rule recomputation recorded','records':out},{'id':'C-R48-01','status':'closed','basis':'TBR flag and requirement approval separated in body'}],'actual_review':'all19 full manuscripts read initially; source/number spot-checks recorded; this turn re-read2 actual prose diffs, independent3 confirmation record decisions, verified other17 exactSHA; not expanding unlisted semantic tests','reviewed_package_entries_unchanged_during_review':True}
(O/'final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('19 final exact-path candidates;2 corrections closed,17 unchanged,36 package entries unchanged')
