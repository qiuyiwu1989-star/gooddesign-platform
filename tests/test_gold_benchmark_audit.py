# coding: utf-8
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import gold_benchmark_audit as audit
import project_pipeline as pp

class BenchmarkAuditTests(unittest.TestCase):
 def setUp(self):
  base=ROOT/'output/research-051/quality-tests';base.mkdir(parents=True,exist_ok=True)
  self.temp=tempfile.TemporaryDirectory(dir=base);self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.lib=self.root/'library';self.lib.mkdir();self.p=self.lib/'demo-01';self.p.mkdir();self.row=dict(id='demo-01',path='demo-01',name='测试金奖项目',year=2025,award='金奖')
  pp.save(self.lib/'项目索引.json',dict(projects=[self.row,dict(id='silver-01',name='银奖不混入',award='银奖')]))
  self.text='Demo project gold technical principle and constraints. Test evidence.'
  self.raw=self.p/'来源/S1/original.txt';self.raw.parent.mkdir(parents=True);self.raw.write_text(self.text);(self.raw.parent/'可读来源.md').write_text(self.text)
  self.blocks=[dict(id='B0001',text=self.text,locator='正文')];pp.save(self.raw.parent/'chunks.json',self.blocks)
  self.source=dict(id='S1',original='来源/S1/original.txt',document='来源/S1/可读来源.md',chunks='来源/S1/chunks.json',sha256=pp.sha(self.raw.read_bytes()),chunks_sha256=pp.sha((self.raw.parent/'chunks.json').read_bytes()),chunk_count=1,status='text_extracted',origin=dict(kind='web',url='https://example.org/project'))
  pp.save(self.p/'数据/管道状态.json',dict(project=self.row,sources={'S1':self.source},revision=1))
  self.evidence=dict(source_id='S1',source_sha256=self.source['sha256'],chunks_path=self.source['chunks'],chunks_sha256=self.source['chunks_sha256'],chunk_id='B0001',quote='Demo project',quote_sha256=pp.sha(b'Demo project'))
 def known(self,value,evidence=True):
  cell=dict(value=value,value_state='known',content_nature='source_statement')
  if evidence:cell['evidence']=copy.deepcopy(self.evidence)
  return cell
 def record(self,rid,entity,**fields):return dict(id=rid,project_id='demo-01',entity=entity,title=rid,cells={k:self.known(v)for k,v in fields.items()})
 def publish(self,records=None,n=1,**changes):
  d=dict(project_id='demo-01',publication_revision='research-%06d'%n,records=records or[self.record('PROJECT','project',canonical_name='Demo project')],interpretations=[],expert_reviewed=False);d.update(changes)
  dest=self.p/'研究工作区/版本'/d['publication_revision'];dest.mkdir(parents=True,exist_ok=True);pp.save(dest/'档案.json',d)
  pp.save(dest/'manifest.json',dict(revision=d['publication_revision'],files={'档案.json':pp.sha((dest/'档案.json').read_bytes())},previous_manifest_sha256=pp.sha((dest.parent/('research-%06d'%(n-1))/'manifest.json').read_bytes())if n>1 else None))
  pp.save(self.p/'研究工作区/工作状态.json',dict(revision=n,candidates=[],events=[]));return d
 def files(self):return {str(p.relative_to(self.lib)):pp.sha(p.read_bytes())for p in self.lib.rglob('*')if p.is_file()}
 def test_downloads_not_research_completion(self):
  before=self.files();r=audit.audit(self.lib,drafts_root=self.root/'drafts');p=r['projects'][0]
  self.assertEqual(r['summary']['catalog_gold_projects'],1);self.assertEqual(p['source_counts']['project_originals'],1);self.assertFalse(p['statuses']['research_readable']);self.assertFalse(p['statuses']['benchmark_candidate']);self.assertIsNone(p['quality_score']);self.assertEqual(before,self.files())
 def test_pending_original_not_project_proof(self):
  pp.save(self.p/'资料归属.json',dict(version=1,assignments={'S1':dict(scope='pending')},url_rules={}))
  p=audit.audit_project(self.lib,self.row)
  self.assertEqual(p['source_counts']['pending'],1);self.assertEqual(p['source_counts'].get('project_originals',0),0);self.assertEqual(p['gates']['originals']['status'],'pending_or_missing')
 def test_no_current_or_mutation(self):
  self.publish();before=self.files()
  with patch.object(audit.rw,'current',side_effect=AssertionError('must never recover')):
   r=audit.audit(self.lib,drafts_root=self.root/'drafts')
  self.assertEqual(r['summary']['with_published_revision'],1);self.assertEqual(before,self.files())
 def test_older_version_tampering_is_detected(self):
  self.publish();self.publish(n=2);file=self.p/'研究工作区/版本/research-000001/档案.json';file.write_text('{}')
  p=audit.audit_project(self.lib,self.row);self.assertEqual(p['gates']['published_version']['status'],'invalid');self.assertFalse(p['statuses']['research_readable'])
 def test_newer_folder_does_not_advance_pointer(self):
  self.publish();pointer=self.p/'研究工作区/工作状态.json';old=pointer.read_bytes();self.publish(n=2);pointer.write_bytes(old)
  r=audit.audit_project(self.lib,self.row)
  self.assertEqual(r['publication_revision'],'research-000001');self.assertEqual(pointer.read_bytes(),old);self.assertEqual(r['gates']['published_version']['status'],'attention')
 def test_legacy_references_are_not_frozen_evidence(self):
  r=self.record('PROJECT','project',canonical_name='Demo project');r['cells']['canonical_name']=self.known('Demo project',False);self.publish([r],quality_score=99,expert_reviewed=True)
  p=audit.audit_project(self.lib,self.row);self.assertEqual(p['facts']['legacy_or_unfrozen_known_cells'],1);self.assertFalse(p['statuses']['frozen_evidence_traceable']);self.assertFalse(p['expert_reviewed']);self.assertIsNone(p['quality_score']);self.assertFalse(p['statuses']['professionally_approved'])
 def test_same_team_patent_is_not_confirmed_project_result(self):
  for relation in ['same_team','同团队相关专利，尚未确认型号采用','pending',{'invalid':'type'}]:
   records=[self.record('P1','patent',title='Related patent',publication_number='CN000000001A',project_relation=relation,relation_evidence='Same team only')]
   gate=audit._relation_gate(records,'patent');self.assertEqual(gate['confirmed_relation_records'],[]);self.assertEqual(gate['status'],'candidate_relations_not_confirmed')
 def test_ai_only_does_not_fill_fact_depth(self):
  self.publish(interpretations=[dict(entity='innovation',record_id='AI1',value='an idea',content_nature='ai_interpretation',conditions='test first',limitations='not adopted',**self.evidence)])
  p=audit.audit_project(self.lib,self.row);module=next(x for x in p['modules']if x['key']=='innovation')
  self.assertEqual(module['state'],'ai_only_not_fact_depth');self.assertEqual(module['known_fact_records'],0);self.assertEqual(p['gates']['mechanisms_constraints']['status'],'incomplete')
 def test_zero_known_metric_requires_context_unknown_zero_not_known(self):
  self.publish([self.record('M1','metric',value=0),self.record('PROJECT','project',canonical_name='Demo project')]);p=audit.audit_project(self.lib,self.row)
  self.assertEqual(p['metric_context_gaps'],[dict(record_id='M1',missing=['subject','unit','conditions'])]);self.assertFalse(audit._known(dict(value=0,value_state='unknown')))
 def test_depth_gap_is_actionable_not_score(self):
  self.publish();baseline=[dict(key=k,label=l,known_fact_records=1,known_fact_cells=2,ai_items=1)for k,l,_ in audit.MODULES]
  p=audit.audit_project(self.lib,self.row,baseline);self.assertTrue(any('需求与系统' in x for x in p['depth_gaps_to_benchmark']));self.assertTrue(p['next_actions']);self.assertNotIn('quality_percent',p)
 def make_draft(self,pid='demo-01'):
  folder=self.root/'drafts'/pid/'job-1';folder.mkdir(parents=True)
  for name in audit.DRAFT_FILES:(folder/name).write_text(json.dumps(dict(valid_candidates=[{}],rejected_candidates=[]))if name=='校验结果.json'else'{}')
  m=dict(schema='gold-deep-draft-1.0',project_id=pid,status='draft_ready_for_review',expert_reviewed=False,published=False,created_at='2026-10-23T00:00:00Z',files={name:pp.sha((folder/name).read_bytes())for name in audit.DRAFT_FILES});pp.save(folder/'manifest.json',m);return folder
 def test_draft_integrity_separate_from_publication(self):
  self.make_draft();r=audit.audit(self.lib,drafts_root=self.root/'drafts');p=r['projects'][0]
  self.assertTrue(p['draft']['ready']);self.assertEqual(r['summary']['draft_ready'],1);self.assertFalse(p['statuses']['research_readable']);self.assertEqual(r['summary']['with_published_revision'],0)
 def test_tampered_or_self_approved_draft_not_counted(self):
  folder=self.make_draft();(folder/'模型草稿.json').write_text('tampered');self.assertFalse(audit.read_draft_status(self.root/'drafts','demo-01')['ready'])
  folder=self.make_draft('demo-02');manifest=audit._load(folder/'manifest.json');manifest['expert_reviewed']=True;pp.save(folder/'manifest.json',manifest);self.assertFalse(audit.read_draft_status(self.root/'drafts','demo-02')['ready'])
 def test_draft_path_escape_rejected(self):
  with self.assertRaises(ValueError):audit.read_draft_status(self.root/'drafts','../../escape')
 def test_no_untrusted_source_path_read(self):
  state=pp.load(self.p/'数据/管道状态.json');state['sources']['S1']['original']='../../outside';pp.save(self.p/'数据/管道状态.json',state)
  p=audit.audit_project(self.lib,self.row);self.assertEqual(p['source_counts']['invalid_source_metadata'],1)
if __name__=='__main__':unittest.main()
