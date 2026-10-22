import json,sys,time,unittest,subprocess
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw,semantic_agent as sa

class SemanticTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def response(self,**updates):
  c=dict(entity='paper',record_id='A01',title='测试论文',field='doi',value_json=json.dumps('10.1234/test.2026'),source_id=self.sid,chunk_id='B0001',quote='DOI:10.1234/test.2026',content_nature='source_statement',object='',unit='',conditions='',limitations='')
  r=dict(summary='仅给定片段',limitations='不代表全文审核',risks=[],unresolved_conflicts=[],candidates=[c]);r.update(updates);return r
 def queue(self,reader=None):return sa.SemanticQueue(self.lib,self.root/'semantic',reader or(lambda p,f:self.response()))
 def test_persistent_pause_idempotence_single_budget_and_read_only_result(self):
  q=self.queue();job=q.enqueue('sample',[self.sid])['jobs'][0];self.assertEqual(q.enqueue('sample',[self.sid])['jobs'][0]['id'],job['id']);q.pause(True);self.assertEqual(q.step()['status'],'paused');q=self.queue();q.pause(False);self.assertEqual(q.step(job['id'])['status'],'ready');self.assertEqual(q.step()['status'],'idle');self.assertEqual(q.get(job['id'])['attempts'],1);self.assertEqual(rw.current(self.p)['candidates'],[]);self.assertEqual(rw.dataset(self.p)['records'],[]);self.assertEqual(q.bundle(job['id'],'sample')['candidates'][0]['value'],'10.1234/test.2026')
 def test_budget_and_project_boundaries(self):
  q=self.queue()
  for opts in [dict(max_calls=0),dict(max_sources=4),dict(max_chars=25000)]:
   with self.assertRaises(ValueError):q.enqueue('sample',[self.sid],**opts)
  q.enqueue('sample',[self.sid]);q.step()
  self.assertEqual(q.status('other')['jobs'],[])
  with self.assertRaises(ValueError):q.bundle(1,'other')
 def test_invalid_quote_foreign_source_and_ai_without_limits_rejected(self):
  frozen=sa.snapshot(self.lib,'sample',self.sid,24000)
  for patch in [dict(quote='虚构'),dict(source_id='other'),dict(chunk_id='B9999'),dict(content_nature='ai_interpretation',conditions='',limitations='')]:
   response=self.response();response['candidates'][0].update(patch)
   with self.subTest(patch=patch),self.assertRaises(ValueError):sa.validate_bundle(self.lib,frozen,response)
  self.assertFalse(rw.current(self.p)['candidates'])
 def test_stale_and_tampered_result_are_rejected(self):
  q=self.queue();q.enqueue('sample',[self.sid]);q.step();bundle=Path(q.get(1)['result_path']);data=pp.load(bundle);data['candidates'][0]['value']='tampered';pp.save(bundle,data)
  with self.assertRaises(ValueError):q.bundle(1,'sample')
  frozen=sa.snapshot(self.lib,'sample',self.sid,24000);x=pp.state(self.p)['sources'][self.sid];blocks=pp.load(self.p/x['chunks']);blocks[0]['text']+='changed';pp.save(self.p/x['chunks'],blocks)
  with self.assertRaises(ValueError):sa.validate_bundle(self.lib,frozen,self.response())
 def test_model_failure_never_falls_back_to_rules(self):
  def fail(p,f):raise RuntimeError('model offline')
  q=self.queue(fail);q.enqueue('sample',[self.sid]);out=q.step();self.assertEqual(out['status'],'failed');self.assertIn('model offline',out['error']);self.assertIsNone(out['result_path']);self.assertEqual(q.step()['status'],'idle');self.assertFalse(rw.current(self.p)['candidates'])
 def test_expired_lease_needs_attention_no_extra_calls(self):
  q=self.queue();q.enqueue('sample',[self.sid])
  with q.connect()as db:db.execute("UPDATE jobs SET status='running',attempts=1,lease=?",(time.time()-1,))
  self.assertEqual(q.step()['status'],'idle');self.assertEqual(q.get(1)['status'],'needs_attention');self.assertEqual(q.get(1)['attempts'],1)
 def test_risk_and_conflicts_hold_batch(self):
  q=self.queue(lambda p,f:self.response(unresolved_conflicts=['正文前后绕组匝数描述不一致']));q.enqueue('sample',[self.sid]);self.assertEqual(q.step()['status'],'needs_review');self.assertTrue(q.bundle(1,'sample')['semantic_agent']['requires_review']);self.assertFalse(rw.current(self.p)['candidates'])
 def test_empty_output_not_fake_completion(self):
  q=self.queue(lambda p,f:self.response(candidates=[]));q.enqueue('sample',[self.sid]);out=q.step();self.assertEqual(out['status'],'no_candidates')
 def test_risk_without_candidates_is_still_attention(self):
  q=self.queue(lambda p,f:self.response(candidates=[],risks=['原文存在无法裁决的矛盾']));q.enqueue('sample',[self.sid]);self.assertEqual(q.step()['status'],'needs_review');self.assertTrue(q.bundle(1,'sample')['semantic_agent']['requires_review'])
 def test_explicit_retry_preserves_attempt_logs_and_is_bounded(self):
  def fail(p,f):
   (f/'failure-proof.txt').write_text('private diagnostic');raise RuntimeError('offline')
  q=self.queue(fail);q.enqueue('sample',[self.sid]);q.step()
  with self.assertRaises(ValueError):q.retry(1,'other','actor')
  for i in range(2):q.retry(1,'sample','显式授权测试重试');self.assertEqual(q.step()['status'],'failed')
  with self.assertRaises(ValueError):q.retry(1,'sample','超过预算')
  self.assertEqual(len(list((q.folder/'job-000001').glob('attempt-*/failure-proof.txt'))),3)
 def test_missing_risk_contract_rejected(self):
  response=self.response();response.pop('risks')
  with self.assertRaises(ValueError):sa.validate_bundle(self.lib,sa.snapshot(self.lib,'sample',self.sid,24000),response)
 def test_timeout_terminates_only_call_process_group(self):
  folder=self.root/'timeout-test';folder.mkdir();fake=folder/'fake-codex';fake.write_text('#!/usr/bin/env python3\nimport subprocess,sys,time,json,pathlib\nc=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"])\npathlib.Path("child.json").write_text(json.dumps({"pid":c.pid}))\ntime.sleep(30)\n');fake.chmod(0o700);reader=sa.CodexReader();reader.timeout=2
  with patch.object(sa.shutil,'which',return_value=str(fake)),self.assertRaises(subprocess.TimeoutExpired):reader('untrusted input',folder)
  termination=pp.load(folder/'termination.json');self.assertTrue(termination['local_process_exited']);child=pp.load(folder/'child.json')['pid'];result=subprocess.run(['ps','-o','stat=','-p',str(child)],capture_output=True,text=True);self.assertTrue(not result.stdout.strip()or result.stdout.strip().startswith('Z'))
 def test_enabled_system_loopback_proxy_is_adopted_without_secrets(self):
  out=' HTTPEnable : 1\n HTTPProxy : 127.0.0.1\n HTTPPort : 7897\n HTTPSEnable : 1\n HTTPSProxy : 127.0.0.1\n HTTPSPort : 7897\n'
  with patch.object(sa.sys,'platform','darwin'),patch.object(sa.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout=out)),patch.object(sa.socket,'create_connection')as connect:
   env,note=sa.model_environment({'NO_PROXY':'internal.local'});self.assertEqual(env['HTTPS_PROXY'],'http://127.0.0.1:7897');self.assertIn('127.0.0.1',env['NO_PROXY']);self.assertEqual(note['system_proxy_adopted'],['http','https']);self.assertEqual(connect.call_count,2)
 def test_remote_disabled_invalid_or_unreachable_system_proxy_is_not_adopted(self):
  for host,enabled,port in [('proxy.example','1','7897'),('127.0.0.1','0','7897'),('127.0.0.1','1','70000')]:
   out=' HTTPEnable : '+enabled+'\n HTTPProxy : '+host+'\n HTTPPort : '+port+'\n'
   with patch.object(sa.sys,'platform','darwin'),patch.object(sa.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout=out)),patch.object(sa.socket,'create_connection')as connect:
    self.assertEqual(sa.model_environment({})[0],{});connect.assert_not_called()
  with patch.object(sa.sys,'platform','darwin'),patch.object(sa.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout=' HTTPEnable : 1\n HTTPProxy : localhost\n HTTPPort : 7897\n')),patch.object(sa.socket,'create_connection',side_effect=OSError('offline')):
   self.assertEqual(sa.model_environment({})[0],{})
 def test_existing_proxy_credentials_are_preserved_not_recorded(self):
  old={'ALL_PROXY':'http://user:private@existing:9000'}
  with patch.object(sa.subprocess,'run')as command:
   env,note=sa.model_environment(old);self.assertEqual(env,old);self.assertNotIn('private',json.dumps(note));command.assert_not_called()
 def test_per_instance_output_schema_does_not_mutate_default_or_other_reader(self):
  fake=self.root/'fake-schema-cli';fake.write_text('#!/usr/bin/env python3\nimport sys,pathlib\npathlib.Path(sys.argv[sys.argv.index("--output-last-message")+1]).write_text(\'{"analysis":"synthetic schema test"}\')\n');fake.chmod(0o700)
  custom=dict(type='object',properties=dict(analysis=dict(type='string')),required=['analysis'],additionalProperties=False)
  for i,reader in enumerate([sa.CodexReader(response_schema=custom),sa.CodexReader(response_schema=lambda:custom),sa.CodexReader()]):
   folder=self.root/('schema-'+str(i));folder.mkdir()
   with patch.object(sa.shutil,'which',return_value=str(fake)):self.assertEqual(reader('synthetic test only',folder)['analysis'],'synthetic schema test')
   self.assertEqual(pp.load(folder/'response-schema.json'),custom if i<2 else sa.response_schema())
if __name__=='__main__':unittest.main()
