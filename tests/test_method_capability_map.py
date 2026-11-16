import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_method_capability_map as capability
import method_library_catalog


class MethodCapabilityMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = capability.build()
        cls.methods = {m['research_id']: m for m in cls.data['methods']}

    def test_all_64_methods_have_unique_valid_routes(self):
        self.assertEqual(len(self.methods), 64)
        self.assertEqual(set(self.methods), set(capability.METHOD_MAP))
        self.assertEqual(set(capability.CAPABILITIES), {m['primary_capability'] for m in self.methods.values()})
        for rid, method in self.methods.items():
            with self.subTest(method=rid):
                self.assertTrue(method['engine_stages'])
                self.assertIn(method['primary_capability'], capability.CAPABILITIES)
                self.assertTrue(all(stage in capability.STAGES for stage in method['engine_stages']))
                self.assertTrue(all(c in capability.CAPABILITIES for c in method['secondary_capabilities']))
                for relation in method['relations']:
                    self.assertIn(relation['target_research_id'], self.methods)

    def test_levels_reflect_actual_contracts_and_research_only_status(self):
        self.assertEqual({rid for rid, m in self.methods.items() if m['skill_level'] == 'S2'}, capability.CONTRACT_IDS)
        self.assertEqual({rid for rid, m in self.methods.items() if m['skill_level'] == 'S0'}, {'WB02', 'WB05', 'WB11'})
        self.assertEqual(sum(m['skill_level'] == 'S1' for m in self.methods.values()), 55)
        for rid, method in self.methods.items():
            if rid in capability.CONTRACT_IDS:
                self.assertIsNotNone(method['contract_ref'])
            else:
                self.assertIsNone(method['contract_ref'])

    def test_inputs_outputs_and_content_hashes_come_from_dossiers(self):
        for rid, method in self.methods.items():
            with self.subTest(method=rid):
                source = method_library_catalog.read(rid)
                catalog_row = next(r for r in method_library_catalog.catalog()['methods'] if r['research_id'] == rid)
                self.assertEqual(method['content_ref']['sha256'], catalog_row['sha256'])
                self.assertEqual(method['dossier_inputs'], [{'key': i['key'], 'required': i['required']} for i in source['inputs']])
                self.assertEqual(method['dossier_outputs'], [o['key'] for o in source['outputs']])
                self.assertEqual(method['relations'], source['relations'])
                self.assertEqual(method['review_status'], source['review_status'])
                self.assertEqual(method['validation_status'], source['validation_status'])

    def test_six_contract_outputs_match_frozen_artifact_types(self):
        for rid in capability.CONTRACT_IDS:
            contract = json.loads((capability.CONTRACTS / rid / 'contract.json').read_text())
            self.assertEqual(self.methods[rid]['logical_outputs'], [contract['artifact_type']])
            self.assertEqual(self.methods[rid]['contract_ref']['version'], contract['contract_version'])

    def test_representative_engine_routes(self):
        self.assertEqual(self.methods['R48']['primary_capability'], 'problem_framing')
        self.assertEqual(self.methods['R14']['logical_outputs'], ['FunctionModel'])
        self.assertEqual(self.methods['R17']['engine_stages'], ['S6', 'S7'])
        self.assertEqual(self.methods['R36']['logical_outputs'], ['ComparisonRecord'])
        self.assertEqual(self.methods['R44']['logical_outputs'], ['PrototypePlan'])
        self.assertEqual(self.methods['R42']['logical_outputs'], ['VerificationPlan'])
        self.assertEqual(self.methods['R52']['primary_capability'], 'research_prioritization')
        self.assertEqual(self.methods['R52']['engine_stages'], ['S8', 'S9'])
        self.assertEqual(self.methods['WB11']['primary_capability'], 'method_governance')

    def test_research_methods_do_not_replace_case_retrieval_or_learning_store(self):
        self.assertEqual(self.methods['R08']['engine_stages'], ['S1'])
        self.assertEqual(self.methods['WB02']['engine_stages'], ['S1'])
        self.assertEqual(self.data['stage_index']['S10'], [])
        for rid in ('R18', 'R27', 'R46'):
            self.assertIn('S4', self.methods[rid]['engine_stages'])

    def test_generated_outputs_are_deterministic_and_current(self):
        first = capability.rendered()
        self.assertEqual(first, capability.rendered())
        json_text, md_text = first
        self.assertEqual((capability.OUTPUT / '能力地图.json').read_text(encoding='utf-8'), json_text)
        self.assertEqual((capability.OUTPUT / '能力矩阵.md').read_text(encoding='utf-8'), md_text)
        self.assertEqual(len(json.loads(json_text)['methods']), 64)
        rows = [line for line in md_text.splitlines() if line.startswith('| R') or line.startswith('| WB')]
        self.assertEqual(len(rows), 64)


if __name__ == '__main__':
    unittest.main()
