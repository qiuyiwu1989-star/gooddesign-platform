# coding: utf-8
"""133 产业看台：真实工作事件与已有成果直达前端契约。"""
import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import expo_agent_server as expo  # noqa: E402


class RetrievalActivityTests(unittest.TestCase):
    def test_candidate_callback_uses_absolute_unique_count(self):
        catalog = {'P1': {'name': '项目一'}, 'P2': {'name': '项目二'}}
        hits = []
        with patch.object(expo.ik, 'search', return_value={'matches': [{'node': {}}, {'node': {}}]}):
            found = expo.retrieve_candidates(
                catalog, {'P1': {}, 'P2': {}}, ['密封'],
                on_hit=lambda pid, term, n: hits.append((pid, n)))
        self.assertEqual(list(found), ['P1', 'P2'])
        self.assertEqual(hits, [('P1', 1), ('P2', 2)])
        with patch.object(expo.ik, 'search', return_value={'matches': [{'node': {}}]}):
            same = expo.retrieve_candidates(catalog, {'P1': {}}, ['密封'], found=found,
                                            on_hit=lambda *args: hits.append(args))
        self.assertIs(same, found)
        self.assertEqual(len(hits), 2)


class ResearchEventTests(unittest.TestCase):
    def test_standard_run_emits_real_artifact_counts(self):
        replies = iter([
            {'theses': [{'id': 'H1', 'text': '本地集群存在升级约束'}]},
            {'headline': '产业界定', 'intro': '概况', 'sectors': ['装备'],
             'sources': [{'title': '公开统计', 'url': 'https://example.com'}]},
            {'facts': [{'label': '产业样本', 'value': '1 个集群', 'status': 'partial'}],
             'benchmarks': [{'place': '对标地', 'similarity': '同类集群', 'lesson': '先验证工艺'}]},
            {'chain': [{'tier': '中游', 'links': ['精密加工']}],
             'companies': [{'name': '样本企业', 'field': '装备', 'reads': ['工艺']}],
             'personas': [{'name': '制造企业', 'pains': ['质量']}]} ,
            {'theses': [{'id': 'H1', 'status': 'partial', 'note': '公开资料部分支撑'}],
             'requirements': [{'id': 'N1', 'text': '提高加工一致性', 'from': '制造企业'}]},
            {'queries': [{'question': '加工一致性', 'terms': ['加工']}]},
            {'matches': [{'question': '加工一致性', 'projects': [
                {'id': 'P1', 'link': '一种机制路径', 'diff': '目标工艺不同'}]}]},
            {'opportunities': [{'title': '工艺验证', 'text': '研究假设',
                                'basis': 'P1', 'verify': '做一次样件验证'}]},
        ])
        stream = io.BytesIO()
        stream.flush = lambda: None
        with patch.object(expo.project_portal, 'catalog', return_value=[
                {'id': 'P1', 'name': '真实项目', 'award': '金奖', 'summary': '真实机制摘要'}]), \
             patch.object(expo, 'ark_chat', side_effect=lambda *a, **kw: next(replies)), \
             patch.object(expo, 'research_indexes', return_value={'P1': {}}), \
             patch.object(expo, 'retrieve_candidates', side_effect=lambda *a, **kw: (
                 kw['on_hit']('P1', '加工', 1), {'P1': {'id': 'P1', 'term': '加工'}})[1]), \
             patch.object(expo, 'store_report', side_effect=lambda place, pack: None):
            expo.Agent({}, '.').run('测试地', stream, depth='standard')
        events = [json.loads(line[6:]) for line in stream.getvalue().decode().splitlines()
                  if line.startswith('data: ')]
        activities = [e for e in events if e['type'] == 'activity']
        by_kind = {e['kind']: e['n'] for e in activities}
        self.assertEqual(by_kind['theses'], 1)
        self.assertEqual(by_kind['sources'], 1)
        self.assertEqual(by_kind['facts'], 1)
        self.assertEqual(by_kind['benchmarks'], 1)
        self.assertEqual(by_kind['companies'], 1)
        self.assertEqual(by_kind['requirements'], 1)
        self.assertEqual(by_kind['checked'], 1)
        self.assertEqual(by_kind['candidates'], 1)
        self.assertEqual(by_kind.get('opportunities'), 1, stream.getvalue().decode())
        self.assertTrue(any(e['type'] == 'pack' for e in events))


class TemplateContractTests(unittest.TestCase):
    def test_cache_roles_and_thought_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        self.assertIn('async function start(query, force = false)', source)
        self.assertIn('if (cached) return openReport(cached);', source)
        self.assertIn("start(place, true)", source)
        self.assertIn("$('#refresh').addEventListener", source)
        self.assertIn("if (evt.type === 'activity') return handleActivity(evt);", source)
        self.assertNotIn('tx.textContent = evt.tail', source)
        self.assertEqual(source.count('skill:'), 7)


if __name__ == '__main__':
    unittest.main()
