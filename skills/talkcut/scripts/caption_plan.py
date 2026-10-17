#!/usr/bin/env python3
"""Validate agent-authored semantic cue strings and map them to retained token timing.
No tokenizer, character-count splitter, ASR, rewriting or video mutation.
Usage: caption_plan.py cut.json plan.json -o captions.json
plan.json: {"cues": ["exact retained phrase", ...]}
"""
import argparse
import hashlib
import json
from pathlib import Path


def map_plan(cut, plan):
    chars=[]
    previous=-1.0
    for sentence in cut['sentences']:
        for index,word in enumerate(sentence['words']):
            text=word['text'];a=float(word['start']);b=float(word['end'])
            if not text or b<a or a<previous-0.05:
                raise ValueError(f'Invalid retained token timing at sentence {sentence["id"]}, token {index}')
            previous=a
            for j,ch in enumerate(text):
                chars.append({'text':ch,'start':a+(b-a)*j/len(text),'end':a+(b-a)*(j+1)/len(text),
                              'sentence':sentence['id'],'word':index,'fractional':len(text)>1})
    source=''.join(c['text'] for c in chars)
    phrases=plan.get('cues')
    if not isinstance(phrases,list) or not phrases or any(not isinstance(x,str) or not x.strip() for x in phrases):
        raise ValueError('Expected nonempty agent-authored exact strings in cues[]')
    candidate=''.join(phrases)
    if candidate!=source:
        pos=next((i for i,(a,b) in enumerate(zip(source,candidate)) if a!=b),min(len(source),len(candidate)))
        raise ValueError(f'Cue coverage mismatch at character {pos}: expected {source[max(0,pos-8):pos+16]!r}, got {candidate[max(0,pos-8):pos+16]!r}; no rendering allowed')
    cues=[];offset=0
    for phrase in phrases:
        group=chars[offset:offset+len(phrase)]
        a=group[0]['start'];b=group[-1]['end']
        if b<=a:
            raise ValueError(f'Nonpositive cue duration: {phrase!r}')
        if cues and a<cues[-1]['end']-0.05:
            raise ValueError(f'Overlapping semantic cues: {phrase!r}')
        cues.append({'text':phrase,'start':a,'end':b,'char_start':offset,'char_end':offset+len(phrase),
                     'source_start':{'sentence':group[0]['sentence'],'word':group[0]['word']},
                     'source_end':{'sentence':group[-1]['sentence'],'word':group[-1]['word']},
                     'timing_estimated_within_token':(offset>0 and chars[offset-1]['sentence']==group[0]['sentence'] and chars[offset-1]['word']==group[0]['word']) or
                     (offset+len(phrase)<len(chars) and chars[offset+len(phrase)]['sentence']==group[-1]['sentence'] and chars[offset+len(phrase)]['word']==group[-1]['word'])})
        offset+=len(phrase)
    return {'version':1,'segmentation':'agent-semantic','preferred_chars':[8,12],
            'canonical_sha256':hashlib.sha256(source.encode()).hexdigest(),'character_count':len(source),
            'coverage':'exact','semantic_review':'required','cues':cues}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('cut',type=Path);p.add_argument('plan',type=Path);p.add_argument('-o','--output',type=Path,required=True);a=p.parse_args()
    result=map_plan(json.loads(a.cut.read_text()),json.loads(a.plan.read_text()))
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(result["cues"])} semantic cues, {result["character_count"]} characters; exact coverage (semantic review still required)')

if __name__=='__main__':main()
