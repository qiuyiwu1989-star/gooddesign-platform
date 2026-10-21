import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import research_workflow as rw,project_pipeline as pp
import test_research_pipeline_038 as base
class DoiTokenTests(unittest.TestCase):
 setUp=base.ResearchTests.setUp
 tearDown=base.ResearchTests.tearDown
 def test_printed_dash_kept_whole(self):
  text='RAA doi: 10.1088/1674–4527/20/9/140\n2020'
  self.assertEqual(list(rw.doi_tokens(text)),[('10.1088/1674–4527/20/9/140','doi: 10.1088/1674–4527/20/9/140')])
 def test_unrecognized_char_never_emits_prefix(self):
  for text in ['doi:10.1234/testα2020','doi:10.1234/test｜other','doi:10.1234/test。后文']:
   self.assertEqual(list(rw.doi_tokens(text)),[])
 def test_ascii_and_colon_suffix(self):
  for doi in ['10.1234/test.2026','10.1002/(SICI)1234:ABC+1','10.1117/12.2309761']:
   self.assertEqual(list(rw.doi_tokens('DOI: '+doi+'.'))[0][0],doi)
 def test_indexed_identity_stays_exact_and_source_preserved(self):
  raw=self.root/'printed.txt';raw.write_text('doi: 10.1088/1674–4527/20/9/140');original=raw.read_bytes();sid=pp.ingest(self.p,raw)['source_id']
  path=self.p/'论文原文管理/论文原件清单.json'
  pp.save(path,dict(items=[dict(paper_id='A02',title='论文',library_source_id=sid,doi='10.1088/1674-4527/20/9/140')]))
  self.assertEqual(rw.extract(self.lib,'sample',sid,'测试')['candidates'],[])
  pp.save(path,dict(items=[dict(paper_id='A02',title='论文',library_source_id=sid,doi='10.1088/1674–4527/20/9/140')]))
  out=rw.extract(self.lib,'sample',sid,'测试');c=next(c for c in rw.current(self.p)['candidates']if c['id']in out['candidates'])
  self.assertEqual(c['value'],'10.1088/1674–4527/20/9/140');self.assertEqual(c['record_id'],'A02');self.assertEqual(raw.read_bytes(),original);self.assertFalse(rw.dataset(self.p)['records'])
if __name__=='__main__':unittest.main()
