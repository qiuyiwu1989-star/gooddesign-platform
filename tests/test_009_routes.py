import unittest,tempfile,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_explore import build
class RouteCoverage(unittest.TestCase):
 def test_every_route_stop_has_deep_content(self):
  with tempfile.TemporaryDirectory() as t:
   _,routes=build(Path(t));data=json.loads((Path(t)/'explore/deep.json').read_text())
   self.assertEqual(set(data),{s['id'] for r in routes for s in r['stops']})
   self.assertEqual(sum(len(x['fields']) for x in data.values()),24)
if __name__=='__main__':unittest.main()
