# coding: utf-8
import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import project_pipeline as pp,project_ownership as own,file_admin as fa
class OwnershipTests(unittest.TestCase):
 def setUp(self):
  (ROOT/'tmp/ownership-tests').mkdir(parents=True,exist_ok=True);self.tmp=tempfile.TemporaryDirectory(dir=str(ROOT/'tmp/ownership-tests'));self.r=Path(self.tmp.name);self.lib=self.r/'lib';self.inbox=self.r/'inbox';self.lib.mkdir();cat=self.r/'catalog.json'
  pp.save(cat,dict(projects=[dict(id='case-a',name='项目A',year=2025,award='金奖',unit='单位A'),dict(id='case-b',name='项目B',year=2015,award='银奖',unit='单位B')]))
  pp.bootstrap(self.lib,self.inbox,cat,self.r/'archive');self.p=self.lib/'case-a';self.ids={}
  for name in ['own','foreign','shared','child']:
   file=self.inbox/'case-a'/(name+'.txt');file.write_text(name+' original material');origin=dict(kind='local_drop',filename=name+'.txt')
   if name=='child':origin['parent_source_id']=self.ids['foreign']
   self.ids[name]=pp.ingest(self.p,file,origin)['source_id']
  self.prior='ingest-%06d'%pp.state(self.p)['revision']
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={self.ids['foreign']:dict(scope='reassigned',owner_project='case-b',reason='项目B材料'),self.ids['shared']:dict(scope='shared',owner_project=None,reason='公共制度')},url_rules={'https://public.example/background':dict(scope='shared',owner_project=None,reason='公共背景')}))
  pp.commit(self.p,pp.state(self.p),'correct ownership')
 def tearDown(self):self.tmp.cleanup()
 def test_current_reading_and_documents_exclude_foreign_and_derived(self):
  d=pp.read_project(self.lib,'case-a',level='sources');self.assertEqual([x['id']for x in d['data']],[self.ids['own']])
  self.assertEqual(d['ownership_scope'],'current_project');doc=pp.read_project(self.lib,'case-a',level='document',document='library')['data'];self.assertNotIn('foreign.txt',doc);self.assertNotIn('child.txt',doc)
  with self.assertRaises(ValueError):pp.read_project(self.lib,'case-a',level='source',source_id=self.ids['foreign'])
 def test_historical_source_stays_reproducible_and_explicit(self):
  d=pp.read_project(self.lib,'case-a',level='sources',revision=self.prior);self.assertEqual(len(d['data']),4);self.assertEqual(d['ownership_scope'],'historical_unfiltered')
  d=pp.read_project(self.lib,'case-a',level='source',source_id=self.ids['foreign'],revision=self.prior);self.assertIn('foreign original',d['data'][0]['text'])
 def test_file_scope_applies_to_download_as_well_as_list(self):
  store=fa.Store(self.lib,self.inbox)
  try:
   self.assertEqual(len(store.files('case-a')['files']),1);self.assertEqual(store.files('case-a')['ownership_counts']['reassigned'],2)
   with self.assertRaises(ValueError):store.asset('case-a',self.ids['foreign'],'original')
   path,_=store.asset('case-a',self.ids['foreign'],'original',scope='reassigned');self.assertTrue(path.exists())
   self.assertEqual(len(store.files('case-a','shared')['files']),1)
   with self.assertRaises(ValueError):store.files('case-a','invalid')
  finally:store.pool.shutdown()
 def test_url_rule_covers_future_import_without_keywords(self):
  file=self.inbox/'case-a/new.txt';file.write_text('背景资料');sid=pp.ingest(self.p,file,dict(kind='web',url='https://public.example/background'))['source_id'];s=pp.state(self.p)
  self.assertEqual(own.assignment(self.p,sid,s['sources'])['scope'],'shared');self.assertEqual(pp.read_project(self.lib,'case-a')['data']['source_count'],1)
 def test_project_metadata_has_real_year_award_and_unit(self):
  rows=pp.load(self.lib/'项目索引.json')['projects'];self.assertEqual(rows[0]['year'],2025);self.assertEqual(rows[1]['award'],'银奖');self.assertEqual(rows[0]['unit'],'单位A')
 def test_frozen_ownership_does_not_drift_after_later_correction(self):
  frozen='ingest-%06d'%pp.state(self.p)['revision'];reg=own.registry(self.p);reg['version']=2;reg['assignments'][self.ids['own']]=dict(scope='shared',owner_project=None,reason='后来更正为公共参考');pp.save(self.p/'资料归属.json',reg)
  self.assertEqual(pp.read_project(self.lib,'case-a')['data']['source_count'],0)
  before=pp.read_project(self.lib,'case-a',revision=frozen);self.assertEqual(before['data']['source_count'],1);self.assertEqual(before['ownership_scope'],'frozen_project')
 def test_duplicate_upload_cannot_restore_corrected_foreign_file(self):
  store=fa.Store(self.lib,self.inbox)
  try:
   with self.assertRaises(ValueError):store.upload('case-a','same.txt',b'foreign original material')
  finally:store.pool.shutdown()
 def test_inheritance_cycle_rejected(self):
  with self.assertRaises(ValueError):own.assignment(self.p,'a',{'a':{'origin':{'parent_source_id':'b'}},'b':{'origin':{'parent_source_id':'a'}}},dict(assignments={},url_rules={}))
if __name__=='__main__':unittest.main()
