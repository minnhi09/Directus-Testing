import sys
import tempfile
from pathlib import Path
import unittest
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import scenario_trace as st


class TraceTests(unittest.TestCase):
    def test_real_bundle_keeps_tc13_and_denials_out_of_dispatch(self):
        import coverage_offline as c
        data=c.load(c.ROOT/'docs/coverage/acceptance/P15-TRACE-20261116-01/bundle')
        result=c.calculate(data,c.resolve(data))
        self.assertEqual(len(result['sets']['V']),12)
        self.assertNotIn('LEGACY-TC13',result['sets']['V'])
        for execution in data['executions']:
            if execution['canonical_test_id'] in ('S4','S5','S6'):
                self.assertEqual(execution['operation_evidence'],[])
        self.assertEqual(result['metrics']['hit_coverage']['numerator_count'],5)
        self.assertEqual(result['metrics']['positive_acceptance']['denominator_count'],5)

    def test_real_anonymous_schema_is_no_auth_and_not_editor(self):
        root=Path(__file__).resolve().parents[1]/'docs/coverage/acceptance/P15-TRACE-20261116-01'
        metadata=next(r for r in json.loads((root/'schema-metadata.json').read_bytes()) if r['actor']=='anonymous')
        self.assertFalse(metadata['authorization_sent'])
        self.assertEqual(st.anonymous_schema_state(metadata['status'],(root/'raw-oas/anonymous.json').read_bytes()),'OPERATION_NOT_IN_ANONYMOUS_OAS')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); (self.root/'http-1.json').write_text('{"data":[]}')
        self.rows=[dict(scenario=f'S{i}',actor='editor',curl_exit_code=0,status=200,
                        path='/items/qa_articles',method='GET',response_ref='http-1.json') for i in range(1,7)]

    def test_integrity_attaches_actual_hashes(self):
        self.assertEqual(len(st.validate(self.rows,self.root)),6)
        self.assertTrue(all(len(r['response_sha256'])==64 for r in st.validate(self.rows,self.root)))

    def test_unknown_actor_and_missing_scenario_rejected(self):
        self.rows[0]['actor']='guessed-admin'
        with self.assertRaisesRegex(ValueError,'UNKNOWN_ACTOR'):st.validate(self.rows,self.root)
        self.rows=self.rows[1:]
        with self.assertRaisesRegex(ValueError,'MISSING_SCENARIO'):st.validate(self.rows,self.root)

    def test_missing_network_response_is_not_denial_pass(self):
        self.rows[0].update(curl_exit_code=7,status=0)
        with self.assertRaisesRegex(ValueError,'NO_HTTP_RESPONSE'):st.validate(self.rows,self.root)

    def test_path_traversal_and_missing_body_rejected(self):
        self.rows[0]['response_ref']='../secret.json'
        with self.assertRaisesRegex(ValueError,'UNSAFE_RESPONSE_REF'):st.validate(self.rows,self.root)
        self.rows[0]['response_ref']='http-999.json'
        with self.assertRaises(FileNotFoundError):st.validate(self.rows,self.root)

    def test_anonymous_schema_does_not_fall_back_to_editor(self):
        self.assertEqual(st.anonymous_schema_state(403,b'{}'),'BLOCKED_SCHEMA_EXPORT')
        self.assertEqual(st.anonymous_schema_state(200,b'{"openapi":"3.0.1","paths":{}}'),'OPERATION_NOT_IN_ANONYMOUS_OAS')
        with self.assertRaises(ValueError):st.anonymous_schema_state(200,b'{"errors":[]}')

    def test_empty_204_valid_but_empty_200_not_json_evidence(self):
        (self.root/'http-2.json').write_bytes(b'')
        self.rows[0].update(method='DELETE',status=204,response_ref='http-2.json')
        self.assertEqual(len(st.validate(self.rows,self.root)),6)
        self.rows[0]['status']=200
        with self.assertRaises(ValueError):st.validate(self.rows,self.root)
