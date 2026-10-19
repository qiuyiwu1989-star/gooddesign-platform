# coding: utf-8
"""015: immutable snapshots, additions/removals, and honest quality statistics."""
import copy,json,shutil,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from dossier_governance import DEFAULT,capture,differences,normalized,quality,read,save,snapshot,verify

class GovernanceTests(unittest.TestCase):
 def setUp(self):
  (ROOT/'tmp').mkdir(exist_ok=True)
  self.tmp=tempfile.TemporaryDirectory(prefix='015-test-',dir=str(ROOT/'tmp'));self.p=Path(self.tmp.name)
  for name in ['档案数据.json','主档案结构.json','原子字段档案.json','研究日志.json','字段规范.json','质量评估依据.json','质量评估.json']:shutil.copy2(DEFAULT/name,self.p/name)
  shutil.copytree(DEFAULT/'来源卡',self.p/'来源卡')
 def tearDown(self):self.tmp.cleanup()
 def freeze(self,v):return snapshot(self.p,v,'isolated test fixture','unit test')
 def mutate(self):
  d=read(self.p/'原子字段档案.json');d['records'][0]['cells']['canonical_name']['value']='测试修订，不是项目事实';save(self.p/'原子字段档案.json',d)
 def test_idempotence_and_no_empty_revision(self):
  self.freeze('1.0.0');self.freeze('1.0.0');r=self.freeze('1.0.1');self.assertEqual(r['version'],'1.0.0');self.assertEqual(len(verify(self.p)['versions']),1)
 def test_refuses_overwrite_or_missing_reason(self):
  with self.assertRaises(ValueError):snapshot(self.p,'1.0.0','','test')
  self.freeze('1.0.0');self.mutate()
  with self.assertRaises(AssertionError):self.freeze('1.0.0')
 def test_add_remove_and_replace_preserve_old_values(self):
  old={'events':[{'id':'E1','value':'old'},{'id':'E2','value':'retained history'}]}
  new={'events':[{'id':'E1','value':'new'},{'id':'E3','value':'added'}]}
  diff=differences(normalized(old),normalized(new));self.assertEqual({c['operation'] for c in diff},{'add','remove','replace'})
  self.assertEqual(next(c for c in diff if c['operation']=='remove')['before']['value'],'retained history')
 def test_two_versions_and_restore_as_new_revision(self):
  self.freeze('1.0.0');original=read(self.p/'原子字段档案.json');self.mutate();self.freeze('1.0.1')
  changes=read(self.p/'版本/1.0.1/changes.json');self.assertTrue(any(c['path'].endswith('/canonical_name/value')for c in changes))
  save(self.p/'原子字段档案.json',original);self.freeze('1.0.2');self.assertEqual(verify(self.p)['latest'],'1.0.2')
  self.assertEqual(read(self.p/'版本/1.0.0/snapshot.json')['atomic'],original)
 def test_rejects_duplicate_ids(self):
  d=read(self.p/'原子字段档案.json');d['records'].append(copy.deepcopy(d['records'][0]));save(self.p/'原子字段档案.json',d)
  with self.assertRaises(AssertionError):self.freeze('1.0.0')
 def test_detects_corrupt_snapshot_and_manifest(self):
  self.freeze('1.0.0');f=self.p/'版本/1.0.0/snapshot.json';d=read(f);d['atomic']['project_id']='tampered';save(f,d)
  with self.assertRaises(AssertionError):verify(self.p)
 def test_detects_corrupt_reason(self):
  self.freeze('1.0.0');f=self.p/'版本/1.0.0/manifest.json';d=read(f);d['reason']='tampered';save(f,d)
  with self.assertRaises(AssertionError):verify(self.p)
 def test_quality_does_not_improve_just_from_more_records(self):
  a=quality(self.p);d=read(self.p/'原子字段档案.json');r=copy.deepcopy(d['records'][0]);r['id']='TEST-UNKNOWN'
  for c in r['cells'].values():c.update(value=None,value_state='not_researched',source_ids=[],claim_ids=[])
  d['records'].append(r);save(self.p/'原子字段档案.json',d);b=quality(self.p)
  self.assertEqual(a['score'],b['score']);self.assertLess(b['metrics']['registration_coverage'],a['metrics']['registration_coverage']);self.assertFalse(b['gates']['expert_review_complete'])
 def test_unassessed_dimension_keeps_total_unknown(self):
  b=read(self.p/'质量评估依据.json');b['dimensions'][0]['level']=None;save(self.p/'质量评估依据.json',b);q=quality(self.p);self.assertIsNone(q['score']);self.assertIsNone(q['dimensions'][0]['points'])
 def test_mcp_contract_is_read_only_and_explicitly_draft(self):
  c=read(ROOT/'04-知识库/项目档案标准-v1/MCP只读调用契约-v0.1.json');self.assertIn('design_only',c['implementation_status'])
  self.assertEqual(len({x['name']for x in c['tools']}),7)
  for t in c['tools']:
   self.assertTrue(t['annotations']['readOnlyHint']);self.assertEqual(t['inputSchema']['type'],'object');self.assertIn('revision',t['outputSchema']['properties'])

if __name__=='__main__':unittest.main()
