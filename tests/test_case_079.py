# coding: utf-8
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import project_pipeline as pp
import project_ownership as own
import research_assessment as ra
import research_reader_notes as rn
import research_workflow as rw
import workspace_ui

PID = '2019-s19'
ARCHIVE = 'Se3e240239a2f0916'
PAPER = 'S7e3f4f2b06f63fe8'
MEDIA = 'S8ae50c84687b0709'
PENDING = {'S10217b5974360368', 'S0f787f1cee784ee1', 'S9b56a6acdcb27eb6'}
ALLOWED = {ARCHIVE, PAPER, 'S958291324dfd4332', MEDIA, 'S5ca519ed10721899', 'S349e0fec3fb0debf'}


class Case079Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = pp.project(pp.LIB, PID)
        cls.w = rw.current(cls.p)
        cls.revision = 'research-%06d' % cls.w['revision']
        cls.folder, cls.manifest = rw.check_version(cls.p, cls.revision)
        cls.data = rw.dataset(cls.p, cls.w)
        cls.records = {r['id']: r for r in cls.data['records']}
        cls.state = pp.state(cls.p)

    def cell(self, rid, field):
        value = rw.cell(self.data, rid, field)
        self.assertIsNotNone(value, f'{rid}.{field} 未入档')
        self.assertEqual(value['value_state'], 'known')
        return value

    def test_079_version_counts_and_review_boundary(self):
        self.assertEqual(self.revision, 'research-000001')
        self.assertEqual(len(self.records), 45)
        self.assertEqual(sum(c.get('value_state') == 'known' for r in self.data['records'] for c in r['cells'].values()), 180)
        self.assertEqual(len(self.data['interpretations']), 42)
        self.assertFalse(self.data['expert_reviewed'])
        self.assertEqual(self.data['quality_score_status'], 'unchanged_from_authored_baseline')

    def test_079_engineering_metrics_keep_original_units(self):
        expected = {
            'MET-001': (4500, 'kW'),
            'MET-002': (105, 'MPa'),
            'MET-003': (70, 'MPa'),
            'MET-007': (2.32, 'm3·min-1'),
            'MET-008': (3.22, 'm3·min-1'),
            'MET-009': (132.2, 'h'),
            'MET-010': (107.2, 'h'),
        }
        for rid, (number, unit) in expected.items():
            with self.subTest(rid=rid):
                self.assertEqual(self.cell(rid, 'value')['value'], number)
                self.assertEqual(self.cell(rid, 'unit')['value'], unit)
                self.assertTrue(self.cell(rid, 'value')['conditions'])
        self.assertEqual(self.cell('MET-015', 'original_statement')['value'], '6.3×3.0×3.0')
        self.assertEqual(self.cell('MET-016', 'original_statement')['value'], '3.0~4.5 m3/min，约占总施工液量的1/4')
        self.assertEqual(self.cell('MET-017', 'original_statement')['value'], '70~85 MPa')

    def test_079_equivalence_claims_are_not_merged(self):
        single = self.cell('MET-018', 'original_statement')
        six = self.cell('MET-019', 'original_statement')
        eight = self.cell('MET-020', 'original_statement')
        self.assertEqual(single['value'], '相当于3辆2000型常规压裂车的总和')
        self.assertEqual(six['value'], '实现18台2000型压裂车才能进行的大型工厂化压裂作业')
        self.assertEqual(eight['value'], '至少等同于20台以上传统柴油机压裂设备的性能')
        self.assertEqual(single['evidence']['source_id'], PAPER)
        self.assertEqual(six['evidence']['source_id'], PAPER)
        self.assertEqual(eight['evidence']['source_id'], MEDIA)
        self.assertIn('36000HP', six['evidence']['quote'])
        self.assertNotEqual(eight['evidence']['quote'], six['evidence']['quote'])

    def test_079_cost_claims_keep_source_and_conditions(self):
        self.assertEqual(self.cell('MET-011', 'value')['value'], 40)
        self.assertEqual(self.cell('MET-011', 'qualifier')['value'], '以上')
        self.assertEqual(self.cell('MET-011', 'conditions')['value'], '按照当前油价和电价的差别')
        self.assertEqual(self.cell('MET-012', 'value')['value'], 46)
        self.assertEqual(self.cell('MET-012', 'value')['evidence']['source_id'], ARCHIVE)
        self.assertEqual(self.cell('MET-013', 'value')['value'], 40)
        self.assertEqual(self.cell('MET-022', 'original_statement')['value'], '30%～40%')
        boundary = next(i for i in self.data['interpretations'] if i['record_id'] == 'ANA-002' and i['field'] == 'original_statement')
        self.assertIn('不能相互替代或合并成统一比例', boundary['value'])
        self.assertEqual(boundary['content_nature'], 'ai_interpretation')
        self.assertEqual(self.records['APP-003']['cells']['benefit_value']['value_state'], 'not_researched')

    def test_079_patent_total_is_only_a_disclosure(self):
        self.assertEqual(self.cell('PAT-ACH-001', 'count')['value'], 9)
        self.assertFalse([r for r in self.data['records'] if r['entity'] == 'patent'])
        states = {i['field']: i for i in self.data['interpretations'] if i['record_id'] == 'PAT-ACH-001'}
        self.assertIs(states['item_list_obtained']['value'], False)
        self.assertEqual(states['review_status']['value'], '待逐项核验')
        for item in states.values():
            self.assertEqual(item['content_nature'], 'ai_interpretation')
            self.assertTrue(item['conditions'])
            self.assertTrue(item['limitations'])

    def test_079_pending_and_other_company_material_does_not_enter_facts(self):
        used = {e['source_id'] for r in self.data['records'] for c in r['cells'].values() if c.get('value_state') == 'known' for e in [c['evidence']]}
        used |= {i['source_id'] for i in self.data['interpretations']}
        self.assertLessEqual(used, ALLOWED)
        self.assertFalse(used & PENDING)
        registry = own.registry(self.p)
        for sid in PENDING:
            self.assertEqual(own.assignment(self.p, sid, self.state['sources'], registry)['scope'], 'pending')

        def values(value):
            if isinstance(value, dict):
                for child in value.values():
                    yield from values(child)
            elif isinstance(value, list):
                for child in value:
                    yield from values(child)
            else:
                yield str(value)

        for record in self.data['records']:
            for cell in record['cells'].values():
                if cell.get('value_state') == 'known':
                    self.assertFalse(any(term in ''.join(values(cell['value'])) for term in ('烟台杰瑞', '阿波罗', '工信部')), record['id'])

    def test_079_derived_sources_keep_acquisition_limits(self):
        expectations = {
            MEDIA: ('普通抓取页面未得到正文', '不冒充原网页原件'),
            'S5ca519ed10721899': ('直接抓取接口返回404', '不冒充原网页原件'),
            'S349e0fec3fb0debf': ('直接下载未成功', '不作为PDF原件'),
        }
        for sid, boundaries in expectations.items():
            source = self.state['sources'][sid]
            text = pp.safe(self.p, source['original']).read_text(encoding='utf-8')
            for boundary in boundaries:
                self.assertIn(boundary, text)
        reading = next(i for i in self.data['interpretations'] if i['record_id'] == 'PAPER-001' and i['field'] == 'reading_scope')
        self.assertEqual(reading['value'], '全文')
        self.assertIn('Download PDF入口未单独下载核验', reading['limitations'])

    def test_079_all_facts_and_ai_are_traceable(self):
        audit = ra.audit(self.p, self.data)
        self.assertEqual(audit['status'], 'traceable')
        self.assertEqual(audit['traceable_known_cells'], 180)
        self.assertEqual(audit['traceable_bounded_ai_items'], 42)
        self.assertEqual(audit['issues'], [])
        for item in self.data['interpretations']:
            self.assertIn(item['content_nature'], ('ai_interpretation', 'ai_hypothesis'))
            self.assertTrue(item['conditions'])
            self.assertTrue(item['limitations'])

    def test_079_guide_and_assessment_bind_current_dataset(self):
        digest = pp.sha((self.folder / '档案.json').read_bytes())
        guide = rn.read(self.p, self.revision, '0.1.0')
        review = ra.read(self.p, self.revision, '0.1.0')
        self.assertEqual(guide['status'], 'available')
        self.assertEqual(review['status'], 'available')
        self.assertEqual(guide['notes']['dataset_sha256'], digest)
        self.assertEqual(review['report']['judgment']['dataset_sha256'], digest)
        self.assertEqual(len(guide['notes']['modules']), 8)
        self.assertIsNone(review['report']['quality_score'])
        self.assertFalse(review['report']['expert_reviewed'])
        stale_guide = copy.deepcopy(guide['notes'])
        stale_guide['dataset_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            rn.validate(self.p, stale_guide)
        stale_review = copy.deepcopy(review['report']['judgment'])
        stale_review['dataset_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            ra.validate(self.p, stale_review)

    def test_079_frozen_version_detects_tampering_without_touching_original(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp) / PID
            target = project / '研究工作区' / '版本' / self.revision
            shutil.copytree(self.folder, target)
            before = (target / 'manifest.json').read_bytes()
            rw.check_version(project, self.revision)
            with (target / '档案.json').open('a', encoding='utf-8') as stream:
                stream.write(' ')
            with self.assertRaises(ValueError):
                rw.check_version(project, self.revision)
            self.assertEqual((target / 'manifest.json').read_bytes(), before)

    def test_079_reader_uses_shared_chrome_and_shows_research_status(self):
        html = workspace_ui.dossier(PID, pp.LIB)
        self.assertIn('research-000001', html)
        self.assertIn('45', html)
        self.assertIn('42', html)
        self.assertIn('待专业审核', html)
        self.assertIn('未评', html)
        self.assertIn('reader-shell', html)
        self.assertIn('资料与解读', html)
        self.assertIn('class="gd-shell gd-footer"', html)
        self.assertEqual(html.count('data-gd-chrome="footer"'), 1)
        self.assertNotRegex(html, r'>[^<]*[→↗↑←↘↙][^<]*</a>')
        self.assertIn('.research-box{background:var(--ui-surface);', html)
        self.assertEqual(html.count('class="research-guide"'), 8)
        self.assertIn('id="record-MET-020"', html)
        self.assertIn('id="record-VAL-002"', html)


if __name__ == '__main__':
    unittest.main()
