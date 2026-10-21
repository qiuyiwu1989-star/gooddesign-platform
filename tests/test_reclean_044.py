# coding: utf-8
import sys,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import test_research_pipeline_038 as base
import project_pipeline as pp,research_workflow as rw
from source_reclean import reclean
from archive_steward import Steward
class RecleanTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def html_source(self):
  f=self.root/'table.html';f.write_text('<h1>试验</h1><p>DOI:10.1234/table</p><table><tr><th>压力</th><th>转速</th></tr><tr><td>286</td><td>100</td></tr></table><script>坏指令</script>');return pp.ingest(self.p,f)['source_id']
 def test_boundaries_and_immutable_original_derivative(self):
  sid=self.html_source();before=pp.state(self.p)['sources'][sid];path=self.p/before['chunks'];original=path.read_bytes();raw=(self.p/before['original']).read_bytes();s=Steward(self.lib,self.inbox);old=s.enqueue_source('sample',sid)
  r=reclean(self.lib,'sample',sid);after=pp.state(self.p)['sources'][sid];text='\n'.join(b['text']for b in pp.load(self.p/after['chunks']));self.assertIn('286 | 100 |',text);self.assertIn('压力 | 转速 |',text);self.assertNotIn('坏指令',text);self.assertEqual(path.read_bytes(),original);self.assertEqual((self.p/after['original']).read_bytes(),raw);self.assertNotEqual(old['id'],s.enqueue_source('sample',sid)['id']);self.assertEqual(reclean(self.lib,'sample',sid)['status'],'no_changes')
 def test_published_old_evidence_remains_readable(self):
  sid=self.html_source();x=pp.state(self.p)['sources'][sid];b=pp.load(self.p/x['chunks'])[0];c=rw.propose(self.lib,'sample',dict(entity='paper',record_id='A02',field='doi',value='10.1234/table',source_id=sid,chunk_id=b['id'],quote='DOI:10.1234/table'),'研究员');rw.review(self.lib,'sample',c['id'],'approved','人','核对');rw.publish(self.lib,'sample','人','基线');reclean(self.lib,'sample',sid);rw.check_version(self.p,'research-000001');cell=rw.cell(rw.dataset(self.p),'A02','doi');e=cell['evidence'];self.assertEqual(e['chunks_sha256'],pp.sha((self.p/e['chunks_path']).read_bytes()));self.assertEqual(cell['value'],'10.1234/table')
 def test_non_html_rejected(self):
  with self.assertRaises(ValueError):reclean(self.lib,'sample',self.sid)
 def test_saved_derivative_recovers_after_commit_interruption(self):
  sid=self.html_source();old=pp.state(self.p)['sources'][sid]['chunks']
  with patch.object(pp,'commit',side_effect=OSError('模拟掉盘')):
   with self.assertRaises(OSError):reclean(self.lib,'sample',sid)
  self.assertEqual(pp.state(self.p)['sources'][sid]['chunks'],old)
  self.assertEqual(reclean(self.lib,'sample',sid)['status'],'text_extracted');self.assertNotEqual(pp.state(self.p)['sources'][sid]['chunks'],old)
if __name__=='__main__':unittest.main()
