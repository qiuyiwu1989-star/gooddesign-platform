import sys,unittest,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,project_ownership as own,source_json_row as jr,research_workflow as rw
import build_research_handoff as export
from research_handoff_check import check
class RowTests(unittest.TestCase):
 tearDown=base.ResearchTests.tearDown
 def setUp(self):
  base.ResearchTests.setUp(self);s=pp.state(self.p);s['project']['year']=2015;pp.commit(self.p,s,'测试年份')
  self.row=dict(id='official1',opusName='测试项目',matchYear=2015,awardName='金奖',participant='测试机构',createTime='201706030001');self.raw=self.root/'catalog.json';pp.save(self.raw,dict(status=True,data=dict(rows=[self.row,dict(id='other',opusName='别的项目',matchYear=2015,awardName='金奖')])));self.parent=pp.ingest(self.p,self.raw)['source_id'];pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.parent:dict(scope='shared')},url_rules={}))
 def create(self):return jr.create(self.lib,'sample',self.parent,'official1','Agent')
 def test_exact_project_row_and_parent_shared(self):
  a=self.create();s=pp.state(self.p);x=s['sources'][a['source_id']];self.assertEqual(jr.validate(self.p,x),self.row);self.assertEqual(own.assignment(self.p,self.parent,s['sources'])['scope'],'shared');self.assertEqual(own.assignment(self.p,a['source_id'],s['sources'])['scope'],'project');self.assertNotIn('别的项目',(self.p/x['original']).read_text())
 def test_mismatch_name_year_and_duplicate_row_rejected(self):
  for row in [dict(self.row,opusName='其他'),dict(self.row,matchYear=2017)]:
   pp.save(self.raw,dict(status=True,data=dict(rows=[row])));sid=pp.ingest(self.p,self.raw)['source_id']
   with self.assertRaises(ValueError):jr.create(self.lib,'sample',sid,'official1','Agent')
  pp.save(self.raw,dict(status=True,data=dict(rows=[self.row,self.row])));sid=pp.ingest(self.p,self.raw)['source_id']
  with self.assertRaises(ValueError):jr.create(self.lib,'sample',sid,'official1','Agent')
 def test_idempotent_and_no_provenance_overwrite(self):
  a=self.create();self.assertEqual(a['source_id'],self.create()['source_id'])
  with self.assertRaises(ValueError):jr.create(self.lib,'sample',self.parent,'official1','Other')
 def test_parent_tamper_blocks_evidence(self):
  a=self.create();x=pp.state(self.p)['sources'][a['source_id']];parent=pp.state(self.p)['sources'][self.parent];(self.p/parent['original']).write_text('{}')
  with self.assertRaises(ValueError):jr.validate(self.p,x)
  args=dict(entity='award',record_id='AWARD',field='level',value='金奖',source_id=a['source_id'],chunk_id='B0001',quote='金奖')
  with self.assertRaises(ValueError):rw.propose(self.lib,'sample',args,'Agent')
 def test_child_byte_tamper_and_assessment_fail_closed(self):
  import research_assessment as ra
  a=self.create();sid=a['source_id'];args=dict(entity='award',record_id='AWARD',field='level',value='金奖',source_id=sid,chunk_id='B0001',quote='金奖');c=rw.propose(self.lib,'sample',args,'Agent');rw.review(self.lib,'sample',c['id'],'approved','审读','测试');rw.publish(self.lib,'sample','tester','入档');d=rw.dataset(self.p);self.assertEqual(ra.audit(self.p,d)['status'],'traceable');x=pp.state(self.p)['sources'][sid];f=self.p/x['original'];f.write_bytes(f.read_bytes()+b' ')
  with self.assertRaises(ValueError):jr.validate(self.p,x)
  self.assertEqual(ra.audit(self.p,d)['status'],'attention')
 def test_export_excludes_full_catalog_and_preserves_proof(self):
  a=self.create();args=dict(entity='award',record_id='AWARD',field='level',value='金奖',source_id=a['source_id'],chunk_id='B0001',quote='金奖');c=rw.propose(self.lib,'sample',args,'Agent');rw.review(self.lib,'sample',c['id'],'approved','审读','测试核对');rw.publish(self.lib,'sample','tester','条目入档');p=Path(export.build(self.lib,'sample',self.root/'out')['folder']);check(p);self.assertFalse((p/'资料库/来源'/self.parent).exists());rows=pp.load(p/'资料库/来源目录.json')['items'];self.assertTrue(any(x.get('origin',{}).get('row_id')=='official1'for x in rows))
if __name__=='__main__':unittest.main()
