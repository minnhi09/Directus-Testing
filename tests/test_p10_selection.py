import copy
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import p10_selection as p


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.base=json.loads(p.BASE.read_text())
        self.selected=copy.deepcopy(self.base)
        self.selected['run_ids']=['OFFLINE-TEST-ONLY']
        self.selected['execution_ids']=['OFFLINE-TEST-'+str(i) for i in range(13)]

    def test_exact_selection(self):
        self.assertTrue(p.validate(self.selected,self.base)['valid'])

    def test_alias_duplicate_rejected(self):
        self.selected['tests'][1]=self.selected['tests'][0]
        with self.assertRaises(ValueError): p.validate(self.selected,self.base)

    def test_contract_case_cannot_be_dropped(self):
        self.selected['tests']=self.selected['tests'][:-1]
        with self.assertRaises(ValueError): p.validate(self.selected,self.base)

    def test_duplicate_execution_rejected(self):
        self.selected['execution_ids'][1]=self.selected['execution_ids'][0]
        with self.assertRaises(ValueError): p.validate(self.selected,self.base)

    def test_mandatory_or_denominator_cannot_be_relaxed(self):
        for field,value in [('requirement_ids',[]),('retry_policy','LATEST_PASS')]:
            selected=copy.deepcopy(self.selected); selected[field]=value
            with self.assertRaises(ValueError): p.validate(selected,self.base)
