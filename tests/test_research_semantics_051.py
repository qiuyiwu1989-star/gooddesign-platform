import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import project_pipeline as pp,research_workflow as rw
class SemanticsTests(unittest.TestCase):
 def setUp(self):
  folder=ROOT/'output/semantic-gate-tests';folder.mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=folder);self.root=Path(self.tmp.name);self.lib=self.root/'lib';cat=self.root/'catalog.json';pp.save(cat,dict(projects=[dict(id='sample',name='测试项目')]));pp.bootstrap(self.lib,self.root/'inbox',cat,self.root/'archive');p=pp.project(self.lib,'sample');raw=self.root/'source.txt';raw.write_text('2013年建成投产。已发生。申请公布号 CN 110316339 A。授权公告号 CN 110316339 B。授权公告号 CN 202991532 U。');self.sid=pp.ingest(p,raw)['source_id']
 def tearDown(self):self.tmp.cleanup()
 def propose(self,entity,field,value,quote,**extra):return rw.propose(self.lib,'sample',dict(entity=entity,record_id='R1',title='语义校验',field=field,value=value,source_id=self.sid,chunk_id='B0001',quote=quote,**extra),'test')
 def test_event_narrative_must_use_action(self):
  with self.assertRaisesRegex(ValueError,'发生状态'):self.propose('event','occurrence','2013年建成投产','2013年建成投产')
  self.propose('event','action','2013年建成投产','2013年建成投产');self.propose('event','occurrence','已发生','已发生')
 def test_patent_roles_cannot_swap(self):
  for value in ['CN 110316339 B','CN 202991532 U']:
   with self.assertRaisesRegex(ValueError,'授权公告号'):self.propose('patent','publication_number',value,value)
   self.propose('patent','grant_number',value,value)
  with self.assertRaisesRegex(ValueError,'申请公布号'):self.propose('patent','grant_number','CN 110316339 A','CN 110316339 A')
  self.propose('patent','publication_number','CN 110316339 A','CN 110316339 A')
 def test_clear_bad_legacy_value_remains_possible(self):
  self.propose('event','occurrence',None,'2013年建成投产',operation='clear',limitations='撤回错字段，不抹历史')
