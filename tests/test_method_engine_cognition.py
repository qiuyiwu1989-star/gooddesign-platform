"""Evidence-contamination regressions plus real stdio MCP integration."""
import asyncio
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from method_engine_cognition import read_deep_method, prepare_context, feedback_summary


def task():
    return dict(task_id='ML022-TEST', revision='v1', object='rubber_tapping_robot',
                desired_outcome='develop a research plan', boundary='constructed teaching only', stage='frame')


def claim(ident='A', scope='donor_case'):
    return dict(id=ident, text='A source describes a mechanism; not target performance.',
                scope=scope, epistemic='observed',
                evidence=[dict(source_id='constructed-source', locator='constructed paragraph 1', scope=scope)])


class CognitionTests(unittest.TestCase):
    def test_all_64_latest_manuscripts_not_only_frozen_60(self):
        ids = [f'R{i:02}' for i in range(1, 53)] + [f'WB{i:02}' for i in range(1, 13)]
        methods = [read_deep_method(i) for i in ids]
        self.assertEqual(len(methods), 64)
        self.assertTrue(read_deep_method('WB05')['partial_dimensions'])
        self.assertFalse(read_deep_method('R52')['execution_available'])
        self.assertTrue(read_deep_method('R48')['execution_available'])

    def test_source_observation_never_becomes_target_fact(self):
        source = claim()
        result = prepare_context(task(), [source], ['R48', 'R49'])
        packet = result['context']
        self.assertEqual(packet['claims'][0]['scope'], 'donor_case')
        self.assertFalse(packet['capability_boundary']['semantic_truth_verified'])
        self.assertEqual(len(packet['existing_contract_plan']['nodes']), 6)
        source['text'] = 'caller changed later'
        self.assertNotEqual(packet['claims'][0]['text'], source['text'])

    def test_full_contract_schemas_are_not_repeated_in_model_context(self):
        from method_engine import Engine, digest
        result = prepare_context(task(), [claim()], ['R48', 'R49', 'R23', 'R52', 'R42'])
        plan = result['context']['existing_contract_plan']
        self.assertEqual(plan['full_plan_sha256'], Engine().plan(task())['plan_sha256'])
        self.assertFalse(plan['full_plan_returned'])
        self.assertNotIn('contract_snapshot', plan['nodes'][0])
        self.assertTrue(result['fits_existing_semantic_match_limit'])
        self.assertLess(result['model_context_chars'], 20000)
        projection = dict(plan); recorded = projection.pop('projection_sha256')
        self.assertEqual(digest(projection), recorded)

    def test_large_context_reports_overflow_without_truncating_claims(self):
        c = claim(); c['text'] = 'x' * 21000
        result = prepare_context(task(), [c], ['R48'])
        self.assertFalse(result['fits_existing_semantic_match_limit'])
        self.assertEqual(result['context']['claims'][0]['text'], c['text'])

    def test_observation_requires_anchor_and_matching_scope(self):
        c = claim(); c['evidence'] = []
        with self.assertRaisesRegex(ValueError, 'requires_anchor'):
            prepare_context(task(), [c], ['R48'])
        c = claim(); c['evidence'][0]['scope'] = 'target'
        with self.assertRaisesRegex(ValueError, 'scope_mismatch'):
            prepare_context(task(), [c], ['R48'])

    def test_two_sided_structural_transfer_stays_associated(self):
        a, b = claim(), claim('B', 'target_research')
        p = dict(claim_ids=['A', 'B'], transfer_kind='structural_principle',
                 principle='Separate contacting functions', conditions_to_check='material, geometry, loads')
        result = prepare_context(task(), [a, b], ['R49'], associations=[p])
        link = result['context']['association_candidates'][0]
        self.assertEqual(link['epistemic'], 'associated')
        self.assertFalse(link['source_facts_transferred'])
        b['evidence'] = []; b['epistemic'] = 'hypothesized'
        with self.assertRaisesRegex(ValueError, 'two_anchored_sides'):
            prepare_context(task(), [a, b], ['R49'], associations=[p])
        b = claim('B', 'target_research'); p['transfer_kind'] = 'parameter_copy'
        with self.assertRaisesRegex(ValueError, 'fact_transfer_forbidden'):
            prepare_context(task(), [a, b], ['R49'], associations=[p])

    def test_conflict_creates_research_not_new_wins_old(self):
        a, b = claim(), claim('B')
        b['supersedes'] = 'A'
        out = prepare_context(task(), [a, b], ['R48'], conflicts=[
            dict(claim_ids=['A', 'B'], question='Do conditions differ?')])['context']
        self.assertEqual(len(out['claims']), 2)
        self.assertFalse(out['boundary_research'][0]['auto_resolved'])
        self.assertEqual(out['supersession_proposals'][0]['status'], 'proposed_requires_reason_and_review')
        a['supersedes'] = 'B'
        with self.assertRaisesRegex(ValueError, 'cycle'):
            prepare_context(task(), [a, b], ['R48'])

    def test_incomplete_task_cannot_get_executable_plan(self):
        t = task(); del t['boundary']
        self.assertEqual(prepare_context(t, [], ['R48'])['status'], 'blocked')

    def test_unknown_methods_and_duplicate_claims_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unknown_method'):
            prepare_context(task(), [], ['R99'])
        with self.assertRaisesRegex(ValueError, 'duplicate_claim'):
            prepare_context(task(), [claim(), claim()], ['R48'])

    def test_feedback_does_not_invent_accuracy_or_treat_pending_as_failure(self):
        self.assertEqual(feedback_summary([])['groups'], {})
        data = [dict(prediction_id='P1', judgment_type='technical', outcome='pending')]
        self.assertEqual(feedback_summary(data)['groups']['technical']['refuted'], 0)
        data[0]['outcome'] = 'supported'
        with self.assertRaisesRegex(ValueError, 'outcome_anchor'):
            feedback_summary(data)

    def test_real_stdio_tools_and_partial_depth(self):
        async def run():
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            params = StdioServerParameters(command=sys.executable,
                         args=[str(ROOT / 'scripts/method_engine_cognitive_mcp.py')])
            async with stdio_client(params) as (r, w):
                async with ClientSession(r, w) as session:
                    await session.initialize()
                    names = {t.name for t in (await session.list_tools()).tools}
                    self.assertEqual(len(names), 25)
                    response = await session.call_tool('method_deep_content', {'method_id': 'WB05'})
                    self.assertFalse(response.isError)
                    data = response.structuredContent or json.loads(response.content[0].text)
                    self.assertTrue(data['partial_dimensions'])
                    response = await session.call_tool('innovation_reasoning_context',
                        dict(task=task(), claims=[claim()], method_ids=['R48', 'R52']))
                    self.assertFalse(response.isError)
                    data = response.structuredContent or json.loads(response.content[0].text)
                    self.assertEqual(data['status'], 'host_reasoning_context_ready')
                    self.assertFalse(data['context']['capability_boundary']['model_called'])
        asyncio.run(run())


if __name__ == '__main__':
    unittest.main()
