#!/usr/bin/env python3
"""Connector regressions, including an actual libass frame (no real footage)."""
from pathlib import Path
import subprocess
import tempfile
import unittest

import compositions as c


class ConnectorTests(unittest.TestCase):
    def setUp(self):
        c.EVENTS.clear()

    def test_directional_wrappers_keep_inline_overrides_and_bezier_heads(self):
        for args, helper in [((100, 300, 200), c.arrow_h),
                             ((300, 100, 200), c.arrow_h),
                             ((200, 100, 300), c.arrow_v),
                             ((200, 300, 100), c.arrow_v)]:
            with self.subTest(args=args, helper=helper.__name__):
                c.EVENTS.clear()
                helper(0, 2, *args, alpha=c.A_DIM)
                self.assertEqual(len(c.EVENTS), 2)
                shaft, head = c.EVENTS
                self.assertEqual(shaft.count('{'), 1)
                self.assertEqual(shaft.count('}'), 1)
                self.assertIn(r'\clip(', shaft)
                self.assertIn(r'\1a&H8A', shaft)
                self.assertIn(' b ', shaft)
                self.assertIn(' b ', head)
                self.assertIn('0:00:00.28', head)
                self.assertIn(r'\fad(60,260)', shaft)
                self.assertIn(r'\fad(120,260)', head)

    def test_elbow_is_one_outline_not_overlapping_translucent_segments(self):
        c.connector(0, 2, [(100, 100), (200, 100), (200, 300), (300, 300)],
                    alpha=c.A_DIM)
        shaft = c.EVENTS[0].split('}', 1)[1]
        self.assertEqual(shaft.count('m '), 1)
        self.assertGreaterEqual(shaft.count(' b '), 8)
        self.assertNotIn('nan', shaft)

    def test_dispatch_hands_lanes_to_return_phase_before_return_heads_arrive(self):
        c.fig_dispatch({'type': 'dispatch', 'start': 0, 'end': 20,
                        'title': '派发与回报', 'boss': '包工头',
                        'items': ['子任务 A', '子任务 B', '子任务 C'],
                        't': {'boss': 1, 'workers': 2, 'back': 10}})
        heads = [event for event in c.EVENTS if r'\fad(120,260)' in event]
        self.assertEqual(len(heads), 6)
        for i in range(3):
            outward, returning = heads[i * 2:i * 2 + 2]
            back = 10 + i * .15
            self.assertEqual(outward.split(',')[2], c.at(back + .16))
            self.assertEqual(returning.split(',')[1], c.at(back + .28))
            self.assertEqual(returning.split(',')[2], c.at(20))
            self.assertIn(r'\1a&H8A', returning)

    def test_libass_shows_shafts_in_all_directions_and_rounded_elbow(self):
        c.arrow_h(0, 2, 100, 300, 200)
        c.arrow_h(0, 2, 300, 100, 300, alpha=c.A_DIM)
        c.arrow_v(0, 2, 400, 100, 300)
        c.arrow_v(0, 2, 500, 300, 100)
        c.connector(0, 2, [(600, 200), (700, 200), (700, 400), (800, 400)])
        with tempfile.TemporaryDirectory(prefix='ass-connectors-') as directory:
            ass = Path(directory) / 'probe.ass'
            ass.write_text(c.HEADER + '\n'.join(c.EVENTS) + '\n')
            result = subprocess.run([
                'ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error',
                '-f', 'lavfi', '-i', 'color=black:s=1080x1920:r=1:d=2',
                '-ss', '1', '-vf', f'subtitles={ass}', '-frames:v', '1',
                '-threads', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(len(result.stdout), 1080 * 1920 * 3)

            def pixel(x, y):
                offset = (y * 1080 + x) * 3
                return result.stdout[offset:offset + 3]

            for point in [(200, 200), (200, 300), (400, 200), (500, 200),
                          (650, 200), (700, 300), (750, 400)]:
                with self.subTest(point=point):
                    r, g, b = pixel(*point)
                    self.assertGreater(r, 60)
                    self.assertGreater(g, b + 20)
            # Open chevron: the centre behind the nose stays empty.
            self.assertLess(max(pixel(276, 205)), 10)
            # Proper elbows stay inside the route, not a diagonal shortcut.
            self.assertLess(max(pixel(650, 300)), 10)


if __name__ == '__main__':
    unittest.main()
