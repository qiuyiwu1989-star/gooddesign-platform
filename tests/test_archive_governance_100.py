import copy
import unittest

import jsonschema

import archive_governance as ag
import project_pipeline as pp
import research_workflow as rw


class ArchiveGovernance100Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p2021 = pp.project(pp.LIB, '2021-00')
        cls.p2025 = pp.project(pp.LIB, '2025-00')
        cls.doc2021 = ag.build_mva(cls.p2021)
        ag.validate_mva(cls.p2021, cls.doc2021)

    def test_100_schemas_are_valid_and_review_cannot_self_upgrade(self):
        for schema in ag.SCHEMAS.values():
            jsonschema.validators.validator_for(schema).check_schema(schema)
        review = self.doc2021['review']
        self.assertFalse(review['human_read'])
        self.assertFalse(review['expert_reviewed'])
        self.assertFalse(review['engineering_validated'])
        self.assertFalse(review['official_ingestion'])
        self.assertIsNone(review['quality_score'])
        self.assertTrue(all(not source['original_verified'] for source in self.doc2021['sources']))

    def test_100_2021_00_builds_traceable_claims_from_current_truth(self):
        self.assertTrue(self.doc2021['status']['mva_ready'], self.doc2021['status']['blockers'][:5])
        self.assertEqual(self.doc2021['research_revision'], 'research-000002')
        self.assertEqual(self.doc2021['metrics']['records'], 24)
        self.assertEqual(self.doc2021['metrics']['known_cells'], 51)
        self.assertEqual(self.doc2021['metrics']['source_statement_claims'], 51)
        self.assertEqual(self.doc2021['metrics']['traceable_claims'], 51)
        self.assertEqual(self.doc2021['metrics']['project_sources'], 8)
        self.assertEqual(self.doc2021['metrics']['unique_frozen_evidence'], 40)
        self.assertEqual(self.doc2021['review']['agent_assessment']['status'], 'available_current')

    def test_100_2025_00_separates_platform_entries_and_blocks_incomplete_evidence(self):
        result = ag.audit(self.p2025)
        self.assertFalse(result['mva_ready'])
        self.assertEqual(result['metrics']['known_cells'], 802)
        self.assertEqual(result['metrics']['source_statement_claims'], 476)
        self.assertEqual(result['metrics']['platform_metadata_cells'], 249)
        self.assertEqual(result['metrics']['platform_analysis_cells'], 77)
        self.assertEqual(result['metrics']['traceable_claims'], 109)
        self.assertEqual(len(result['blockers']), 367)
        self.assertIn('冻结证据缺字段', result['blockers'][0])

    def test_100_2025_00_A01_rebind_preserves_values_and_old_version(self):
        current = rw.dataset(self.p2025, revision='research-000005')
        previous = rw.dataset(self.p2025, revision='research-000004')
        rebound_fields = ('authors', 'year', 'online_date', 'venue', 'volume', 'issue', 'doi')
        for field in rebound_fields:
            before = rw.cell(previous, 'A01', field)
            after = rw.cell(current, 'A01', field)
            self.assertEqual(after['value'], before['value'], field)
            self.assertEqual(after['evidence']['source_id'], 'Sd9990d8319008dcb', field)
            self.assertEqual(after['evidence']['chunk_id'], 'B0014', field)
            self.assertEqual(after['verification_state'], 'automated_evidence_checked_not_expert', field)
        self.assertNotIn('evidence', rw.cell(current, 'A01', 'pages'))
        self.assertFalse(current['expert_reviewed'])
        self.assertEqual(current['quality_score_status'], 'unchanged_from_authored_baseline')

    def test_100_2025_00_batch02_rebinds_only_directly_supported_fields(self):
        previous = rw.dataset(self.p2025, revision='research-000005')
        current = rw.dataset(self.p2025, revision='research-000006')
        expected = {
            'MET-06': ('name', 'S62270319aa992c70', 'B0006'),
            'MET-07': ('name', 'S62270319aa992c70', 'B0006'),
            'MET-08': ('name', 'S62270319aa992c70', 'B0006'),
            'MET-10': ('name', 'S62270319aa992c70', 'B0009'),
            'MET-11': ('name', 'S62270319aa992c70', 'B0019'),
            'MET-12': ('name', 'S62270319aa992c70', 'B0019'),
            'A02': ('title', 'Sc36311fd1ae3b041', 'B0001'),
            'A03': ('authors', 'S69cca68f7b87a8d4', 'B0001'),
            'A04': ('authors', 'S62270319aa992c70', 'B0001'),
            'A04': ('affiliations', 'S62270319aa992c70', 'B0001'),
        }
        for rid, (field, sid, chunk) in expected.items():
            before = rw.cell(previous, rid, field)
            after = rw.cell(current, rid, field)
            self.assertEqual(after['value'], before['value'], f'{rid}/{field}')
            self.assertEqual(after['evidence']['source_id'], sid, f'{rid}/{field}')
            self.assertEqual(after['evidence']['chunk_id'], chunk, f'{rid}/{field}')
        for rid, field in (('A02', 'doi'), ('A03', 'doi'), ('A04', 'doi')):
            self.assertIn('source_id', rw.cell(current, rid, field)['evidence'])
        for rid in ('MET-05', 'MET-10', 'MET-11', 'MET-12', 'MET-14', 'MET-15', 'MET-18', 'MET-19', 'MET-20'):
            self.assertNotIn('evidence', rw.cell(current, rid, 'value'), rid)

    def test_100_2025_00_official_and_patent_batches_preserve_values_and_boundaries(self):
        previous = rw.dataset(self.p2025, revision='research-000005')
        current = rw.dataset(self.p2025, revision='research-000008')
        for revision, expected_count in (('research-000006', 13), ('research-000007', 32), ('research-000008', 46)):
            changes = pp.load(rw.workspace(self.p2025) / '版本' / revision / 'changes.json')['changes']
            self.assertEqual(len(changes), expected_count, revision)
            for change in changes:
                rid, field = change['record_id'], change['field']
                self.assertEqual(rw.cell(current, rid, field)['value'], rw.cell(previous, rid, field)['value'], f'{rid}/{field}')
                self.assertIn('source_id', rw.cell(current, rid, field)['evidence'], f'{rid}/{field}')
        for rid, field in (('AWD-2025-10', 'award_name'), ('AWD-2025-10', 'organizer'), ('ORG-01', 'name_original'), ('ORG-02', 'name_original')):
            self.assertNotIn('evidence', rw.cell(current, rid, field), f'{rid}/{field}')
        self.assertEqual(rw.cell(current, 'E01', 'date')['evidence']['source_id'], 'Se42947611adb5e1c')
        self.assertEqual(rw.cell(current, 'E03', 'date')['evidence']['source_id'], 'S42fd1522a74507b2')
        patent_changes = pp.load(rw.workspace(self.p2025) / '版本/research-000008/changes.json')['changes']
        for change in patent_changes:
            cell = rw.cell(current, change['record_id'], change['field'])
            self.assertIn('不代表现时法律状态、权属或项目实际采用', cell['conditions'])

    def test_100_missing_quote_and_stale_dataset_are_blocked(self):
        missing_quote = copy.deepcopy(self.doc2021)
        del missing_quote['claims'][0]['evidence'][0]['quote']
        missing_quote['status'] = {'blockers': [], 'warnings': [], 'mva_ready': False}
        status = ag.validate_mva(self.p2021, missing_quote)
        self.assertFalse(status['mva_ready'])
        self.assertTrue(any('quote' in item for item in status['blockers']))

        stale = copy.deepcopy(self.doc2021)
        stale['dataset_sha256'] = '0' * 64
        stale['status'] = {'blockers': [], 'warnings': [], 'mva_ready': False}
        status = ag.validate_mva(self.p2021, stale)
        self.assertFalse(status['mva_ready'])
        self.assertIn('mva: 投影已偏离当前研究版本', status['blockers'])

    def test_100_failed_audit_cannot_be_written_as_mva(self):
        with self.assertRaisesRegex(ValueError, 'MVA 门禁未通过'):
            ag.write_mva(self.p2025)


if __name__ == '__main__':
    unittest.main()
