import copy
import sys
from pathlib import Path
import unittest
import tempfile
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from p14_pilot import scoped, overlay


class PilotScopeTests(unittest.TestCase):
    def test_completed_guided_resume_stops_before_credentials_or_mutation(self):
        import p14_pilot as p
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); out=root/'docs/coverage/runs/P14-20261116-01/guided'; out.mkdir(parents=True)
            (out/'report.json').write_text('{}')
            with patch.object(p,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'already recorded'): p.main('P14-20261116-01',True)

    def setUp(self):
        self.collection='qa_sys_categories_offline'
        self.path='/items/'+self.collection
        operation={'responses':{'200':{'description':'unchanged'}},'parameters':[{'name':'id','in':'path','schema':{'type':'integer'}}],
                   'requestBody':{'content':{'application/json':{'schema':{'type':'object'}}}}}
        self.raw={'openapi':'3.0.1','paths':{self.path:{m:copy.deepcopy(operation) for m in ('get','post','patch','delete')},self.path+'/{id}':{m:copy.deepcopy(operation) for m in ('get','patch','delete')},'/users':{'get':operation}},'components':{'schemas':{}}}

    def test_scope_exactly_five_without_admin_routes_or_bulk(self):
        value=scoped(self.raw,self.collection)
        self.assertEqual(sum(len(v) for v in value['paths'].values()),5)
        self.assertEqual(set(value['paths']),{self.path,self.path+'/{id}'})

    def test_overlay_does_not_mutate_raw_or_response_contract(self):
        before=copy.deepcopy(self.raw); raw=scoped(self.raw,self.collection); guided=overlay(raw,self.collection,[91])
        self.assertEqual(self.raw,before)
        for path,methods in raw['paths'].items():
            for method,op in methods.items(): self.assertEqual(op['responses'],guided['paths'][path][method]['responses'])
        self.assertEqual(guided['paths'][self.path]['post']['requestBody']['content']['application/json']['example'],{'name':'P14 valid category'})

    def test_missing_actor_operation_fails_before_run(self):
        del self.raw['paths'][self.path]['post']
        with self.assertRaises(ValueError): scoped(self.raw,self.collection)
