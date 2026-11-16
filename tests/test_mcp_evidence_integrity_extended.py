import copy,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import project_pipeline as pp
import research_workflow as rw
import claim_evidence_packet as packet
import archive_knowledge_search as search
class Integrity(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(dir=pp.ROOT/'output');self.lib=Path(self.tmp.name);self.p=self.lib/'TEST';self.p.mkdir()
  self.write(self.lib/'项目索引.json',{'projects':[{'id':'TEST'}]})
  (self.p/'raw').write_text('original fixture');self.write(self.p/'chunks.json',[{'id':'B1','text':'fixture mechanism','locator':'paragraph 1'}])
  self.source={'id':'S1','original':'raw','sha256':pp.sha((self.p/'raw').read_bytes()),'title':'fixture','read_scope':'fixture'}
  self.write(self.p/'数据/管道状态.json',{'sources':{'S1':self.source}})
  self.ref=dict(source_id='S1',source_sha256=self.source['sha256'],chunks_path='chunks.json',chunks_sha256=pp.sha((self.p/'chunks.json').read_bytes()),chunk_id='B1',quote='fixture mechanism',quote_sha256=pp.sha(b'fixture mechanism'),source_read_scope='fixture')
  self.data={'records':[{'id':'R1','entity':'technical','cells':{'principle':{'value':'fixture mechanism','value_state':'known','content_nature':'source_statement','evidence':self.ref}}}]}
  self.publish(1,self.data)
 def tearDown(self):self.tmp.cleanup()
 def write(self,p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d))
 def publish(self,n,data):
  folder=self.p/'研究工作区/版本'/('research-%06d'%n);folder.mkdir(parents=True,exist_ok=True);self.write(folder/'档案.json',data)
  m={'revision':'research-%06d'%n,'files':{'档案.json':pp.sha((folder/'档案.json').read_bytes())}}
  if n>1:m['previous_manifest_sha256']=pp.sha((folder.parent/('research-%06d'%(n-1))/'manifest.json').read_bytes())
  self.write(folder/'manifest.json',m);self.write(self.p/'研究工作区/工作状态.json',{'revision':n,'candidates':[]})
 def read(self):return packet.read(self.lib,'TEST','research-000001','R1','principle')
 def test_valid_real_files(self):self.assertEqual(self.read()['quality']['traceability'],'verified_frozen_quotes')
 def test_original_tamper(self):
  (self.p/'raw').write_text('tampered')
  with self.assertRaisesRegex(ValueError,'original_checksum'):self.read()
 def test_chunks_tamper(self):
  (self.p/'chunks.json').write_text('[]')
  with self.assertRaisesRegex(ValueError,'chunks_checksum'):self.read()
 def test_bad_quote_with_valid_manifest(self):
  d=copy.deepcopy(self.data);d['records'][0]['cells']['principle']['evidence']['quote']='not in block';self.publish(1,d)
  with self.assertRaisesRegex(ValueError,'quote_binding'):self.read()
 def test_missing_evidence_not_verified(self):
  d=copy.deepcopy(self.data);d['records'][0]['cells']['principle'].pop('evidence');self.publish(1,d)
  x=self.read();self.assertEqual(x['evidence'],[]);self.assertEqual(x['quality']['traceability'],'missing_frozen_evidence')
 def test_ai_rejected(self):
  d=copy.deepcopy(self.data);d['records'][0]['cells']['principle']['content_nature']='ai_interpretation';self.publish(1,d)
  with self.assertRaisesRegex(ValueError,'only_known_source'):self.read()
 def test_reassigned_source_rejected(self):
  self.write(self.p/'资料归属.json',{'assignments':{'S1':{'scope':'reassigned'}},'url_rules':{}})
  with self.assertRaisesRegex(ValueError,'来源不在当前项目'):self.read()
 def test_search_reassigned_quote_rejected(self):
  self.write(self.p/'资料归属.json',{'assignments':{'S1':{'scope':'reassigned'}},'url_rules':{}})
  result=search.search(self.lib,'fixture',project_ids=['TEST'])
  self.assertEqual(result['total'],0)
  self.assertEqual(result['coverage']['failed'],1)
  self.assertIsNone(result['snapshot'])
  with self.assertRaisesRegex(ValueError,'来源不在当前项目'):self.read()
 def test_no_partial_project_leak_when_later_quote_invalid(self):
  d=copy.deepcopy(self.data);bad=copy.deepcopy(d['records'][0]);bad['id']='R2';bad['cells']['principle']['evidence']['quote']='invalid';d['records'].append(bad);self.publish(1,d)
  result=search.search(self.lib,'fixture',project_ids=['TEST'])
  self.assertEqual(result['data'],[]);self.assertEqual(result['coverage']['failed'],1)
 def test_snapshot_cannot_bypass_reassignment(self):
  a=search.search(self.lib,'fixture',project_ids=['TEST'])
  self.write(self.p/'资料归属.json',{'assignments':{'S1':{'scope':'reassigned'}},'url_rules':{}})
  with self.assertRaisesRegex(ValueError,'snapshot evidence unavailable'):search.search(self.lib,'fixture',project_ids=['TEST'],snapshot=a['snapshot'])
 def test_snapshot_survives_current_advance(self):
  a=search.search(self.lib,'fixture',project_ids=['TEST']);self.assertEqual(a['total'],1)
  d=copy.deepcopy(self.data);d['records'][0]['cells']['principle']['value']='different';self.publish(2,d)
  self.assertEqual(search.search(self.lib,'fixture',project_ids=['TEST'])['total'],0)
  b=search.search(self.lib,'fixture',project_ids=['TEST'],snapshot=a['snapshot']);self.assertEqual(b['data'],a['data'])
 def test_snapshot_corruption_rejected(self):
  a=search.search(self.lib,'fixture',project_ids=['TEST']);a['snapshot']['revisions']['TEST']='research-000009'
  with self.assertRaisesRegex(ValueError,'snapshot checksum'):search.search(self.lib,'fixture',project_ids=['TEST'],snapshot=a['snapshot'])
 def test_pinned_published_data_tamper_fails(self):
  a=search.search(self.lib,'fixture',project_ids=['TEST']);(self.p/'研究工作区/版本/research-000001/档案.json').write_text('{}')
  with self.assertRaisesRegex(ValueError,'snapshot evidence unavailable'):search.search(self.lib,'fixture',project_ids=['TEST'],snapshot=a['snapshot'])
if __name__=='__main__':unittest.main()
