# coding: utf-8
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw
from archive_steward import Steward
class IdentityTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def index(self,**extra):
  path=self.p/'论文原文管理/论文原件清单.json';x=pp.load(path);x['items'][0].update(extra);pp.save(path,x)
 def baseline(self):
  self.index(doi='10.1234/test.2026');c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','测试','标准文献记录')
 def old(self,**extra):return self.candidate(record_id='DOC-'+self.sid,extraction_method='conservative_rules_v1',**extra)
 def test_same_value_placeholder_closes_with_rule_and_preserves_facts(self):
  self.baseline();c=self.old();before=rw.dataset(self.p);self.assertEqual(rw.close_duplicate_identifiers(self.lib,'sample'),[c['id']]);now=next(x for x in rw.current(self.p)['candidates']if x['id']==c['id']);self.assertEqual(now['status'],'rejected');self.assertEqual(now['reviewer_kind'],'rule');self.assertEqual(now['quote'],c['quote']);self.assertEqual(now['resolution']['record_id'],'A01');self.assertEqual(before,rw.dataset(self.p));self.assertEqual(rw.close_duplicate_identifiers(self.lib,'sample'),[])
 def test_conflicting_identifier_and_human_decisions_not_closed(self):
  self.baseline();wrong=self.old(value='10.1234/test.202');human=self.old(quote='10.1234/test.2026');rw.review(self.lib,'sample',human['id'],'needs_more','人','需要继续核对');manual=self.old();self.approve(manual);self.assertEqual(rw.close_duplicate_identifiers(self.lib,'sample'),[]);self.assertEqual(next(c for c in rw.current(self.p)['candidates']if c['id']==wrong['id'])['status'],'pending')
 def test_stale_evidence_not_closed(self):
  self.baseline();self.old();x=pp.state(self.p)['sources'][self.sid];path=self.p/x['chunks'];blocks=pp.load(path);blocks[0]['text']+=' mutation';pp.save(path,blocks);self.assertEqual(rw.close_duplicate_identifiers(self.lib,'sample'),[])
 def test_related_html_maps_to_same_identity(self):
  self.index(library_source_id='another-format',related_source_ids=[self.sid],doi='10.1234/test.2026');out=rw.extract(self.lib,'sample',self.sid,'规则');cs=[c for c in rw.current(self.p)['candidates']if c['id']in out['candidates']];self.assertTrue(all(c['record_id']=='A01'for c in cs))
 def test_indexed_patent_does_not_take_citation_identifiers(self):
  path=self.root/'patent.txt';path.write_text('授权公告号 CN 102611346 B\n对比文件 CN 101340156 B\n引用 CN 101442290 A');sid=pp.ingest(self.p,path)['source_id'];pp.save(self.p/'专利原文管理/专利原件清单.json',dict(items=[dict(patent_id='P01',title='当前专利',library_source_id=sid,publication='CN102611346B')]))
  out=rw.extract(self.lib,'sample',sid,'规则');cs=[c for c in rw.current(self.p)['candidates']if c['id']in out['candidates']];self.assertEqual([(c['field'],c['value'])for c in cs],[('grant_number','CN102611346B')]);self.assertEqual(cs[0]['extraction_method'],rw.RULE_METHOD)
 def test_missing_declared_doi_never_auto_admits_unknown_identity(self):
  s=Steward(self.lib,self.inbox);s.enqueue_source('sample',self.sid);s.tick();self.assertEqual(rw.current(self.p)['revision'],0);self.assertEqual(s.summary('sample')['counts']['needs_attention'],1)
 def test_only_fully_resolved_task_exceptions_leave_attention(self):
  self.baseline();c=self.old();s=Steward(self.lib,self.inbox);s.enqueue_candidates('sample',[c['id']]);s.tick()
  # A source-processing task with only this placeholder exception, as generated before indexing.
  t=s.enqueue('sample',dict(kind='source',source_id=self.sid))
  with s.connect()as db:db.execute("UPDATE tasks SET status='needs_attention',result=? WHERE id=?",(__import__('json').dumps(dict(exceptions=[dict(candidate_id=c['id'])])),t['id']))
  s.reconcile_identifiers('sample')
  with s.connect()as db:row=dict(db.execute('SELECT * FROM tasks WHERE id=?',(t['id'],)).fetchone())
  self.assertEqual(row['status'],'awaiting_agent');self.assertEqual(rw.current(self.p)['revision'],1);self.assertIn('previous_exceptions',row['result']);self.assertTrue(s.summary('sample')['controls'])
 def test_mixed_exceptions_remain_attention(self):
  self.baseline();c=self.old();s=Steward(self.lib,self.inbox);t=s.enqueue('sample',dict(kind='source',source_id=self.sid))
  with s.connect()as db:db.execute("UPDATE tasks SET status='needs_attention',result=? WHERE id=?",(__import__('json').dumps(dict(exceptions=[dict(candidate_id=c['id']),dict(candidate_id='different-conflict')])),t['id']))
  s.reconcile_identifiers('sample')
  with s.connect()as db:self.assertEqual(db.execute('SELECT status FROM tasks WHERE id=?',(t['id'],)).fetchone()[0],'needs_attention')
 def test_maintenance_failure_is_reported_without_stopping_worker(self):
  import threading
  from unittest.mock import patch
  s=Steward(self.lib,self.inbox);s.enqueue_source('sample',self.sid);signal=threading.Event()
  with patch.object(rw,'close_duplicate_identifiers',side_effect=OSError('bad project metadata')),patch.object(s,'tick',side_effect=lambda:signal.set()or False):
   try:s.start();self.assertTrue(signal.wait(2));self.assertTrue(s.summary('sample')['maintenance_attention'])
   finally:s.close()
if __name__=='__main__':unittest.main()
