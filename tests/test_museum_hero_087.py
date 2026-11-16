import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'


class MuseumHero087Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = (OUT / 'inno/portal/museum-hero.css').read_text(encoding='utf-8')

    def test_087_new_palette_replaces_blue_gradient(self):
        self.assertIn('linear-gradient(135deg, #15151c 0%, #1d1d27 52%, #27232f 100%)', self.css)
        self.assertNotIn('#2D4FAF', self.css)
        self.assertNotIn('#5984D6', self.css)
        self.assertIn('border-bottom: 1px solid rgba(255,255,255,.08)', self.css)

    def test_087_typography_and_readability(self):
        self.assertIn('font-family: var(--font-sans)', self.css)
        self.assertIn('color: rgba(236,238,255,.76)', self.css)
        self.assertIn('color: rgba(236,238,255,.56)', self.css)
        self.assertIn('color: #F59A82', self.css)
        self.assertIn('line-height: 1.95', self.css)

    def test_087_mobile_and_no_decorative_glow(self):
        self.assertIn('@media (max-width: 860px)', self.css)
        self.assertIn('@media (max-width: 480px)', self.css)
        self.assertIn('display: none;', self.css)
        self.assertNotIn('radial-gradient', self.css)

    def test_087_override_loads_after_legacy_inline_styles(self):
        for name in ('inno/museum/index.html', 'categories.html'):
            text = (OUT / name).read_text(encoding='utf-8')
            self.assertGreater(text.index('/inno/portal/museum-hero.css'), text.index('<style>'), name)
            self.assertEqual(text.count('/inno/portal/museum-hero.css'), 1, name)

    def test_087_asset_is_local_and_self_contained(self):
        self.assertNotIn('fonts.googleapis.com', self.css)
        self.assertNotIn('url(', self.css)
        self.assertIn('font-size: 36px', self.css)


if __name__ == '__main__':
    unittest.main()
