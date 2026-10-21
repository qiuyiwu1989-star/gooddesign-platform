# coding: utf-8
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,source_excerpt as ex,project_ownership as own,research_workflow as rw
class ExcerptTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def create(self,**extra):
  args=dict(lib=self.lib,pid='sample',sid=self.sid,chunk_id='B0001',text='满足试验需求',title='本项目试验描述选录',reason='只用于本例试验描述，原文其他内容不作项目成果',actor='测试Agent');args.update(extra);return ex.create(**args)
 def test_shared_parent_preserved_and_child_project_not_approved(self):
  s=pp.state(self.p);old=(self.p/s['sources'][self.sid]['original']).read_bytes();pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}))
  a=self.create();s=pp.state(self.p);self.assertEqual(own.assignment(self.p,self.sid,s['sources'])['scope'],'shared');self.assertEqual(own.assignment(self.p,a['source_id'],s['sources'])['scope'],'project');self.assertEqual(old,(self.p/s['sources'][self.sid]['original']).read_bytes());x=s['sources'][a['source_id']];self.assertEqual(x['review_status'],'unreviewed');self.assertEqual(x['origin']['parent_source_sha256'],s['sources'][self.sid]['sha256']);self.assertFalse(a['expert_reviewed'])
 def test_identical_selection_is_idempotent(self):
  a=self.create();n=pp.state(self.p)['revision'];b=self.create();self.assertEqual(a['source_id'],b['source_id']);self.assertEqual(n,pp.state(self.p)['revision']);self.assertEqual(b['status'],'duplicate')
 def test_rewrite_or_wrong_block_rejected(self):
  for arg in [dict(text='满足了试验的需求'),dict(chunk_id='B9999'),dict(text='')]:
   with self.subTest(arg=arg),self.assertRaises(ValueError):self.create(**arg)
 def test_nonproject_parent_and_tamper_rejected(self):
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='reassigned')},url_rules={}))
  with self.assertRaises(ValueError):self.create()
  pp.save(self.p/'资料归属.json',dict(version=2,assignments={},url_rules={}));x=pp.state(self.p)['sources'][self.sid];(self.p/x['original']).write_text('tamper')
  with self.assertRaises(ValueError):self.create()
 def test_editorial_reason_cannot_be_used_as_source_evidence(self):
  a=self.create();sid=a['source_id'];x=pp.state(self.p)['sources'][sid];b=pp.load(self.p/x['chunks'])[0]
  self.assertEqual(ex.selected_text(self.p,x),'满足试验需求')
  for quote in ['本项目试验描述选录','只用于本例试验描述']:
   args=dict(entity='paper',record_id='A99',field='findings',value=quote,source_id=sid,chunk_id=b['id'],quote=quote)
   with self.assertRaisesRegex(ValueError,'编者说明'):rw.propose(self.lib,'sample',args,'Agent')
  args.update(quote='满足试验需求',value='满足试验需求');self.assertEqual(rw.propose(self.lib,'sample',args,'Agent')['quote'],'满足试验需求')
 def test_parent_chunks_tamper_blocks_excerpt_evidence(self):
  a=self.create();x=pp.state(self.p)['sources'][a['source_id']];parent=pp.state(self.p)['sources'][self.sid];f=self.p/parent['chunks'];f.write_text('[]')
  with self.assertRaisesRegex(ValueError,'父证据块'):ex.selected_text(self.p,x)
 def test_nested_excerpt_cannot_promote_editorial_context(self):
  a=self.create()
  with self.assertRaisesRegex(ValueError,'编者说明'):self.create(sid=a['source_id'],text='只用于本例试验描述')
  child=self.create(sid=a['source_id'],text='满足试验需求',title='二次选录');x=pp.state(self.p)['sources'][child['source_id']];self.assertEqual(ex.selected_text(self.p,x),'满足试验需求')
 def test_changed_provenance_not_silently_replaced(self):
  self.create()
  with self.assertRaisesRegex(ValueError,'不能覆盖'):self.create(actor='不同Agent')
if __name__=='__main__':unittest.main()
