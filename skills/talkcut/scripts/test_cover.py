"""Targeted local tests; ImageMagick-dependent tests skip if not installed."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from cover import command, render, shadow_draw


@unittest.skipUnless(shutil.which('magick') and shutil.which('fc-match'), 'ImageMagick/fontconfig required')
class CoverTests(unittest.TestCase):
    def test_gradient_alpha(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'shadow.png'
            command('magick','-size','2560x1440','xc:none','-stroke','none',*shadow_draw('#64A9E8'),p)
            # Straight right-hand edge away from corners: outward alpha decreases.
            alpha=[float(command('magick',p,'-format',f'%[fx:p{{{x},500}}.a]','info:')) for x in (855,862,870,878,880)]
            self.assertGreater(alpha[0],.5)
            self.assertTrue(all(a>=b for a,b in zip(alpha,alpha[1:])))
            self.assertEqual(alpha[-1],0)

    def test_render_dimensions_border_and_sticker(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/'frame.png';out=p/'cover.png';sticker=p/'sticker.png'
            command('magick','-size','1280x720','xc:white',source)
            command('magick','-size','20x20','xc:red',sticker)
            before=source.read_bytes()
            data=render(source,out,stickers=[{'file':str(sticker),'x':2100,'y':700,'width':100}])
            self.assertEqual(command('magick','identify','-format','%w %h',out),b'1280 720')
            self.assertEqual(source.read_bytes(),before)
            self.assertEqual(data['outline'],8)
            self.assertEqual(len(data['stickers']),1)
            self.assertEqual(int(command('magick',out,'-format','%[fx:round(p{1060,360}.r*255)]','info:')),255)
            self.assertLess(float(command('magick',out,'-format','%[fx:p{100,250}.r]','info:')),.15)

    def test_reject_bad_inputs(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/'frame.png';out=p/'cover.png'
            command('magick','-size','400x400','xc:white',source)
            with self.assertRaisesRegex(ValueError,'16:9'):render(source,out)
            with self.assertRaisesRegex(ValueError,'Accent'):render(source,out,accent='blue')
            with self.assertRaisesRegex(ValueError,'different files'):render(source,source)

if __name__=='__main__':unittest.main()
