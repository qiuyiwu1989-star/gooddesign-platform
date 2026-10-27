from pathlib import Path
import sys,json,importlib.util
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import project_pipeline as pp,research_workflow as rw
prep=ROOT/'output/research-051/native-preparation/deepening-round1-batch01';spec=importlib.util.spec_from_file_location('safe_prepare',prep/'prepare_native.py');safe=importlib.util.module_from_spec(spec);spec.loader.exec_module(safe)
assert pp.sha(safe.REVIEW.read_bytes())==safe.REVIEW_SHA
out=ROOT/'output/research-051/root/deepening01-published.json';assert not out.exists(),'already recorded; do not republish'
results=[]
for x in pp.load(prep/'root-propose-pending.json')['projects']:
 pid=x['project_id'];p,w,data=safe.assert_version(pid);ids=x['pending_candidate_ids'];candidates=[c for c in w['candidates']if c['id']in ids];assert len(candidates)==len(ids)
 for c in candidates:
  assert c['status']=='pending';rw.evidence(p,c);assert safe.supported(c)
  assert '采用' in str(c.get('limitations','')) or 'related' in str(c.get('limitations','')).lower(),c
 for cid in ids:rw.review(pp.LIB,pid,cid,'approved','051root整合独立专利首页复核','逐字首页题录及原生块指纹核验；仅相关技术参考，未证获奖采用/当前法律状态，04非连续权利人一项保留hold',reviewer_kind='agent',expected_status='pending')
 result=rw.publish(pp.LIB,pid,'051root独立复核整合','限定专利题录参考补证，不认型号采用、全文核读、当前权属或法律状态；不调分',selected_candidate_ids=ids);results.append(dict(project_id=pid,result=result,candidate_ids=ids));pp.save(out,dict(projects=results,scope='bibliography_related_only_no_score_change'))
print(json.dumps(results,ensure_ascii=False))
