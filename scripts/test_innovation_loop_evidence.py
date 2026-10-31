import copy,json,unittest
from innovation_loop_evidence import verify_experience_files
from innovation_loop_store import ROOT
class EvidenceTests(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/'output/innovation-loop-024/experience/experiences-v0.4.0.json').read_text())[0]
 def test_real_binding(self):self.assertFalse(verify_experience_files(self.r)['semantic_approval'])
 def test_bad_quote_sha(self):
  r=copy.deepcopy(self.r);r['evidence_refs'][0]['quote_sha256']='0'*64
  with self.assertRaises(ValueError):verify_experience_files(r)
 def test_wrong_chunk_file(self):
  r=copy.deepcopy(self.r);r['evidence_refs'][0]['chunks_path']='来源/wrong/chunks.json'
  with self.assertRaises((ValueError,FileNotFoundError)):verify_experience_files(r)
 def test_outside_project(self):
  r=copy.deepcopy(self.r);r['evidence_refs'][0]['dataset_path']='/etc/passwd'
  with self.assertRaises(ValueError):verify_experience_files(r)
 def test_fake_dataset(self):
  import hashlib
  r=copy.deepcopy(self.r);path=ROOT/'04-知识库/项目库'/r['evidence_refs'][0]['project_id']/'资料归属.json'
  r['evidence_refs'][0]['dataset_path']=str(path);r['evidence_refs'][0]['dataset_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
  with self.assertRaises(ValueError):verify_experience_files(r)
 def test_source_level_cannot_claim_native(self):
  r=json.loads((ROOT/'output/innovation-loop-024/experience/deepening-v0.5.1/experiences.json').read_text())[0]
  verify_experience_files(r);r['evidence_refs'][0]['native_published_record']=True
  with self.assertRaises(ValueError):verify_experience_files(r)
if __name__=='__main__':unittest.main()
