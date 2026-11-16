import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import project_pipeline as pp
import research_workflow as rw
import workspace_ui


class DossierReading094Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.benchmark = (ROOT / '04-知识库/标杆案例/2025-00-嫦娥钻取采样/档案.html').read_text()
        cls.dynamic = workspace_ui.dossier('2019-s19', pp.LIB)

    def test_094_benchmark_core_modules_are_open(self):
        for key in ('overview', 'technical', 'innovation', 'validation'):
            self.assertRegex(self.benchmark, rf'<details class="reader-section reader-module" id="reader-{key}" tabindex="-1" open>')
        for key in ('ip', 'history', 'applications', 'governance'):
            self.assertRegex(self.benchmark, rf'<details class="reader-section reader-module" id="reader-{key}" tabindex="-1">')
        self.assertIn('核心 4 个板块已展开', self.benchmark)
        for marker in ('{icon(', '{e(', '{i:', '{status['):
            self.assertNotIn(marker, self.benchmark)

    def test_094_dynamic_records_are_visible_with_bounded_details(self):
        for key in ('overview', 'technical', 'innovation', 'validation'):
            self.assertRegex(self.dynamic, rf'<details class="reader-section reader-module" id="reader-{key}" tabindex="-1" open>')
        self.assertEqual(len(re.findall(r'research-record reader-expand" id="record-[^"]+" open', self.dynamic)), 45)
        self.assertIn('id="record-MET-020" open', self.dynamic)
        self.assertNotIn('<details class="research-ai reader-expand" open>', self.dynamic)
        self.assertNotIn('<details class="missing-fields reader-expand" open>', self.dynamic)
        self.assertEqual(self.dynamic.count('data-gd-chrome="footer"'), 1)

    def test_094_accordion_single_open_behavior_is_removed(self):
        self.assertNotIn('forEach(el=>el.open=el===module)', self.benchmark)
        self.assertNotIn('forEach(m=>m.open=m===el)', self.dynamic)
        self.assertIn('module.open=!module.open', self.benchmark)
        self.assertIn('m.open=!m.open', self.dynamic)
        self.assertIn('function openModule(el){if(el)el.open=true;markModule(el);}', self.dynamic)
        self.assertIn('markReaderModule(null)', self.benchmark)

    def test_094_render_does_not_change_research_snapshot(self):
        project = pp.project(pp.LIB, '2019-s19')
        revision = 'research-%06d' % rw.current(project)['revision']
        folder, _ = rw.check_version(project, revision)
        before = {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}
        workspace_ui.dossier('2019-s19', pp.LIB)
        after = {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
