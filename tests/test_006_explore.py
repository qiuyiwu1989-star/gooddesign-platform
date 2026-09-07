import unittest,tempfile,json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_explore import build,SRC
class ExploreTests(unittest.TestCase):
 def test_records_routes_and_sources(self):
  with tempfile.TemporaryDirectory() as t:
   rows,routes=build(Path(t));self.assertEqual(len(rows),560);self.assertEqual(len({r['id'] for r in rows}),560)
   self.assertEqual(sum(r['description_status']=='missing' for r in rows),96)
   for r in rows:
    for k in ['project_url','source_url','lesson_url','cover']:
     if r[k]:self.assertTrue((SRC/r[k].lstrip('/')).is_file(),(r['id'],k))
   self.assertEqual(len(routes),3)
   for r in routes:
    for s in r['stops']:
     raw=(SRC/f"cases/detail/{s['id']}.json").read_bytes();e=s['evidence']
     self.assertEqual(hashlib.sha256(raw).hexdigest(),e['sha256'])
     self.assertEqual(json.loads(raw)[e['field']][e['start']:e['end']],e['excerpt'])
     self.assertTrue(s['task'] and s['look'] and s['reflect'])
 def test_build_idempotent_and_home_untouched(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);(p/'index.html').write_text('original')
   for name in ['hall.html','award.html']:(p/name).write_text('<header>original</header>')
   build(p);build(p)
   self.assertEqual((p/'index.html').read_text(),'original')
   for name in ['hall.html','award.html']:self.assertEqual((p/name).read_text().count('id="explore-entry"'),1)
if __name__=='__main__':unittest.main()
