"""051 integrity checks: references, provenance, safe reading and immutable delivery."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import method_library_051 as lib


def fixture():
    return {
        'research_id': 'R01', 'method_id': 'IM-ML-001', 'version': '0.1.0', 'name': '方法样本',
        'english_name': 'Fixture', 'kind': 'method', 'category': 'A问题发现与需求定义',
        'summary': '结构校验样本，不是库中方法', 'content_status': 'substantive_draft',
        'execution_status': 'documented_not_runtime_integrated', 'review_status': 'not_expert_reviewed',
        'validation_status': 'not_engineering_validated', 'lineage': [], 'search_terms': ['样本'],
        'sections': {k: '测试结构字段；不是正文质量认证。' for k in lib.SECTIONS},
        'inputs': [{'key': 'task', 'label': '任务', 'type': 'object', 'required': True,
                    'description': '来源明确的任务', 'missing_action': 'ask_or_stop'}],
        'steps': [{'step_id': 'R01-S01', 'title': '核对任务', 'input_refs': ['task'], 'depends_on': [],
                   'operation': '核对对象与目标', 'decision': '对象不明则追问', 'output_key': 'brief',
                   'output_description': '有边界的问题', 'checks': ['目标明确'],
                   'stop_condition': '输入缺失', 'source_refs': ['S01'], 'knowledge_queries': ['任务原文']}],
        'outputs': [{'key': 'brief', 'label': '简报', 'required_fields': ['object'], 'interpretation': '仅支持后续研究'}],
        'relations': [], 'sources': [{'source_id': 'S01', 'publisher': '机构', 'title': '来源',
            'url': 'https://example.org/method', 'locator': '公开说明', 'read_scope': '介绍',
            'supports': ['概念'], 'evidence_note': '测试来源身份', 'rights': '原创释义'}],
        'evaluations': [{'scenario': '输入缺失', 'expected': '追问'}],
    }


class MethodLibrary051Tests(unittest.TestCase):
    def test_valid_structure_not_semantic_certification(self):
        result = lib.validate(fixture(), {'R01'})
        self.assertEqual(result['errors'], [])
        self.assertIn('not_semantic_certification', result['status'])

    def test_forward_reference_and_unknown_input_rejected(self):
        d = fixture()
        d['steps'][0]['depends_on'] = ['R01-S02']
        d['steps'][0]['input_refs'] = ['imaginary']
        self.assertGreaterEqual(len(lib.validate(d)['errors']), 2)

    def test_missing_source_and_unsafe_url_rejected(self):
        d = fixture()
        d['steps'][0]['source_refs'] = ['S99']
        d['sources'][0]['url'] = 'javascript:alert(1)'
        self.assertEqual(len(lib.validate(d)['errors']), 2)

    def test_unproduced_output_and_overwrite_rejected(self):
        d = fixture()
        d['outputs'][0]['key'] = 'unproduced'
        d['steps'][0]['output_key'] = 'task'
        self.assertEqual(len(lib.validate(d)['errors']), 2)

    def test_unknown_relation_and_false_validation_rejected(self):
        d = fixture()
        d['relations'] = [{'target_research_id': 'R99', 'binding': '产物→输入', 'condition': '明确'}]
        d['validation_status'] = 'engineering_validated'
        self.assertEqual(len(lib.validate(d, {'R01'})['errors']), 2)

    def test_html_and_source_identity_preserved(self):
        d = fixture()
        d['name'] = '<script>alert(1)</script>'
        d['sections']['principle'] = '<img src=x onerror=alert(1)>'
        rendered = lib.render_record(d, {'R01': d})
        self.assertNotIn('<script>alert(1)</script>', rendered)
        self.assertNotIn('<img src=x onerror', rendered)
        self.assertIn('source-S01', rendered)
        self.assertIn('核读范围', rendered)

    def test_build_read_and_fingerprint_tamper(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'output') as tmp:
            work, output = Path(tmp) / 'work', Path(tmp) / 'delivery'
            path = work / '批次A/R01/档案.json'
            lib.dump(path, fixture())
            (path.parent / '来源核读.md').write_text('测试记录')
            with self.assertRaises(ValueError):
                lib.build(work, output)
            result = lib.build(work, output, allow_partial=True)
            self.assertEqual(result['methods'], 1)
            self.assertEqual(lib.read('R01', output)['name'], '方法样本')
            self.assertEqual(lib.read('IM-ML-001', output)['research_id'], 'R01')
            self.assertTrue((output/'档案/R01/方法结构.md').exists())
            self.assertIsNone(lib.load(output/'档案/R01/输入模板.json')['inputs']['task']['value'])
            portable = subprocess.run([sys.executable, str(output/'library_cli.py'), 'read',
                                       '--id', 'IM-ML-001', '--level', 'steps', '--step-id', 'R01-S01'],
                                      capture_output=True, text=True)
            self.assertEqual(portable.returncode, 0, portable.stderr)
            self.assertEqual(json.loads(portable.stdout)['steps'][0]['output_key'], 'brief')
            lib.dump(output/'发布冻结.json', {'status': 'frozen'})
            with self.assertRaises(ValueError):
                lib.build(work, output, allow_partial=True)
            self.assertEqual(lib.search('样本', output)['total'], 1)
            with self.assertRaises(ValueError):
                lib.read('../../private', output)
            with self.assertRaises(ValueError):
                lib.read('R01', output, 'steps', 'NONEXISTENT')
            (output / '档案/R01/档案.json').write_text('{}')
            with self.assertRaises(ValueError):
                lib.read('R01', output)

    def test_identity_and_category_must_be_canonical(self):
        d = fixture()
        d['method_id'] = 'IM-ML-01'
        d['category'] = '闻邦椿谱系专题'
        self.assertEqual(len(lib.validate(d)['errors']), 2)

    def test_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'output') as tmp:
            p = Path(tmp) / 'bad.json'
            p.write_text('{"value": NaN}')
            with self.assertRaises(ValueError):
                lib.load(p)


if __name__ == '__main__':
    unittest.main()
