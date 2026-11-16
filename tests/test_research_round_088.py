import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
OUT = ROOT / 'output/research-088'


class ResearchRound088Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads((OUT / 'audit-summary.json').read_text())
        cls.queues = json.loads((OUT / 'queues.json').read_text())
        cls.index = json.loads((ROOT / '04-知识库/项目库/项目索引.json').read_text())['projects']
        cls.task = (ROOT / '04-知识库/项目档案标准-v1/外部Agent协作-v1/088-豆包全量深研任务书.md').read_text()

    def test_088_index_and_material_directories_are_complete(self):
        self.assertEqual(self.audit['index_projects'], 560)
        self.assertEqual(self.audit['unique_project_ids'], 560)
        self.assertEqual(self.audit['missing_project_directories'], [])
        self.assertEqual(self.audit['missing_material_directories'], [])

    def test_088_queue_covers_every_project_once(self):
        self.assertEqual(sum(self.queues['counts'].values()), 560)
        actual = [row['id'] for rows in self.queues['queues'].values() for row in rows]
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual(set(actual), {row['id'] for row in self.index})
        self.assertEqual(self.queues['counts'], {'A_no_standard_no_native': 60, 'B_standard_no_native': 397, 'C_standard_with_native': 70, 'D_no_standard_with_native': 33})

    def test_088_mechanical_validation_and_repaired_exception_are_exact(self):
        self.assertEqual(self.audit['standard_batch_coverage'], {'20261103-doubao-full-01': 467, '20261103-doubao-patents-01': 467})
        allowed = {'mechanical_pass_pending_content_review', 'needs_correction'}
        for batch in ('20261103-doubao-full-01', '20261103-doubao-patents-01'):
            statuses = self.audit['standard_batch_validation'][batch]
            self.assertLessEqual(set(statuses), allowed)
            self.assertEqual(sum(statuses.values()), 467)
        self.assertNotIn('2021-c30', {item['project_id'] for item in self.audit['exceptions']})

    def test_088_c30_is_repaired_without_fabricating_sources(self):
        import agent_intake
        batch = ROOT / '04-知识库/项目库/2021-c30/04-深研素材/外部投递/20261103-doubao-patents-01'
        claims = agent_intake.rows(batch / 'claims.jsonl')
        self.assertEqual([claim['kind'] for claim in claims], ['lead', 'lead', 'lead'])
        self.assertTrue(all('当前未登记可核验来源' in claim['limitations'] for claim in claims[1:]))
        queries = agent_intake.rows(batch / 'queries.jsonl')
        self.assertEqual(queries[1]['source_ids'], [])
        result = agent_intake.validate(batch)
        self.assertEqual(result['status'], 'mechanical_pass_pending_content_review')
        self.assertFalse(result['official_ingestion'])

    def test_088_native_quality_is_not_overclaimed(self):
        native = self.audit['native_research']
        self.assertEqual(native['projects'], 103)
        self.assertEqual(native['audit_traceable'], 102)
        self.assertEqual(native['audit_attention'], 1)
        self.assertEqual(native['issues'], 791)
        self.assertIn('legacy_baseline_missing_frozen_evidence_objects', self.audit['baseline_evidence_exception']['kind'])
        self.assertFalse(self.audit['official_ingestion'])
        self.assertFalse(self.audit['semantic_review_completed'])
        self.assertFalse(self.audit['quality_score_assigned'])

    def test_088_doubao_task_has_actionable_contract_and_redlines(self):
        for text in ('2021-c30', '2025-00', '60', '397', '70', '33', 'agent-intake-1.0', 'mechanical_pass_pending_content_review', 'CNIPA', 'unknown', 'queries.jsonl', 'sources.jsonl', 'claims.jsonl'):
            self.assertIn(text, self.task)
        self.assertIn('不得把“560/560有目录”写成“560/560真深研完成”', self.task)
        self.assertIn('scripts/agent_intake.py validate', self.task)
        self.assertIn('不得为通过校验虚构URL', self.task)


if __name__ == '__main__':
    unittest.main()
