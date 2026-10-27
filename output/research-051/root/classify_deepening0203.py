from pathlib import Path
import sys,copy,json
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import project_pipeline as pp,project_ownership as own
base=ROOT/'output/research-051/native-preparation/deepening-round1-batch02-03'
for row in pp.load(base/'root-ingest-pending.json')['projects']:
 pid=row['project_id'];sid=row['ingestion']['source_id'];scope='project'if pid=='2023-05'else'shared'
 with pp.lock(pp.LIB):
  p=pp.project(pp.LIB,pid);state=pp.state(p);s=state['sources'][sid];assert pp.sha(pp.safe(p,s['original']).read_bytes())==s['sha256'];reg=own.registry(p);old=own.assignment(p,sid,state['sources'],reg)
  if old['scope']==scope:continue
  assert old['scope']=='pending';before=copy.deepcopy(reg);entry=dict(scope=scope,owner_project=pid if scope=='project'else None,relation='related_only'if scope=='project'else'shared_mixed_parent',reason='独立复核题录/指定原文范围；专利仅技术参考，目录/论文父件含其他内容，只准精确选录',actor='051root独立审核整合',source_sha256=s['sha256'],updated_at=pp.now());reg['assignments'][sid]=entry;reg['version']+=1;reg['updated_at']=pp.now();pp.save(p/'资料归属.json',reg);pp.save(p/'归属版本'/('ownership-%06d.json'%reg['version']),dict(project_id=pid,registry=reg,previous_registry=before,changes=[dict(source_id=sid,before=old,after=entry)],actor=entry['actor'],recorded_at=pp.now()));pp.commit(p,state,entry['reason'])
print('3 parent sources classified, no fact publication')
