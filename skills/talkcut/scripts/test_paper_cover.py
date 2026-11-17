#!/usr/bin/env python3
"""Small static-image contract checks; no video, ASR or production inputs."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageChops

from paper_cover import build_paper_overlay, make_paper_cover


class PaperCoverTests(unittest.TestCase):
    def test_real_copy_large_fitted_and_recomposable(self):
        copies = [
            ['AI 出图之后', '报价还得人填？'],
            ['图用完就丢？', '提示词也要留下'],
            ['客户一改款', '又得重做一遍？'],
        ]
        with tempfile.TemporaryDirectory(prefix='paper-cover-') as directory:
            root = Path(directory)
            source = root / 'source.png'
            Image.new('RGB', (1080, 1920), '#888888').save(source)
            for index, lines in enumerate(copies, 1):
                with self.subTest(index=index):
                    result = make_paper_cover(
                        source, root / f'{index:02d}-cover.jpg', lines,
                        kicker=f'外贸新品开发   {index:02d} / 04')
                    self.assertEqual(result['copy'], lines)
                    self.assertEqual(len(result['lines']), 2)
                    for line in result['lines']:
                        self.assertGreaterEqual(line['font_size'], 135)
                        x0, y0, x1, y1 = line['box']
                        self.assertTrue(0 <= x0 < x1 <= 1080)
                        self.assertTrue(0 <= y0 < y1 <= 1920)
                    with Image.open(result['outputs']['overlay']) as overlay:
                        self.assertEqual(overlay.mode, 'RGBA')
                        self.assertEqual(overlay.getpixel((0, 0))[3], 0)
                        self.assertEqual(overlay.getbbox(), tuple(result['overlay_bbox']))
                        with Image.open(source) as background, Image.open(result['outputs']['png']) as cover:
                            expected = Image.alpha_composite(background.convert('RGBA'), overlay)
                            difference = ImageChops.difference(expected, cover)
                            self.assertFalse(any(channel.getbbox() for channel in difference.split()))
                    with Image.open(result['outputs']['thumbnail']) as thumb:
                        self.assertEqual(thumb.size, (270, 480))
                    saved = json.loads(Path(result['outputs']['design']).read_text())
                    self.assertEqual(saved['copy'], lines)

    def test_rejects_third_line_empty_lines_and_overflow(self):
        for lines in ([], ['a', 'b', 'c'], ['a\nb'], ['']):
            with self.subTest(lines=lines), self.assertRaises(ValueError):
                build_paper_overlay((1080, 1920), lines)
        with self.assertRaises(ValueError):
            build_paper_overlay((1080, 1920), ['客户一改款'], top=1900)
        with self.assertRaises(ValueError):
            build_paper_overlay((300, 600), ['提示词也要留下'], min_font_size=150)
        with self.assertRaises(ValueError):
            build_paper_overlay((1080, 1920), ['客户一改款'], kicker='系列', top=10)

    def test_parameterized_style_and_static_source_guard(self):
        overlay, result = build_paper_overlay(
            (1080, 1920), ['客户一改款'], top=500, margin=40,
            font_size=160, color='#123456', paper_color='#FFFFEE',
            angles=(2.0,), kicker='系列', kicker_top=390)
        self.assertEqual(result['lines'][0]['font_size'], 160)
        self.assertEqual(result['lines'][0]['box'][:2], [40, 500])
        self.assertEqual(result['foreground'], '#123456')
        self.assertEqual(overlay.size, (1080, 1920))
        with tempfile.TemporaryDirectory(prefix='paper-cover-') as directory:
            root = Path(directory)
            source = root / 'source.png'
            Image.new('RGB', (1080, 1920)).save(source)
            with self.assertRaises(ValueError):
                make_paper_cover(root / 'movie.mp4', root / 'cover.jpg', ['标题'])
            with self.assertRaises(ValueError):
                make_paper_cover(source, source, ['标题'])
            animated = root / 'animated.png'
            Image.new('RGBA', (100, 100), 'red').save(
                animated, save_all=True,
                append_images=[Image.new('RGBA', (100, 100), 'blue')], duration=100)
            with self.assertRaises(ValueError):
                make_paper_cover(animated, root / 'cover.jpg', ['标题'])


if __name__ == '__main__':
    unittest.main()
