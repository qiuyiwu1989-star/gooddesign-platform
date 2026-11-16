import json
import unittest

import archive_knowledge_graph as kg
import project_pipeline as pp
import research_workflow as rw
import steward_dossier_ui


class ProjectKnowledgeGraph100Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data2025 = kg.graph_data(pp.LIB, '2025-00')
        cls.data2021 = kg.graph_data(pp.LIB, '2021-00')
        cls.html2025 = steward_dossier_ui.render(pp.LIB, '2025-00', '', '', graph_href='graphs/2025-00.html')

    def test_100_graph_summary_and_versions_match_current_truth(self):
        self.assertEqual(self.data2025['summary'], {
            'records': 105, 'sources': 176, 'facts': 476, 'traceable': 109,
            'gaps': 367, 'platform_metadata': 249, 'platform_analysis': 77,
        })
        self.assertEqual(self.data2025['project']['research_revision'], 'research-000008')
        folder, _ = rw.check_version(pp.project(pp.LIB, '2025-00'), 'research-000008')
        self.assertEqual(self.data2025['project']['dataset_sha256'], pp.sha((folder / '档案.json').read_bytes()))
        self.assertEqual(self.data2021['summary']['records'], 24)
        self.assertEqual(self.data2021['summary']['traceable'], 51)
        self.assertEqual(self.data2021['summary']['gaps'], 0)

    def test_100_graph_nodes_and_edges_are_complete_and_resolvable(self):
        self.assertEqual(len(self.data2025['nodes']), 1 + 8 + 105 + 176)
        self.assertEqual(len(self.data2021['nodes']), 1 + 8 + 24 + 8)
        ids = {node['id'] for node in self.data2025['nodes']}
        self.assertIn('record-H01', ids)
        self.assertIn('record-MET-01', ids)
        self.assertTrue(all(edge['source'] in ids and edge['target'] in ids for edge in self.data2025['edges']))
        self.assertTrue(any(edge['relation'] == 'evidence' for edge in self.data2025['edges']))
        modules = {node['id'] for node in self.data2025['nodes'] if node['type'] == 'module'}
        self.assertEqual(len(modules), 8)

    def test_100_record_details_use_chinese_labels(self):
        _, fields, _ = kg.detail_record(self.data2025, 'PRJ-2025-00')
        labels = {field['field'] for field in fields}
        self.assertIn('规范名称', labels)
        self.assertNotIn('canonical_name', labels)
        record, fields, _ = kg.detail_record(self.data2025, 'H01')
        self.assertEqual(record['title'], '任务之前的长期准备')
        self.assertTrue(any('持续设计与试验积累' in field['value'] for field in fields))

    def test_100_graph_html_is_interactive_and_self_contained(self):
        html = kg.render_html(self.data2025)
        self.assertIn('id="graph-search"', html)
        self.assertIn('data-node-id="record-H01"', html)
        self.assertIn('id="module-filter"', html)
        self.assertIn('id="status-filter"', html)
        self.assertIn('id="record-detail"', html)
        self.assertIn('gooddesign-project-graph-1.0', html)
        self.assertNotIn('https://', html.split('<script id="graph-data"', 1)[0])

    def test_100_assessment_visualization_uses_same_metrics_and_graph_link(self):
        for marker in ('assessment-donut', 'assessment-composition-row', 'assessment-module-card', '22.9%', '109 / 476', 'graphs/2025-00.html'):
            self.assertIn(marker, self.html2025)
        self.assertEqual(self.html2025.count('assessment-module-card'), 12)
        self.assertIn('证据重绑：109 / 476 项', self.html2025)
        self.assertIn('尚未形成有效评估', self.html2025)


if __name__ == '__main__':
    unittest.main()
