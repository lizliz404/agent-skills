#!/usr/bin/env python3
"""Small isolated regressions: python -m unittest discover -s scripts -p test_caption_plan.py"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from caption_plan import map_plan

ROOT=Path(__file__).resolve().parent

class CaptionPlanTests(unittest.TestCase):
    def setUp(self):
        self.cut={'media':'missing.mp4','sentences':[{'id':1,'words':[{'text':'工厂','start':0,'end':1},{'text':'能做的','start':1,'end':2}]},{'id':2,'words':[{'text':'新品','start':2.5,'end':3.5}]}]}

    def test_exact_coverage_and_cross_sentence(self):
        result=map_plan(self.cut,{'cues':['工厂能做的新品']})
        self.assertEqual(result['coverage'],'exact');self.assertEqual(result['cues'][0]['end'],3.5)
        self.assertFalse(result['cues'][0]['timing_estimated_within_token'])

    def test_no_length_quota(self):
        result=map_plan(self.cut,{'cues':['工厂','能做的新品']})
        self.assertEqual(len(result['cues']),2)

    def test_reject_omission_duplication_and_empty(self):
        for cues in (['工厂能做的新'],['工厂工厂能做的新品'],[],['']):
            with self.subTest(cues=cues),self.assertRaises(ValueError):map_plan(self.cut,{'cues':cues})

    def test_subtoken_boundary_is_disclosed(self):
        result=map_plan(self.cut,{'cues':['工厂能','做的新品']})
        self.assertTrue(result['cues'][0]['timing_estimated_within_token'])
        self.assertTrue(result['cues'][1]['timing_estimated_within_token'])

    def test_invalid_time_is_rejected(self):
        self.cut['sentences'][0]['words'][1]['end']=.5
        with self.assertRaises(ValueError):map_plan(self.cut,{'cues':['工厂能做的新品']})

    def test_burn_gates_precede_media_probe(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);cut=p/'cut.json';cut.write_text(json.dumps(self.cut))
            args=[sys.executable,str(ROOT/'subs.py'),str(cut),'--burn']
            result=subprocess.run(args,capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertIn('requires --caption-plan',result.stderr)
            plan=p/'plan.json';plan.write_text(json.dumps({'cues':['工厂能做的新品']}))
            result=subprocess.run(args+['--caption-plan',str(plan)],capture_output=True,text=True)
            self.assertEqual(result.returncode,2);self.assertIn('must be reviewed',result.stderr)
            plan.write_text(json.dumps({'reviewed':True,'cues':['wrong']}))
            result=subprocess.run(args+['--caption-plan',str(plan)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertIn('coverage mismatch',result.stderr)

if __name__=='__main__':unittest.main()
