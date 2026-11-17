#!/usr/bin/env python3
"""Render a plain series cover over an existing frame; never edit the video.
Requires ImageMagick 7 and a local CJK font (fontconfig helps locate it).
Example: cover.py frame.png -o cover.png --title 外贸新品开发 --part 上
Coordinates use a 2560x1440 design canvas, scaled to the input's 16:9 size.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def command(*args):
    return subprocess.check_output([str(x) for x in args])


def resolve_font(font):
    if font:
        return str(font)
    if not shutil.which('fc-match'):
        raise ValueError('Pass --font with the path to a local CJK bold font')
    return command('fc-match', '-f', '%{file}', 'Noto Sans CJK SC:style=Bold').decode().strip()


def shadow_draw(accent, extent=28):
    """Source-over nested offsets: near edge solidifies, outer edge fades to zero.

    The opaque white card covers the interior. The farthest translated rounded
    rectangle has zero alpha; there is no opaque blue ledge or colored glow.
    """
    rgb=tuple(int(accent[i:i+2],16) for i in (1,3,5))
    args=[]
    for distance in range(extent,0,-1):
        alpha=.13*(1-distance/extent)
        args+=['-fill',f'rgba({rgb[0]},{rgb[1]},{rgb[2]},{alpha:.6f})']
        for x,y,w,h in ((200,385,650,240),(200,650,1700,270)):
            args+=['-draw',f'roundrectangle {x+distance},{y+distance} {x+w+distance},{y+h+distance} 22,22']
    return args


def render(source, output, *, title='外贸新品开发', part='上', kicker='AI', accent='#64A9E8', outline=8, font=None, stickers=None):
    if not shutil.which('magick'):
        raise ValueError('ImageMagick 7 (magick) is required')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',accent):
        raise ValueError('Accent must be a six-digit hex color')
    if not title.strip() or not kicker.strip() or not part.strip():
        raise ValueError('Title, kicker and part must be nonempty')
    if not 1<=outline<=20:
        raise ValueError('Outline must be between 1 and 20 design pixels')
    source=Path(source).resolve();output=Path(output).resolve()
    if source==output:
        raise ValueError('Source frame and output must be different files')
    width,height=map(int,command('magick','identify','-format','%w %h',source).split())
    if abs(width/height-16/9)>.01:
        raise ValueError('This layout expects a 16:9 frame; do not silently crop footage')
    font=resolve_font(font)
    title_size=186
    while title_size>=80:
        measured=int(command('magick','-font',font,'-pointsize',title_size,f'label:{title}','-format','%w','info:'))
        if measured<=1220:break
        title_size-=2
    if measured>1220:
        raise ValueError('Title is too long; shorten the copy instead of making unreadable text')
    kicker_width=int(command('magick','-font',font,'-pointsize','186',f'label:{kicker}','-format','%w','info:'))
    if kicker_width>300:
        raise ValueError('Kicker is too long for this two-line layout')
    prepared=[]
    for sticker in stickers or []:
        file=Path(sticker['file']).resolve()
        x,y,size=(int(sticker[k]) for k in ('x','y','width'))
        if not file.is_file() or file.suffix.lower() not in ('.png','.svg'):
            raise ValueError('Sticker must be a trusted local PNG/SVG file')
        sw,sh=map(int,command('magick','identify','-format','%w %h',file).split())
        if min(sw,sh)<=0 or size<=0 or x<0 or y<0 or x+size>2560 or y+size*sh/sw>1440:
            raise ValueError('Sticker lies outside the design canvas')
        prepared.append({'file':str(file),'x':x,'y':y,'width':size})
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='cover-',dir=output.parent) as td:
        td=Path(td);shadow=td/'shadow.png';overlay=td/'overlay.png'
        command('magick','-size','2560x1440','xc:none','-stroke','none',*shadow_draw(accent),shadow)
        command('magick',shadow,'-fill','#FFFFFF','-stroke','#101010','-strokewidth',outline,
                '-draw','roundrectangle 200,385 850,625 22,22',
                '-draw','roundrectangle 200,650 1900,920 22,22',
                '-stroke','none','-font',font,'-fill','#101010','-pointsize','186','-annotate','+260+576',kicker,
                '-fill',accent,'-annotate','+550+576','×',
                '-fill','#101010','-pointsize',title_size,'-annotate','+260+851',title,
                '-pointsize','86','-annotate','+1515+830',f'（{part}）',
                '-resize',f'{width}x{height}!',overlay)
        layers=[]
        scale=width/2560
        for i,sticker in enumerate(prepared):
            layer=td/f'sticker-{i}.png'
            command('magick','-background','none',sticker['file'],'-filter','point',
                    '-resize',f'{round(sticker["width"]*scale)}x',layer)
            layers += [str(layer),'-geometry',f'+{round(sticker["x"]*scale)}+{round(sticker["y"]*scale)}',
                       '-compose','over','-composite']
        command('magick',source,overlay,'-compose','over','-composite',*layers,output)
    return {'canvas':[width,height],'text':[kicker+' ×',title+f'（{part}）'],
            'font':font,'accent':accent,'outline':outline,'shadow':'directional outward alpha fade to zero',
            'shadow_extent':28,'source':str(source),'stickers':prepared,'scope':'independent image; video untouched'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('-o','--output',type=Path,required=True)
    p.add_argument('--title',default='外贸新品开发');p.add_argument('--part',default='上')
    p.add_argument('--kicker',default='AI');p.add_argument('--accent',default='#64A9E8')
    p.add_argument('--outline',type=int,default=8);p.add_argument('--font',type=Path)
    p.add_argument('--stickers',type=Path,help='JSON list of trusted local PNG/SVG files with x,y,width in design pixels')
    a=p.parse_args()
    stickers=json.loads(a.stickers.read_text()) if a.stickers else []
    for s in stickers:
        file=Path(s['file'])
        if not file.is_absolute():s['file']=str(a.stickers.resolve().parent/file)
    result=render(a.source,a.output,title=a.title,part=a.part,kicker=a.kicker,accent=a.accent,outline=a.outline,font=a.font,stickers=stickers)
    a.output.with_suffix('.design.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(a.output)

if __name__=='__main__':main()
