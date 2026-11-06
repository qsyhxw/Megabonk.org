"""Image attribution must work without a bibliography; legacy numbered pages stay supported."""
import unittest
from unittest.mock import patch
import guide_images


class CitationModes(unittest.TestCase):
    def render(self, mode, bibliography=''):
        data = {
            'pages': {'/sample/': {'image': 'sample', 'anchor': 'start',
                                  'alt': 'Real game menu', 'purpose': '',
                                  'citation_mode': mode}},
            'media': {'sample': {'source': 'https://example.com/game',
                                 'label': 'Original game', 'detail': 'Menu, checked 5 November 2026.',
                                 'credit': 'Creator', 'stem': '/assets/menu', 'sizes': [480, 640],
                                 'width': 640, 'height': 480}}}
        html = '<html><head></head><body><article class="prose"><section id="start"><h2>Start</h2><p>Open the game.</p></section>' + bibliography + '</article></body></html>'
        with patch.object(guide_images, 'DATA', data):
            return guide_images.decorate('/sample/', html)

    def test_inline_attribution_needs_no_sources_section(self):
        html = self.render('inline')
        self.assertIn('href="https://example.com/game"', html)
        self.assertIn('external website, opens in a new tab', html)
        self.assertNotIn('source-1', html)
        self.assertNotIn('[1]', html)
        self.assertIn('Open the game.', html)

    def test_inline_preserves_existing_compact_notes(self):
        notes = '<section id="sources"><h2>Checks</h2><p>One check.</p></section>'
        self.assertIn(notes, self.render('inline', notes))

    def test_self_explanatory_image_needs_no_visible_caption(self):
        html = self.render('none')
        self.assertNotIn('<figcaption', html)
        self.assertNotIn('https://example.com/game', html)
        self.assertNotIn('source-1', html)
        self.assertIn('alt="Real game menu"', html)
        self.assertIn('href="/assets/menu-640.webp"', html)

    def test_numbered_source_is_reused(self):
        notes = '<section id="sources"><ol><li id="source-7"><a href="https://example.com/game">Original game</a></li></ol></section>'
        html = self.render('numbered', notes)
        self.assertIn('href="#source-7"', html)
        self.assertEqual(html.count('id="source-7"'), 1)
        self.assertNotIn('id="source-8"', html)


if __name__ == '__main__':
    unittest.main()
