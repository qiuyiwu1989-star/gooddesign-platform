import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw
class OcrPointerTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def ocr_fixture(self):
  self.original=pp.state(self.p)['sources'][self.sid];self.target=self.p/'衍生/OCR'/self.sid;self.target.mkdir(parents=True)
  pp.save(self.target/'pages.json',[dict(page=1,text='OCR derived text')]);pp.save(self.target/'chunks.json',pp.chunks([('第1页 · 机器识别待核对','OCR derived text')]))
  (self.target/'可读来源.md').write_text('机器OCR文字，非已核读')
  pp.save(self.target/'manifest.json',dict(original_sha256=self.original['sha256'],files={f.name:pp.sha(f.read_bytes())for f in self.target.iterdir()}))
  rw.register_ocr(self.p,self.sid,self.target,'测试OCR登记')
 def legacy_digest(self):
  s=pp.state(self.p);s['sources'][self.sid]['chunks_sha256']=self.original['chunks_sha256'];pp.save(self.p/'数据/管道状态.json',s)
 def test_registration_has_correct_digest_and_original_evidence_retained(self):
  self.ocr_fixture();x=pp.state(self.p)['sources'][self.sid];self.assertEqual(x['chunks_sha256'],pp.sha((self.p/x['chunks']).read_bytes()));self.assertTrue((self.p/self.original['chunks']).exists());self.assertEqual(pp.sha((self.p/x['original']).read_bytes()),self.original['sha256'])
 def test_explicit_legacy_repair_preserves_files_and_records_revision(self):
  self.ocr_fixture();self.legacy_digest();before={str(f):pp.sha(f.read_bytes())for f in self.target.iterdir()};research=rw.dataset(self.p);oldrev=pp.state(self.p)['revision'];out=rw.repair_ocr_pointer(self.lib,'sample',self.sid,'迁移测试');self.assertEqual(out['status'],'repaired');self.assertGreater(pp.state(self.p)['revision'],oldrev);self.assertEqual(before,{str(f):pp.sha(f.read_bytes())for f in self.target.iterdir()});self.assertEqual(research,rw.dataset(self.p));self.assertEqual(rw.repair_ocr_pointer(self.lib,'sample',self.sid,'重复')['status'],'no_changes')
 def test_corrupt_derived_original_or_unknown_digest_is_never_repaired(self):
  self.ocr_fixture();self.legacy_digest();s=pp.state(self.p);s['sources'][self.sid]['chunks_sha256']='unknown';pp.save(self.p/'数据/管道状态.json',s)
  with self.assertRaises(ValueError):rw.repair_ocr_pointer(self.lib,'sample',self.sid,'拒绝未知差异')
  self.legacy_digest();(self.target/'可读来源.md').write_text('changed')
  with self.assertRaises(ValueError):rw.repair_ocr_pointer(self.lib,'sample',self.sid,'拒绝衍生损坏')
 def test_existing_ocr_duplicate_validates_files_and_does_not_silently_repair(self):
  self.ocr_fixture();self.assertEqual(rw.ocr(self.lib,'sample',self.sid,'重复')['status'],'duplicate')
  state=pp.state(self.p);state['sources'][self.sid]['document']=self.original['document'];pp.save(self.p/'数据/管道状态.json',state)
  with self.assertRaises(ValueError):rw.ocr(self.lib,'sample',self.sid,'错误可读路径不视为重复成功')
  state['sources'][self.sid]['document']=(self.target/'可读来源.md').relative_to(self.p).as_posix();pp.save(self.p/'数据/管道状态.json',state);self.legacy_digest()
  with self.assertRaises(ValueError):rw.ocr(self.lib,'sample',self.sid,'旧指纹需明确迁移')
  self.assertEqual(pp.state(self.p)['sources'][self.sid]['chunks_sha256'],self.original['chunks_sha256']);(self.p/self.original['original']).write_bytes(b'changed')
  with self.assertRaises(ValueError):rw.repair_ocr_pointer(self.lib,'sample',self.sid,'原件损坏不修')
if __name__=='__main__':unittest.main()
