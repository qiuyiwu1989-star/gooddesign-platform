# coding: utf-8
"""154 产业看台浅色主题与纯净全屏契约。"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'extensions/expo/agent-template.html').read_text(encoding='utf-8')
        cls.chrome = (ROOT / 'scripts/immersive_chrome.py').read_text(encoding='utf-8')
        cls.site_chrome = (ROOT / 'scripts/gooddesign_chrome.py').read_text(encoding='utf-8')

    def test_complete_light_theme_covers_research_and_map(self):
        for selector in (
            'html[data-theme="light"] body:not(.report-mode)',
            'html[data-theme="light"] body:not(.report-mode) .cty',
            'html[data-theme="light"] body:not(.report-mode) .map-tip',
            '#orchestrator,.research-card{background:var(--soft)}',
            '.research-focus{background:var(--panel)',
        ):
            self.assertIn(selector, self.source)

    def test_shared_theme_control_is_connected_without_duplicate(self):
        self.assertIn('<script src="/inno/portal/chrome.js" defer></script>', self.site_chrome)
        self.assertIn('data-gd-theme-toggle', self.site_chrome)
        self.assertNotIn('function syncExpoTheme()', self.source)
        self.assertNotIn("localStorage.setItem('gd-preview-theme'", self.source)

    def test_pure_presentation_hides_real_shared_chrome(self):
        self.assertIn("text = text.replace('<div id=\"run\">', footer() + '</div>\\n<div id=\"run\">', 1)", self.chrome)
        for selector in (
            'body.expo-presenting>header.gd-nav',
            'body.expo-presenting #home>footer.gd-footer',
            'body.expo-presenting #run-controls',
            'body.expo-presenting #rbar',
            'body.expo-presenting .map-tools',
        ):
            self.assertIn(selector, self.source)

    def test_fullscreen_has_user_activation_fallback_and_state_sync(self):
        self.assertIn("button.addEventListener('click', enterPresentation)", self.source)
        self.assertIn('document.documentElement.requestFullscreen()', self.source)
        self.assertIn('/* 权限受限时保留纯净展示 */', self.source)
        self.assertIn("document.addEventListener('fullscreenchange'", self.source)
        self.assertIn("$('#fullscreen-exit').addEventListener('click', exitPresentation)", self.source)
        self.assertIn("if (document.body.classList.contains('expo-presenting')) void exitPresentation()", self.source)

    def test_idle_and_print_preserve_delivery(self):
        self.assertIn("!document.body.classList.contains('expo-presenting')", self.source)
        self.assertIn('@media print{#fullscreen-exit,[data-expo-fullscreen],body>.gd-skip{display:none!important}}', self.source)
        self.assertIn('body.expo-presenting #rbody{padding-bottom:48px}', self.source)


if __name__ == '__main__':
    unittest.main()
