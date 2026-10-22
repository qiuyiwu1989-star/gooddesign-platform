import sys,json,tempfile,unittest,time
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import gold_research_task as gt
class GoldTaskTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=gt.pp.ROOT/'output/research-050');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.lib=self.root/'lib';self.lib.mkdir();self.task=gt.Task(self.root/'task',self.lib,self.root)
  gt.pp.save(self.lib/'项目索引.json',{'projects':[{'id':'a','name':'A','award':'金奖','year':2025},{'id':'b','name':'B','award':'银奖','year':2025}]})
  gt.pp.save(self.root/'99-历史项目快照/good-design/.build/enrich.json',{'a':[{'url':'https://example.org/a','title':'A'}],'b':[{'url':'https://example.org/b'}]})
 def test_gold_only_idempotent(self):
  for _ in range(2):summary=self.task.init()
  self.assertEqual(summary['projects'],1);self.assertEqual(summary['candidate_urls'],1);self.assertEqual(summary['query_dimensions'],10);self.assertEqual(summary['unexecuted_queries'],10)
 def test_reject_non_gold_and_credential_url(self):
  self.task.init()
  for row in [{'project_id':'b','url':'https://example.org/b'},{'project_id':'a','url':'https://u:p@example.org/b'}]:
   with self.assertRaises(ValueError):self.task.add(row)
 def test_search_leads_not_complete(self):
  self.task.init();self.task.add({'project_id':'a','url':'https://example.org/new','dimension':'identity','discovery_query':'A award'})
  result=self.task.export();self.assertEqual(result['summary']['unexecuted_queries'],9);self.assertEqual(result['summary']['full_research_complete'],0)
 def test_lease_and_exclusive_claim(self):
  self.task.init();first=self.task.claim();self.assertIsNone(self.task.claim())
  with self.task.connect()as c:c.execute('UPDATE sources SET lease=?',(time.time()-1,))
  self.assertEqual(self.task.claim()['id'],first['id'])
 def test_failed_is_visible_no_automatic_retry(self):
  self.task.init()
  with patch.object(self.task,'acquire',side_effect=ValueError('HTTP 403')):self.task.run(limit=1)
  self.assertEqual(self.task.export()['summary']['failed'],1);self.assertIsNone(self.task.claim());self.assertIn('HTTP 403',(self.task.folder/'金奖采集进度.html').read_text())
 def test_reuse_does_not_rewrite_ownership(self):
  self.task.init();p=self.lib/'a';p.mkdir();(p/'old.pdf').write_bytes(b'old');source={'original':'old.pdf','sha256':gt.pp.sha(b'old'),'origin':{'url':'https://example.org/a'}}
  with patch.object(gt.pp,'project',return_value=p),patch.object(gt.pp,'state',return_value={'sources':{'S1':source}}),patch.object(gt.own,'assignment',return_value={'scope':'shared'}),patch.object(gt.pp,'fetch')as fetch:
   result=self.task.acquire({'project':'a','url':'https://example.org/a'});fetch.assert_not_called();self.assertEqual(result['ownership'],'shared');self.assertEqual(result['status'],'reused_existing')
 def test_new_material_pending_not_fact(self):
  self.task.init();gt.pp.bootstrap(self.lib,self.root/'inbox',self.lib/'项目索引.json',self.root/'archive');p=self.lib/'a';path=self.root/'article.txt';path.write_text('测试来源原文，不是档案事实。')
  def fetch(lib,inbox,pid,url,**kwargs):return gt.pp.ingest(p,path,dict(kind='web',url=url),**kwargs)
  with patch.object(gt.pp,'fetch',side_effect=fetch)as fake:
   result=self.task.acquire({'project':'a','url':'https://example.org/new'});self.assertEqual(result['ownership'],'pending');self.assertFalse((p/'研究工作区').exists());self.assertEqual(fake.call_args.kwargs['initial_scope'],'pending')
  state=gt.pp.state(p);sid=result['source_id'];snapshot=gt.pp.load(p/'版本'/('ingest-%06d'%state['revision'])/'snapshot.json')
  self.assertEqual(snapshot['ownership_registry']['assignments'][sid]['scope'],'pending')
 def test_duplicate_does_not_change_ownership(self):
  self.task.init();gt.pp.bootstrap(self.lib,self.root/'inbox',self.lib/'项目索引.json',self.root/'archive');p=self.lib/'a';path=self.root/'article.txt';path.write_text('已审核归属不能被重复下载改写。')
  first=gt.pp.ingest(p,path);second=gt.pp.ingest(p,path,initial_scope='pending')
  self.assertEqual(second['status'],'duplicate');self.assertEqual(gt.own.assignment(p,first['source_id'],gt.pp.state(p)['sources'])['scope'],'project')
 def test_record_actual_search_separate_from_plan(self):
  self.task.init();self.task.record_search({'project_id':'a','query':'A exact search','status':'no_leads','results':[]})
  r=self.task.export();self.assertEqual(r['summary']['projects_searched'],1);self.assertEqual(r['projects'][0]['search_history'][0]['query'],'A exact search');self.assertEqual(r['summary']['candidate_urls'],1)
if __name__=='__main__':unittest.main()
