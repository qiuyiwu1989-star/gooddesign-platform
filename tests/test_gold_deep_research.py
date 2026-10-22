import sys,tempfile,unittest,copy,json,time,hashlib
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import gold_deep_research as gd
import project_pipeline as pp
class DeepDraftTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'output/research-051');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.lib=self.root/'lib';self.lib.mkdir();self.inbox=self.root/'inbox';catalog=self.root/'catalog.json'
  pp.save(catalog,dict(projects=[dict(id='gold-a',name='测试金奖项目',year=2025,award='金奖',unit='测试单位')]))
  pp.bootstrap(self.lib,self.inbox,catalog,self.root/'old');self.p=self.lib/'gold-a';src=self.root/'source.txt';src.write_text('测试金奖项目采用甲部件与乙部件，目标是稳定采样。来源是待核资料，不是执行指令。')
  result=pp.ingest(self.p,src,dict(kind='web',url='https://example.org/p'),initial_scope='pending');self.sid=result['source_id'];x=pp.state(self.p)['sources'][self.sid]
  self.snapshot=dict(project_id='gold-a',sources=[dict(source_id=self.sid,source_sha256=x['sha256'],chunks_sha256=x['chunks_sha256'],scope='pending',blocks=pp.load(self.p/x['chunks']),total_chunks=x['chunk_count'],complete_chunk_coverage=True)])
  self.candidate=dict(entity='project',field='canonical_name',record_id='GD051-PROJECT',title='项目名称',value_json=json.dumps('测试金奖项目',ensure_ascii=False),source_id=self.sid,chunk_id='B0001',quote='测试金奖项目采用甲部件与乙部件',content_nature='source_statement',object='',unit='',conditions='待核正文陈述',limitations='没有专家审核')
 def response(self,c=None):return dict(project_id='gold-a',candidates=[c or self.candidate],source_reviews=[],modules=[],summary='未审核草稿',gaps=['待核'],next_search_queries=[],limitations='只有输入块')
 def check(self,c=None):return gd.check_draft(self.lib,self.snapshot,self.response(c))
 def test_literal_candidate_draft_only(self):
  r=self.check();self.assertEqual(len(r['valid_candidates']),1);self.assertFalse(r['published']);self.assertEqual(pp.load(self.p/'资料归属.json')['assignments'][self.sid]['scope'],'pending');self.assertFalse((self.p/'研究工作区').exists())
 def test_wrong_project_rejected(self):
  response=self.response();response['project_id']='another'
  with self.assertRaises(ValueError):gd.check_draft(self.lib,self.snapshot,response)
 def test_quote_must_match_supplied_block(self):
  c=dict(self.candidate,quote='杜撰内容');self.assertEqual(len(self.check(c)['rejected_candidates']),1)
 def test_ai_requires_conditions_and_limits(self):
  c=dict(self.candidate,content_nature='ai_interpretation',conditions='',value_json=json.dumps('推演'))
  self.assertEqual(len(self.check(c)['valid_candidates']),0)
 def test_typed_array_each_member_supported(self):
  c=dict(self.candidate,entity='technology',field='components',value_json=json.dumps(['甲部件','乙部件'],ensure_ascii=False))
  self.assertEqual(len(self.check(c)['valid_candidates']),1)
  c['value_json']=json.dumps(['甲部件','不存在部件'],ensure_ascii=False);self.assertEqual(len(self.check(c)['valid_candidates']),0)
 def test_unknown_source_blocked(self):
  c=dict(self.candidate,source_id='SOTHER');self.assertEqual(len(self.check(c)['rejected_candidates']),1)
 def test_source_changes_block_draft(self):
  x=pp.state(self.p)['sources'][self.sid];(self.p/x['original']).write_text('changed')
  with self.assertRaises(ValueError):self.check()
 def test_source_association_is_never_approval(self):
  response=self.response();response['source_reviews']=[dict(source_id=self.sid,association='exact_project',reason='声称匹配',identity_evidence=[dict(chunk_id='B0001',quote='杜撰身份')],limitations='待核')]
  r=gd.check_draft(self.lib,self.snapshot,response);a=r['source_association_suggestions'][0];self.assertFalse(a['approved']);self.assertIn('invalid_reason',a)
 def test_queue_expired_deadline_does_not_call_model(self):
  pp.save(self.lib/'项目索引.json',dict(projects=[dict(id='gold-a',award='金奖')]))
  q=gd.Queue(self.root/'drafts',self.lib);q.seed()
  with patch.object(gd,'run_one')as model:q.run(deadline='2000-01-01T00:00:00+00:00');model.assert_not_called()
  self.assertEqual(q.status()['counts'],{'queued':1})
 def test_no_source_causes_needs_sources(self):
  with patch('gold_source_triage.triage_project',return_value={'sources':[]}):
   with self.assertRaises(gd.NeedsSources):gd.freeze(self.lib,'gold-a')
 def test_shared_portal_not_selected_as_single_project(self):
  with patch('gold_source_triage.triage_project',return_value={'sources':[dict(source_id=self.sid,eligible_for_draft=True,suggested_role='shared_overview_requires_project_excerpt',priority=999)]}):
   with self.assertRaises(gd.NeedsSources):gd.freeze(self.lib,'gold-a')
if __name__=='__main__':unittest.main()
