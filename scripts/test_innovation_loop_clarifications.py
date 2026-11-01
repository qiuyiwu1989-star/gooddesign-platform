"""ML025 independent QA: local temporary data, no customer confirmations."""
import copy,json,tempfile,unittest,threading,http.client
from pathlib import Path
from unittest.mock import patch
from innovation_loop_store import LoopStore,ROOT
from innovation_loop_tasks import load_task
from innovation_loop_server import Handler,ThreadingHTTPServer

class ClarificationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=ROOT/'output/innovation-loop-025/qa');self.s=LoopStore(Path(self.tmp.name)/'test.sqlite3');self.rq=load_task('rubber-v1')['requirement'];self.s.put('requirement',self.rq)
  self.record={'schema_version':'0.1.0','id':'CLAR-QA','revision':1,'task_id':'rubber-v1','requirement_ref':{'id':self.rq['id'],'revision':1},'field':'budget','value':'待提供报价，尚未确认','actor':'内部QA','status':'pending_review'}
 def tearDown(self):self.tmp.cleanup()
 def test_saved_pending_and_requirement_unchanged(self):
  self.s.put('clarification',self.record);self.assertEqual(self.s.get('clarification','CLAR-QA',1)['status'],'pending_review');self.assertEqual(self.s.get('requirement',self.rq['id'],1),self.rq)
 def test_idempotent_and_immutable(self):
  self.s.put('clarification',self.record);self.assertEqual(self.s.put('clarification',self.record)['status'],'already_saved');r=copy.deepcopy(self.record);r['value']='different'
  with self.assertRaises(ValueError):self.s.put('clarification',r)
 def test_mismatched_task_ref(self):
  r=copy.deepcopy(self.record);r['task_id']='gear-v1'
  with self.assertRaises(ValueError):self.s.put('clarification',r)
 def test_status_and_fields(self):
  for key,value in [('status','confirmed'),('field','goal'),('value',True),('value',''),('actor',''),('revision',True)]:
   with self.subTest(key=key,value=value):
    r=copy.deepcopy(self.record);r[key]=value
    with self.assertRaises(ValueError):self.s.put('clarification',r)
 def test_http_rejects_injected_confirmation_and_wrong_origin(self):
  with patch('innovation_loop_server.LoopStore',return_value=self.s):
   server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();port=server.server_port
   def post(data,origin=None):
    conn=http.client.HTTPConnection('127.0.0.1',port);body=json.dumps(data);conn.request('POST','/api/clarifications',body,{'Content-Type':'application/json','Origin':origin or f'http://127.0.0.1:{port}'});r=conn.getresponse();out=(r.status,json.loads(r.read()));conn.close();return out
   try:
    data={k:self.record[k] for k in ['task_id','field','value','actor']}
    self.assertEqual(post(data)[0],200);self.assertEqual(post(data)[1]['status'],'already_saved')
    self.assertEqual(post(dict(data,status='confirmed'))[0],400);self.assertEqual(post(data,'https://example.com')[0],403)
    self.assertEqual(post(dict(data,task_id='../../private'))[0],400)
    self.assertEqual(self.s.get('requirement',self.rq['id'],1),self.rq)
   finally:server.shutdown();server.server_close();thread.join()
if __name__=='__main__':unittest.main()
