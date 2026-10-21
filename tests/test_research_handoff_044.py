# coding: utf-8
import json,sys,subprocess,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw,research_reader_notes as rn
import build_research_handoff as export
from research_handoff_check import check,sha
class HandoffTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 candidate=base.ResearchTests.candidate
 approve=base.ResearchTests.approve
 def publish(self):
  c=self.candidate();self.approve(c);rw.publish(self.lib,'sample','tester','测试首版')
 def build(self):return export.build(self.lib,'sample',self.root/'out')
 def reseal(self,folder):
  pp.save(folder/'manifest.json',dict(schema='research-handoff-1.0',files={str(f.relative_to(folder)):sha(f)for f in folder.rglob('*')if f.is_file()and f!=folder/'manifest.json'}))
 def test_portable_layered_read_and_zip_integrity(self):
  self.publish();r=self.build();p=Path(r['folder']);self.assertEqual(check(p)['records'],1);self.assertFalse(check(p)['expert_reviewed']);self.assertEqual(r['check']['history_scope'],'single_snapshot_not_full_chain')
  for args in [[],['--record','A01'],['--source',self.sid]]:
   x=subprocess.run([sys.executable,str(p/'read.py'),*args],capture_output=True,text=True,check=True);self.assertIsInstance(json.loads(x.stdout),dict)
  with zipfile.ZipFile(r['zip'])as z:self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),len(list(p.rglob('*')))-sum(f.is_dir()for f in p.rglob('*')))
  self.assertEqual(Path(r['zip']+'.sha256').read_text().split()[0],sha(Path(r['zip'])))
 def test_repeated_export_keeps_previous(self):
  self.publish();a=self.build();b=self.build();self.assertNotEqual(a['folder'],b['folder']);check(Path(a['folder']));check(Path(b['folder']))
 def test_reassigned_cited_source_blocks_export(self):
  self.publish();pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.sid:dict(scope='shared')},url_rules={}))
  with self.assertRaisesRegex(ValueError,'当前项目'):self.build()
  self.assertEqual(list((self.root/'out').iterdir()),[])
 def test_uncited_other_source_excluded_and_origin_path_removed(self):
  self.publish();raw=self.root/'other.txt';raw.write_text('其他项目');sid=pp.ingest(self.p,raw,origin=dict(kind='local_upload',path='/Users/private/original.txt'))['source_id'];pp.save(self.p/'资料归属.json',dict(version=1,assignments={sid:dict(scope='pending')},url_rules={}))
  p=Path(self.build()['folder']);rows=pp.load(p/'资料库/来源目录.json')['items'];self.assertEqual([x['id']for x in rows],[self.sid]);self.assertNotIn('/Users/',json.dumps(rows))
 def test_frozen_old_chunks_preserved_after_reclean(self):
  self.publish();s=pp.state(self.p);old=s['sources'][self.sid]['chunks'];new='衍生/new/chunks.json';pp.save(self.p/new,[dict(id='B0001',text='new revision')]);s['sources'][self.sid]['chunks']=new;pp.save(self.p/'数据/管道状态.json',s)
  p=Path(self.build()['folder']);self.assertTrue((p/'资料库'/old).exists());self.assertTrue((p/'资料库'/new).exists());self.assertEqual(check(p)['evidence'],1)
 def test_tampered_and_extra_file_rejected(self):
  self.publish();p=Path(self.build()['folder']);f=p/'研究版本/01-项目档案.md';original=f.read_bytes();f.write_text('改动')
  with self.assertRaises(ValueError):check(p)
  f.write_bytes(original);(p/'extra.txt').write_text('extra')
  with self.assertRaises(ValueError):check(p)
 def test_resealed_invalid_quote_rejected(self):
  self.publish();p=Path(self.build()['folder']);d=pp.load(p/'研究版本/档案.json');d['records'][0]['cells']['doi']['evidence']['quote']='invented';pp.save(p/'研究版本/档案.json',d);pub=pp.load(p/'研究版本/manifest.json');pub['files']['档案.json']=sha(p/'研究版本/档案.json');pp.save(p/'研究版本/manifest.json',pub);self.reseal(p)
  with self.assertRaisesRegex(ValueError,'摘录'):check(p)
 def test_guide_bound_and_revision_parent_identity(self):
  self.publish();c=self.candidate(field='findings',value='满足试验需求',quote='满足试验需求');self.approve(c);rw.publish(self.lib,'sample','tester','第二版');vf,_=rw.check_version(self.p,'research-000002')
  payload=dict(schema=rn.SCHEMA,project_id='sample',version='0.1.0',research_revision='research-000002',dataset_sha256=sha(vf/'档案.json'),content_nature='ai_reading_guide',overview='AI阅读辅助',modules=[dict(module_id=i,summary='已知情况',record_ids=['A01']if i==5 else[],gaps=['需要专业审核'])for i in range(1,9)])
  rn.freeze(self.lib,'sample',payload,'tester');p=Path(self.build()['folder']);self.assertEqual(pp.load(p/'交付概览.json')['guide_version'],'0.1.0');self.assertTrue((p/'历史对照/前序manifest.json').exists());check(p)
  notes=pp.load(p/'阅读导读/导读.json');notes['research_revision']='research-000001';pp.save(p/'阅读导读/导读.json',notes);self.reseal(p)
  with self.assertRaises(ValueError):check(p)
 def test_symlink_even_empty_folder_rejected(self):
  self.publish();p=Path(self.build()['folder']);(p/'escape').symlink_to(self.root,target_is_directory=True)
  with self.assertRaises(ValueError):check(p)
 def test_wrong_ai_nature_rejected_even_resealed(self):
  c=self.candidate(field='findings',value='应用设想',content_nature='ai_hypothesis',conditions='需要试验',limitations='未验证');self.approve(c);rw.publish(self.lib,'sample','tester','AI试验');p=Path(self.build()['folder']);d=pp.load(p/'研究版本/档案.json');d['interpretations'][0]['content_nature']='source_statement';pp.save(p/'研究版本/档案.json',d);pub=pp.load(p/'研究版本/manifest.json');pub['files']['档案.json']=sha(p/'研究版本/档案.json');pp.save(p/'研究版本/manifest.json',pub);self.reseal(p)
  with self.assertRaisesRegex(ValueError,'AI内容'):check(p)
 def test_path_traversal_manifest_rejected(self):
  self.publish();p=Path(self.build()['folder']);m=pp.load(p/'manifest.json');m['files']['../outside']='bad';pp.save(p/'manifest.json',m)
  with self.assertRaises(ValueError):check(p)
if __name__=='__main__':unittest.main()
