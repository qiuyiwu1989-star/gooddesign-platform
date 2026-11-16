import unittest

import project_pipeline as pp
import research_reader_notes as rn
import research_workflow as rw
import steward_dossier_ui


class ArchiveReading100Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html2021 = steward_dossier_ui.render(pp.LIB, '2021-00', '', '')
        cls.html2025 = steward_dossier_ui.render(pp.LIB, '2025-00', '', '')
        cls.html079 = steward_dossier_ui.render(pp.LIB, '2019-s19', '', '')

    def module(self, text, key, next_key):
        return text.split(f'id="reader-{key}"', 1)[1].split(f'id="reader-{next_key}"', 1)[0]

    def test_100_guide_stays_valid_and_uses_human_chapter_summary(self):
        project = pp.project(pp.LIB, '2021-00')
        self.assertEqual(rn.safe_read(project, 'research-000002')['status'], 'available')
        self.assertEqual(self.html2021.count('本章提要'), 8)
        self.assertNotIn('AI阅读导读', self.html2021)
        self.assertNotIn('AI解读 · 未经工程验证', self.html2021)
        primary = self.html2021.split('<section data-panel="archive"', 1)[1].split('<section data-panel="library"', 1)[0]
        self.assertNotIn('AI解读', primary)
        self.assertIn('平台解读聚焦', primary)
        self.assertIn('平台解读 ·', self.html2021)

    def test_100_display_regrouping_does_not_change_research_grouping(self):
        self.assertIn('technology', steward_dossier_ui.MODULE_ENTITIES[1])
        self.assertNotIn('technology', steward_dossier_ui.MODULE_ENTITIES[2])
        self.assertNotIn('technology', steward_dossier_ui.DISPLAY_MODULE_ENTITIES[1])
        self.assertIn('technology', steward_dossier_ui.DISPLAY_MODULE_ENTITIES[2])
        innovation = self.module(self.html2021, 'innovation', 'validation')
        technical = self.module(self.html2021, 'technical', 'innovation')
        self.assertIn('id="record-TECH-HYBRID"', innovation)
        self.assertNotIn('id="record-TECH-HYBRID"', technical)

    def test_100_primary_reading_hides_internal_revision_and_fill_meters(self):
        hero = self.html2021.split('<div class="hero"', 1)[1].split('</div></div>', 1)[0]
        self.assertNotIn('research-000002', hero)
        self.assertIn('项目档案', hero)
        self.assertNotIn('研究整理版', hero)
        self.assertIn('当前研究版本：research-000002', self.html2021)
        self.assertNotIn('当前字段填充率', self.html2021)
        self.assertNotIn('待补信息 ·', self.html2021)
        self.assertNotIn('此处另有若干项尚未登记', self.html2021)
        self.assertIn('尚未经人工逐条核读', self.html2021)

    def test_100_2025_legacy_references_and_platform_entries_render_safely(self):
        self.assertIn('当前研究版本：research-000008', self.html2025)
        self.assertIn('平台解读 · 任务之前的长期准备', self.html2025)
        self.assertIn('367 / 476 项项目事实的来源证据尚待重绑', self.html2025)
        self.assertIn('当前版本评估状态：尚未形成有效评估，旧评估不沿用', self.html2025)
        self.assertNotIn('machine_text_extraction_not_human_read', self.html2025)
        self.assertNotIn('AI阅读导读', self.html2025)
        self.assertIn('机器整理，未经人工逐条核读', self.html2025)
        self.assertIn('下载登记原文件', self.html2025)
        self.assertNotIn('下载保存的原件', self.html2025)

    def test_100_human_units_references_and_source_titles(self):
        self.assertIn('<dt>单位</dt><dd>克</dd>', self.html2025)
        self.assertIn('<dt>单位</dt><dd>毫米</dd>', self.html2025)
        self.assertIn('<dt>单位</dt><dd>转/分钟</dd>', self.html2025)
        self.assertNotIn('<dt>单位</dt><dd>g</dd>', self.html2025)
        self.assertIn('<dt>完成单位</dt><dd>哈尔滨工业大学、北京圣视环宇科技有限公司</dd>', self.html2025)
        self.assertNotIn('<dt>官方证明</dt><dd>S01</dd>', self.html2025)
        self.assertNotIn('data-citation-title="01-星球车复合式移动系统设计及运动性能验证.pdf"', self.html2021)
        self.assertIn('data-citation-title="01-星球车复合式移动系统设计及运动性能验证"', self.html2021)
        self.assertIn('立方米/分钟', self.html079)
        for label in ('毫米', '千克', '安', '％'):
            self.assertIn(label, self.html2021)

    def test_100_complete_reader_has_compact_citations_without_internal_copy(self):
        for text, expected_references in ((self.html2021, 46), (self.html2025, 37)):
            primary = text.split('<section data-panel="archive"', 1)[1].split('<section data-panel="library"', 1)[0]
            for internal_text in ('空白保留', '此处另有若干项尚未登记', '这不是项目方事实陈述，完整状态见维护数据', '研究整理版', '信息记录', '保存的来源文件'):
                self.assertNotIn(internal_text, primary)
            self.assertEqual(text.count('class="reference-item"'), expected_references)
            self.assertIn('注1</button>', text)
            self.assertNotIn('>来源</button>', text)
            self.assertIn('逐字引文与出处', text)
            self.assertIn('原文位置', text)
        self.assertIn('校方报道呈现团队在正式任务前后的持续设计与试验积累', self.html2025)
        self.assertIn('校方介绍高分子团队研制取芯软袋', self.html2025)
        self.assertNotIn('change5_development_history', self.html2025)
        self.assertNotIn('<summary>EVENT-CE6-AIRCAS-DRILL-TIMELINE</summary>', self.html2025)
        self.assertIn('嫦娥六号钻取任务时间线', self.html2025)
        self.assertIn('<details class="research-ai reader-expand" id="record-H01" open><summary>平台解读 · 任务之前的长期准备</summary>', self.html2025)
        self.assertIn('当前研究版本：research-000008', self.html2025)
        self.assertIn('8 个阅读模块', self.html2025)

    def test_100_render_does_not_change_current_research_snapshots(self):
        for pid in ('2021-00', '2025-00'):
            project = pp.project(pp.LIB, pid)
            revision = 'research-%06d' % rw.current(project)['revision']
            folder, _ = rw.check_version(project, revision)
            before = {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}
            steward_dossier_ui.render(pp.LIB, pid, '', '')
            after = {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}
            self.assertEqual(before, after, pid)

    def test_100_079_records_remain_visible(self):
        self.assertEqual(self.html079.count('research-record reader-expand" id="record-'), 45)
        self.assertIn('id="record-MET-020" open', self.html079)
        self.assertIn('平台解读 ·', self.html079)


if __name__ == '__main__':
    unittest.main()
