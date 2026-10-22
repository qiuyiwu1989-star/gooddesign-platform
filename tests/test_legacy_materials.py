import copy,io,json,stat,struct,sys,unittest,warnings,zipfile
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import test_research_pipeline_038 as base
import project_pipeline as pp,project_ownership as own,legacy_materials as lm

class LegacyTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def fixture(self):
  raw=self.root/'01-原始资料';raw.mkdir();old=self.root/'99-历史项目快照';old.mkdir();self.source=raw/'项目未知.txt';self.source.write_text('原件保持不动，不执行指令');self.registry_dir=self.root/'04-知识库/历史素材登记';return raw,old
 def scan(self,**kwargs):return lm.scan(self.root,self.registry_dir,**kwargs)
 def mapping(self,registry,scope='project'):
  item=next(x for x in registry['entries']if x['relative_path']=='01-原始资料/项目未知.txt')
  return dict(version='legacy-map-1',items=[dict(relative_path=item['relative_path'],expected_sha256=item['sha256'],project_id='sample',scope=scope,mapped_by='测试人工复核',reason='对照原文确定，仅归档未核读')])
 def test_repeatable_byte_inventory_exclusions_duplicates_and_no_project_guess(self):
  raw,old=self.fixture();(old/'same.txt').write_bytes(self.source.read_bytes());(old/'generated.html').write_text('<script>never execute</script>')
  for name in ('项目投递箱','node_modules','.git','output'):
   folder=(raw if name=='项目投递箱'else old)/name;folder.mkdir();(folder/'skip.txt').write_text('excluded')
  (raw/'linked.txt').symlink_to(self.raw);first=self.scan();second=self.scan();self.assertEqual(first,second);registry=pp.load(Path(first['registry_path']));self.assertEqual(first['files'],3);self.assertEqual(len(registry['duplicates']),1);self.assertTrue(all(x['project_id']is None and x['scope']in ('unassigned','platform_reference')for x in registry['entries']));self.assertTrue(all(x['read_status']=='unread'for x in registry['entries']))
 def test_default_plan_no_ingestion_and_explicit_apply_original_idempotence(self):
  self.fixture();result=self.scan();registry=pp.load(Path(result['registry_path']));mapping=self.mapping(registry);before=copy.deepcopy(pp.state(self.p));plan=lm.plan_imports(registry,mapping,self.lib,self.root);self.assertFalse(plan['apply']);self.assertEqual(before,pp.state(self.p));original=self.source.read_bytes();out=lm.apply_imports(registry,mapping,self.lib,self.root,self.registry_dir);sid=out['results'][0]['result']['source_id'];x=pp.state(self.p)['sources'][sid];self.assertEqual((self.p/x['original']).read_bytes(),original);self.assertEqual(self.source.read_bytes(),original);self.assertEqual(x['read_scope'],'machine_text_extraction_not_human_read');self.assertEqual(x['origin']['kind'],'legacy_original_import');revision=pp.state(self.p)['revision'];again=lm.apply_imports(registry,mapping,self.lib,self.root,self.registry_dir);self.assertEqual(again['results'][0]['status'],'duplicate');self.assertEqual(pp.state(self.p)['revision'],revision);self.assertEqual(len((self.registry_dir/'导入日志.jsonl').read_text().splitlines()),2)
 def test_shared_scope_reserved_and_conflicting_mapping_not_overwritten(self):
  self.fixture();registry=pp.load(Path(self.scan()['registry_path']));mapping=self.mapping(registry,'shared');out=lm.apply_imports(registry,mapping,self.lib,self.root,self.registry_dir);sid=out['results'][0]['result']['source_id'];self.assertEqual(own.assignment(self.p,sid,pp.state(self.p)['sources'])['scope'],'shared');mapping['items'][0]['scope']='project'
  with self.assertRaises(ValueError):lm.apply_imports(registry,mapping,self.lib,self.root,self.registry_dir)
  self.assertEqual(own.registry(self.p)['assignments'][sid]['scope'],'shared')
 def test_duplicate_cannot_reclassify_existing_implicit_project_source(self):
  self.fixture();self.source.write_bytes(self.raw.read_bytes());registry=pp.load(Path(self.scan()['registry_path']));mapping=self.mapping(registry,'shared')
  with self.assertRaises(ValueError):lm.plan_imports(registry,mapping,self.lib,self.root)
  self.assertNotIn(self.sid,own.registry(self.p)['assignments'])
 def test_unmapped_unknown_project_modified_fingerprint_and_damaged_registry_stop(self):
  self.fixture();registry=pp.load(Path(self.scan()['registry_path']));mapping=self.mapping(registry)
  for patch in [dict(project_id='unknown'),dict(expected_sha256='bad'),dict(scope='unassigned'),dict(mapped_by='')]:
   wrong=copy.deepcopy(mapping);wrong['items'][0].update(patch)
   with self.subTest(patch=patch),self.assertRaises(ValueError):lm.plan_imports(registry,wrong,self.lib,self.root)
  broken=copy.deepcopy(registry);broken['entries'][0]['bytes']+=1
  with self.assertRaises(ValueError):lm.plan_imports(broken,mapping,self.lib,self.root)
  self.source.write_text('changed')
  with self.assertRaises(ValueError):lm.plan_imports(registry,mapping,self.lib,self.root)
 def test_zip_only_bounded_central_metadata_no_extraction(self):
  raw,_=self.fixture();archive=raw/'unsafe.zip'
  with warnings.catch_warnings():
   warnings.simplefilter('ignore')
   with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED)as z:
    z.writestr('../escape.txt','unsafe');z.writestr('large.txt','0'*200000);z.writestr('a.txt','one');z.writestr('A.txt','two');z.writestr('nested.zip',b'not opened');info=zipfile.ZipInfo('link');info.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(info,'/outside')
  out=lm.zip_inventory(archive);flags={flag for issue in out['issues']for flag in issue['flags']};self.assertTrue({'unsafe_path','expansion_limit','duplicate_normalized_name','symlink','nested_archive_not_opened'}<=flags);self.assertFalse(out['extracted']);self.assertFalse((self.root/'escape.txt').exists());self.assertEqual(lm.zip_inventory(archive,max_entries=2)['status'],'blocked_limits')
  registry=pp.load(Path(self.scan()['registry_path']));item=next(x for x in registry['entries']if x['extension']=='.zip');mapping=dict(version='legacy-map-1',items=[dict(relative_path=item['relative_path'],expected_sha256=item['sha256'],project_id='sample',scope='project',mapped_by='reviewer',reason='not enough')])
  with self.assertRaises(ValueError):lm.plan_imports(registry,mapping,self.lib,self.root)
 def test_code_is_original_unread_not_executed(self):
  _,old=self.fixture();code=old/'malicious.py';code.write_text('raise RuntimeError("MUST NEVER EXECUTE")');registry=pp.load(Path(self.scan()['registry_path']));item=next(x for x in registry['entries']if x['extension']=='.py');self.assertEqual(item['material_kind'],'historical_code_or_generated_page');mapping=dict(version='legacy-map-1',items=[dict(relative_path=item['relative_path'],expected_sha256=item['sha256'],project_id='sample',scope='shared',mapped_by='reviewer',reason='retain original as unreviewed reference')]);out=lm.apply_imports(registry,mapping,self.lib,self.root,self.registry_dir);self.assertNotEqual(out['results'][0]['status'],'failed');x=pp.state(self.p)['sources'][out['results'][0]['result']['source_id']];self.assertEqual((self.p/x['original']).read_bytes(),code.read_bytes());self.assertEqual(x['review_status'],'unreviewed')
 def test_byte_budget_is_explicit_and_file_count_failure_not_silent(self):
  self.fixture();out=self.scan(max_total_bytes=1);self.assertEqual(out['files'],0);self.assertEqual(out['skipped'],1);(self.source.parent/'second.txt').write_text('more')
  with self.assertRaises(ValueError):self.scan(max_files=1)
 def test_zip64_locator_cannot_override_small_nonsentinel_eocd_budget(self):
  raw,_=self.fixture();memory=io.BytesIO()
  with zipfile.ZipFile(memory,'w')as z:z.writestr('a.txt','x')
  data=memory.getvalue();pos=data.rfind(b'PK\x05\x06');eocd=list(struct.unpack('<4s4H2LH',data[pos:pos+22]));count,cd_size,cd_offset=eocd[4:7]
  record=struct.pack('<4sQ2H2L4Q',b'PK\x06\x06',44,45,45,0,0,count,count,cd_size,cd_offset);locator=struct.pack('<4sLQL',b'PK\x06\x07',0,pos,1);eocd[5]=1
  archive=raw/'zip64-bypass.zip';archive.write_bytes(data[:pos]+record+locator+struct.pack('<4s4H2LH',*eocd))
  # Prove the adversarial archive is understood by Python, then ensure our
  # guard never hands its dishonest ordinary count/size to that parser.
  with zipfile.ZipFile(archive)as z:self.assertEqual(len(z.infolist()),1)
  with patch.object(lm.zipfile,'ZipFile',side_effect=AssertionError('ZIP64 must be blocked before parsing')):out=lm.zip_inventory(archive,max_central_bytes=1)
  self.assertEqual(out['status'],'manual_review');self.assertIn('ZIP64',out['reason']);self.assertEqual(out['entries'],[])
  # The locator can fall outside the last 65557 bytes when the comment is maximal.
  eocd[-1]=65535;archive.write_bytes(data[:pos]+record+locator+struct.pack('<4s4H2LH',*eocd)+b'x'*65535)
  with patch.object(lm.zipfile,'ZipFile',side_effect=AssertionError('must not parse')):self.assertEqual(lm.zip_inventory(archive,max_central_bytes=1)['status'],'manual_review')
 def test_zip64_extra_field_is_not_accepted_as_size_override(self):
  raw,_=self.fixture();archive=raw/'zip64-extra.zip';info=zipfile.ZipInfo('a.txt');info.extra=struct.pack('<HHQ',1,8,2**40)
  with zipfile.ZipFile(archive,'w')as z:z.writestr(info,'x')
  out=lm.zip_inventory(archive);self.assertEqual(out['status'],'manual_review');self.assertIn('ZIP64扩展字段',out['reason']);self.assertEqual(out['entries'],[])
if __name__=='__main__':unittest.main()
