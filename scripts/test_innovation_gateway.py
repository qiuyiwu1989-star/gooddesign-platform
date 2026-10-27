import unittest,tempfile,json
from pathlib import Path
from unittest.mock import patch
import innovation_gateway as g
class GatewayTest(unittest.TestCase):
 def test_packet_binds_two_libraries_and_does_not_save(self):
  with patch.object(g,'RUNS',Path('/not-created-by-read')):
   x=g.prepare('教学研究：寻找降低表面损伤的启发，载荷未知。',['2025-04'],['R48','R14'],['抛光'])
  self.assertEqual(g.digest(x['packet']),x['packet_sha256']);self.assertEqual(len(x['packet']['method_versions']),2);self.assertFalse(x['packet']['engineering_validated']);self.assertEqual(x['packet']['model_calls'],0)
  p=x['packet']['project_versions'][0];self.assertTrue(p['dataset_sha256']);self.assertTrue(all(h['revision']==p['revision']for h in p['evidence_hits']))
 def test_invalid_scope_aliases_and_read_path(self):
  for kw in [dict(project_ids=[]),dict(project_ids=['2025-04'],method_ids=['R48','IM-PD-001']),dict(project_ids=['2025-04'],keywords=[''])]:
   with self.assertRaises(ValueError):g.prepare('问题',**kw)
  with self.assertRaises(ValueError):g.read_run('../secret')
  with self.assertRaises(ValueError):g.read_method('UNKNOWN')
 def test_save_read_and_tamper_detection(self):
  base=g.ROOT/'output/innovation-unified-tests';base.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=base)as folder,patch.object(g,'RUNS',Path(folder)):
   x=g.start('教学计划，尚无工程验证。',['2025-04'],['R48']);d=g.read_run(x['run_id']);self.assertEqual(x['packet_sha256'],d['packet_sha256'])
   p=Path(folder)/(x['run_id']+'.json');d['packet']['problem']='tampered';p.write_text(json.dumps(d))
   with self.assertRaises(ValueError):g.read_run(x['run_id'])
 def test_gateway_requires_explicit_evidence_version(self):
  from innovation_gateway_mcp import inno_read_evidence,inno_read_project
  for revision in ['','current_ingest','../secret']:
   with self.assertRaises(ValueError):inno_read_evidence('2025-04','anything',revision)
  with self.assertRaises(ValueError):inno_read_project('2025-04',revision='')
 def test_gateway_rejects_oversized_query_unknown_fields(self):
  from innovation_gateway_mcp import inno_search_projects,inno_read_project
  with self.assertRaises(ValueError):inno_search_projects('x'*201)
  with self.assertRaises(ValueError):inno_read_project('2025-04',section='records',fields=['not_a_field'])
  with self.assertRaises(ValueError):inno_read_project('2025-04',entity='UNKNOWN')
 def test_unknown_section_and_size(self):
  with self.assertRaises(ValueError):g.read_method('R48','execute')
  with self.assertRaises(ValueError):g.bounded({'x':'汉'*50000})
if __name__=='__main__':unittest.main()
