# coding: utf-8
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import innovation_knowledge as ik,innovation_application as app,project_pipeline as pp,research_workflow as rw

class Knowledge046Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=pp.ROOT/'output');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.p=self.root/'P';self.p.mkdir();self.folder=self.p/'v';self.folder.mkdir()
  (self.p/'original').write_text('原始资料');(self.p/'chunks.json').write_text(json.dumps([dict(id='B1',text='系统功能保护样品')],ensure_ascii=False))
  self.src=dict(sha256=pp.sha((self.p/'original').read_bytes()),original='original',origin={})
  e=dict(source_id='S1',source_sha256=self.src['sha256'],chunks_path='chunks.json',chunks_sha256=pp.sha((self.p/'chunks.json').read_bytes()),chunk_id='B1',quote='保护样品',quote_sha256=pp.sha('保护样品'.encode()))
  self.data=dict(project_id='P',records=[dict(id='R1',entity='innovation',project_id='P',title='取样机制',cells=dict(mechanism=dict(value='保护样品',value_state='known',content_nature='source_statement',evidence=e),constraints=dict(value=None,value_state='not_researched')))],interpretations=[])
  for name in ['档案.json','manifest.json']:(self.folder/name).write_text('{}')
  self.patches=[patch.object(pp,'project',return_value=self.p),patch.object(rw,'current',return_value=dict(revision=1)),patch.object(rw,'check_version',return_value=(self.folder,{})),patch.object(rw,'dataset',side_effect=lambda *a,**kw:copy.deepcopy(self.data)),patch.object(rw,'source',side_effect=lambda p,s:self.src if s=='S1' else (_ for _ in ()).throw(ValueError('跨项目')))]
  for x in self.patches:x.start();self.addCleanup(x.stop)
 def test_index_unknown_and_no_guessed_edges(self):
  i=ik.build_index(self.root,'P');self.assertEqual(i['edges'],[]);self.assertEqual(len(i['gaps']),1);self.assertEqual(i['nodes'][0]['evidence_state'],'frozen_traceable')
 def test_match_explains_and_unmatched(self):
  out=ik.search(ik.build_index(self.root,'P'),needs=['保护样品','毫无关联词']);self.assertEqual(len(out['matches']),1);self.assertEqual(out['unmatched'][0]['term'],'毫无关联词');self.assertNotIn('score',out)
 def test_bad_quote(self):
  self.data['records'][0]['cells']['mechanism']['evidence']['quote']='不存在';self.assertRaises(ValueError,ik.build_index,self.root,'P')
 def test_cross_project_record(self):
  self.data['records'][0]['project_id']='OTHER';self.assertRaises(ValueError,ik.build_index,self.root,'P')
 def test_cross_project_source(self):
  self.data['records'][0]['cells']['mechanism']['evidence']['source_id']='OTHER';self.assertRaises(ValueError,ik.build_index,self.root,'P')
 def test_stale_index_current_guard(self):
  i=ik.build_index(self.root,'P')
  with patch.object(rw,'current',return_value=dict(revision=2)):self.assertRaises(ValueError,ik.validate_index,self.root,i,True)
  self.assertEqual(ik.validate_index(self.root,i,False)['status'],'passed')
 def test_unknown_record_relation_rejected(self):
  self.data['records'][0]['cells']['problem_id']=dict(value='OTHER',value_state='known');self.assertRaises(ValueError,ik.build_index,self.root,'P')
 def test_index_tamper(self):
  i=ik.build_index(self.root,'P');i['nodes'][0]['value']='fake';self.assertRaises(ValueError,ik.validate_index,self.root,i)
 def test_published_digest_change_rejected(self):
  i=ik.build_index(self.root,'P');(self.folder/'档案.json').write_text('{"new":true}');self.assertRaises(ValueError,ik.validate_index,self.root,i)
 def test_application_unknown_and_safe_read(self):
  r=dict(task_id='T1',title='模拟取样',scenario_type='simulated',needs=['保护样品'],functions=['取样'],constraints=[],unknowns=['材料'])
  out=app.run_application(self.root,r,{'P':'research-000001'},output_root=self.root/'runs');run=app.read_application(out['run_id'],self.root/'runs',rw.digest(r));self.assertEqual(run['analysis']['contradiction_analysis']['status'],'unknown');self.assertEqual(len(run['method_versions']),3);self.assertFalse(run['execution_mode']['source_facts_modified']);self.assertRaises(ValueError,app.read_application,'../x',self.root/'runs');self.assertRaises(ValueError,app.read_application,out['run_id'],self.root/'runs','bad')
 def test_reasoner_bad_reference_rejected(self):
  def bad(c):
   a=app._analysis(c);a['hypotheses'][0]['knowledge_refs']=['OTHER@bad'];return a
  r=dict(task_id='T1',title='模拟取样',scenario_type='simulated',needs=['保护样品'],functions=[],constraints=[],unknowns=[])
  self.assertRaises(ValueError,app.run_application,self.root,r,{'P':'research-000001'},self.root/'runs',bad,'test')
 def test_real_requirement_not_mislabeled_simulated(self):
  self.assertRaises(ValueError,app._request,dict(task_id='T',title='企业',needs=['x'],scenario_type='real'))

if __name__=='__main__':unittest.main()
