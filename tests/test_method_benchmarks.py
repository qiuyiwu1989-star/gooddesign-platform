import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build_method_benchmarks as benchmarks


class MethodBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = benchmarks.rendered()

    def package(self, rid, name):
        return json.loads(self.files[f'{rid}/{name}'])

    def test_three_complete_packages_and_manifest_hashes(self):
        self.assertEqual(len(self.files), 31)
        required = {'asset.json', '深化内容.md', 'SKILL.md', 'invocation.json', 'evaluations.json', 'reference-artifact.json', 'reference-run.json', 'quality-report.json'}
        manifest = json.loads(self.files['目录.json'])
        self.assertEqual({m['research_id'] for m in manifest['methods']}, {'R17', 'R02', 'R52'})
        for row in manifest['methods']:
            rid = row['research_id']
            self.assertTrue(required <= set(row['files']))
            for name, expected in row['files'].items():
                self.assertEqual(benchmarks.sha(self.files[f'{rid}/{name}'].encode('utf-8')), expected)
        for name, text in self.files.items():
            if name.endswith('.json'):
                json.loads(text)

    def test_r17_real_reference_replay_and_contract_candidate(self):
        artifact = self.package('R17', 'reference-artifact.json')
        run = self.package('R17', 'reference-run.json')
        self.assertEqual(run['counts'], {'functions': 7, 'options': 28, 'combinations': 4, 'compatibility_rows': 2, 'evidence': 28})
        self.assertEqual(run['check']['status'], 'structure_and_declared_consistency_passed')
        self.assertEqual(run['combination_statuses'], ['unknown'])
        self.assertEqual(run['compatibility_statuses'], ['unknown'])
        self.assertEqual(len(artifact['payload']['function_ids']), 7)
        evaluations = self.package('R17', 'evaluations.json')['evaluations']
        self.assertTrue(all(e.get('passed', e.get('passed_candidate', False)) for e in evaluations))
        unknown = next(e for e in evaluations if e['id'] == 'R17-UNKNOWN-CANDIDATE')
        self.assertFalse(unknown['passed_before'])
        self.assertEqual(unknown['actual_candidate'][0]['code'], 'candidate_contains_unknown_compatibility')
        incompatible = next(e for e in evaluations if e['id'] == 'R17-INCOMPATIBLE-CANDIDATE')
        self.assertTrue(incompatible['passed'])
        candidate = self.package('R17', 'contract-candidate.json')
        original = self.package('R17', 'contract.json')
        self.assertEqual(original['contract_version'], '0.2.0')
        self.assertEqual(candidate['contract_version'], '0.3.0-candidate.1')
        self.assertEqual(candidate['source_contract_sha256'], benchmarks.sha((benchmarks.ROOT / '04-知识库/创新方法库/执行契约-v0.2.0/R17/contract.json').read_bytes()))
        proposal = self.package('R17', 'change-proposal.json')
        self.assertEqual(proposal['status'], 'evaluated_candidate_requires_independent_review')

    def test_r02_framework_replay_is_guided_not_strict_execution(self):
        run = self.package('R02', 'reference-run.json')
        self.assertTrue(all(run['checks'].values()))
        self.assertEqual(run['mode'], 'deterministic_guided_teaching_replay')
        artifact = self.package('R02', 'reference-artifact.json')
        self.assertEqual(artifact['payload']['learning_status'], 'planned_not_executed')
        self.assertIn('返回Define', artifact['payload']['return_conditions'][0])
        invocation = self.package('R02', 'invocation.json')
        self.assertEqual(invocation['skill_level'], 'S1')
        self.assertIn('method_run_submit', invocation['forbidden_operations'])
        self.assertIsNone(invocation['contract_ref'])

    def test_r52_numeric_replay_and_qualitative_boundary(self):
        artifact = self.package('R52', 'reference-artifact.json')
        base = artifact['payload']['base_case']
        zero = artifact['payload']['zero_value_case']
        self.assertEqual((base['EVPI'], base['EVSI'], base['net_value']), (20, 6, 3))
        self.assertEqual(zero['EVSI'], 0)
        run = self.package('R52', 'reference-run.json')
        self.assertTrue(all(run['checks'].values()))
        self.assertEqual(run['mode'], 'deterministic_numeric_teaching_replay')
        invocation = self.package('R52', 'invocation.json')
        self.assertEqual(invocation['skill_level'], 'S1')
        self.assertIn('method_run_submit', invocation['forbidden_operations'])

    def test_skill_frontmatter_and_quality_boundaries(self):
        for rid in benchmarks.METHOD_IDS:
            skill = self.files[f'{rid}/SKILL.md']
            frontmatter = skill.split('---')[1].strip().splitlines()
            self.assertTrue(all(line.startswith(('name:', 'description:')) for line in frontmatter))
            quality = self.package(rid, 'quality-report.json')
            self.assertFalse(quality['engine_contribution']['isolated_effect_established'])
            self.assertFalse(quality['real_context']['engineering_validated'])
            self.assertEqual(quality['release_status'], 'benchmark_candidate_not_production')
            self.assertTrue(quality['execution']['evaluation_passed'])

    def test_historical_context_is_not_r17_attribution(self):
        quality = self.package('R17', 'quality-report.json')
        context = quality['engine_contribution']['historical_method_package_context']
        self.assertEqual(context['reports'], 24)
        self.assertEqual(context['ai_reviews'], 48)
        self.assertAlmostEqual(context['C_minus_A']['validation'], 0.666)
        self.assertEqual(context['C_minus_A']['mechanism'], 0)
        self.assertIn('不可单独归因R17', context['attribution'])

    def test_r17_quality_comparison_separates_contract_gain_from_unrun_model_experiment(self):
        report = self.package('R17', 'engine-quality-report.json')
        comparison = report['candidate_contract_comparison']
        self.assertTrue(comparison['before_over_permissive'])
        self.assertTrue(comparison['constraint_improvement_demonstrated'])
        self.assertEqual(comparison['candidate_status'], 'blocked')
        self.assertFalse(report['conclusion']['r17_research_uplift_established'])
        protocol = self.package('R17', 'isolated-evaluation-protocol.json')
        self.assertTrue(protocol['protocol_frozen_before_generation'])
        self.assertEqual(protocol['generation_calls_planned'], 4)
        self.assertEqual(protocol['independent_blind_review_calls_planned'], 2)
        self.assertEqual(protocol['generation_calls_actual'], 0)
        self.assertEqual(protocol['status'], 'blocked_backend_unavailable')

    def test_outputs_are_deterministic_and_current(self):
        self.assertEqual(self.files, benchmarks.rendered())
        for name, text in self.files.items():
            self.assertEqual((benchmarks.OUTPUT / name).read_text(encoding='utf-8'), text)


if __name__ == '__main__':
    unittest.main()
