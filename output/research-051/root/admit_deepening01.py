"""Root integration of independently read patent bibliographies; related references only."""
from pathlib import Path
import sys,json,copy,importlib.util
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import project_pipeline as pp,project_ownership as own,research_workflow as rw
prep=ROOT/'output/research-051/native-preparation/deepening-round1-batch01';spec=importlib.util.spec_from_file_location('safe_prepare',prep/'prepare_native.py');safe=importlib.util.module_from_spec(spec);spec.loader.exec_module(safe)
assert pp.sha(safe.REVIEW.read_bytes())==safe.REVIEW_SHA
for pid in safe.EXPECTED:
 p,_,_=safe.assert_version(pid);fetch=pp.load(safe.BASE/pid/'pdf-fetch-log.json');sid='S'+fetch['raw_sha256'][:16]
 with pp.lock(pp.LIB):
  state=pp.state(p);s=state['sources'][sid];assert s['sha256']==fetch['raw_sha256'] and pp.sha(pp.safe(p,s['original']).read_bytes())==s['sha256']
  reg=own.registry(p);old=own.assignment(p,sid,state['sources'],reg)
  if old.get('relation')=='related_only':continue
  assert old['scope']=='pending';before=copy.deepcopy(reg)
  entry=dict(scope='project',owner_project=pid,relation='related_only',reason='独立目视原专利首页题录，相关技术参考；未证明获奖装备采用、现权属或法律状态，非全文核读',actor='051root整合独立首页核读',updated_at=pp.now(),source_sha256=s['sha256'])
  reg['assignments'][sid]=entry;reg['version']+=1;reg['updated_at']=pp.now();pp.save(p/'资料归属.json',reg);pp.save(p/'归属版本'/('ownership-%06d.json'%reg['version']),dict(project_id=pid,registry=reg,previous_registry=before,changes=[dict(source_id=sid,before=old,after=entry)],actor=entry['actor'],recorded_at=pp.now()));pp.commit(p,state,entry['reason'])
print('Two exact sources classified related_only; no facts approved by classification')
