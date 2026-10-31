import unittest,copy,tempfile,json
from pathlib import Path
import innovation_loop_tasks as t
class TaskTests(unittest.TestCase):
 def test_three_isolated(self):
  tasks=[t.load_task(i) for i in t.IDS];self.assertEqual(len(t.list_tasks()),3)
  ids=[x['requirement']['id'] for x in tasks]+[r['id'] for x in tasks for r in x['routes']]
  self.assertEqual(len(ids),len(set(ids)))
  for x in tasks:self.assertEqual(len(x['actions']),3);self.assertIsNone(x['requirement']['budget']);self.assertIsNone(x['requirement']['confirmation'])
 def test_bad_task(self):
  with self.assertRaises(ValueError):t.load_task('../secret')
 def test_source_change(self):
  b=t.load_task(t.IDS[0]);b['source_refs'][0]['sha256']='0'*64
  with self.assertRaises(ValueError):t._check(b)
 def test_cross_task_action(self):
  b=t.load_task(t.IDS[0]);b['actions'][0]['route_ref']['id']='OTHER'
  with self.assertRaises(ValueError):t._check(b)
 def test_no_shared_mutation(self):
  a=t.load_task(t.IDS[0]);a['routes'][0]['cost']=0;self.assertIsNone(t.load_task(t.IDS[0])['routes'][0]['cost'])
if __name__=='__main__':unittest.main()
