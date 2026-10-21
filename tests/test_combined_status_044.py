import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_file_admin_033 as base
class CombinedStatus(unittest.TestCase):
 setUp=base.FileAdminTests.setUp
 tearDown=base.FileAdminTests.tearDown
 request=base.FileAdminTests.request
 def test_persistent_and_legacy_counts_are_scoped_readonly_and_not_file_counts(self):
  store=self.srv.store;store.jobs=[dict(project_id='demo-01',status=x)for x in ['queued','running','failed']]+[dict(project_id='other',status='failed')]
  with store.steward.connect()as d:
   for i,(pid,state)in enumerate([('demo-01',s)for s in ['queued','retry','running','failed','needs_attention','awaiting_agent','scope_hold']]+[('other','failed')]):
    d.execute('INSERT INTO tasks(project,key,payload,status,created)VALUES(?,?,?,?,?)',(pid,'fixture'+str(i),json.dumps(dict(kind='source',source_id='fixture'+str(i))),state,'test'))
   before=[tuple(r)for r in d.execute('SELECT * FROM tasks')]
  code,data,_=self.request('/api/automation?project=demo-01');self.assertEqual(code,200);self.assertEqual((data['queued'],data['running'],data['attention_records'],data['awaiting_agent'],data['scope_hold']),(3,2,3,1,1));self.assertEqual(data['count_scope'],'processing_tasks_not_unique_sources');self.assertEqual((data['failed_records'],data['needs_judgment']),(2,1))
  with store.steward.connect()as d:self.assertEqual(before,[tuple(r)for r in d.execute('SELECT * FROM tasks')])
 def test_pending_reading_and_scope_hold_are_not_failed_or_queued(self):
  store=self.srv.store
  with store.steward.connect()as d:
   for state in ['awaiting_agent','scope_hold']:
    d.execute('INSERT INTO tasks(project,key,payload,status,created)VALUES(?,?,?,?,?)',('demo-01',state,json.dumps(dict(kind='source',source_id=state)),state,'test'))
  code,data,_=self.request('/api/automation?project=demo-01');self.assertEqual(code,200);self.assertEqual((data['queued'],data['running'],data['attention_records']),(0,0,0));self.assertEqual((data['awaiting_agent'],data['scope_hold']),(1,1))
if __name__=='__main__':unittest.main()
