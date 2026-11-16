# coding: utf-8
"""153 信息吸收粒子与真实角色频次契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ParticleTests(unittest.TestCase):
    def test_real_particles_and_frequency_contract(self):
        source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        for phrase in ('function spawnInfoParticle(', 'function recordRoleActivity(',
                       'function roleFrequency(', 'className = \'info-particle\'',
                       'existing.length >= 36', 'now - e.t <= 10000',
                       'prefers-reduced-motion: reduce', 'LIVE.roleEvents = {}'):
            self.assertIn(phrase, source, phrase)
        self.assertIn('近 10 秒', source)
        self.assertNotIn('能力评分', source)


if __name__ == '__main__':
    unittest.main()
