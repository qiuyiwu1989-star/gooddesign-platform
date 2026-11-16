import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/inno-preview/gooddesign-site'


class AwardIcons073Tests(unittest.TestCase):
    def test_073_award_svg_family(self):
        for name in ('gold', 'silver', 'bronze', 'creative', 'nominee', 'elite'):
            path = OUT / 'inno/portal/awards' / f'{name}.svg'
            self.assertTrue(path.is_file(), name)
            text = path.read_text()
            self.assertIn('<svg', text)
            self.assertIn('aria-labelledby', text)
            self.assertNotIn('<text', text)

    def test_073_card_uses_icons_and_text(self):
        script = (ROOT / 'extensions/design-system/portal.js').read_text()
        for award in ('金奖', '银奖', '铜奖', '创意奖', '提名奖', '菁英奖'):
            self.assertIn(award, script)
        self.assertIn('gd-award-icon', script)
        self.assertIn('project.award', script)
        self.assertNotIn('↗', script)

    def test_073_award_gallery(self):
        page = (ROOT / 'extensions/design-system/site-index.html').read_text()
        for name in ('gold', 'silver', 'bronze', 'creative', 'nominee', 'elite'):
            self.assertIn(f'/inno/portal/awards/{name}.svg', page)


if __name__ == '__main__':
    unittest.main()
