import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_scenario_contracts import prepare
import scenario_trace as st


class ContractMetadataTests(unittest.TestCase):
    def test_real_capture_has_observed_headers_and_no_silent_contract_pass(self):
        root=Path(__file__).resolve().parents[1]/'docs/coverage/acceptance/P15-HTTP-20261116-01'
        trace=json.loads((root/'trace.json').read_bytes())
        self.assertEqual(len(trace),17)
        self.assertTrue(all(r['trace_version']==2 and isinstance(r['content_type'],str)
                            and r['elapsed_seconds']>=0 and r['http_version'] for r in trace))
        self.assertEqual(sum(r['status']==204 and r['content_type']=='' for r in trace),1)
        result=json.loads((root/'contract-diagnostics.json').read_bytes())['records']
        self.assertEqual(sum(len(r['checks']) for r in result),68)
        self.assertEqual(sum(c['status']=='failed' for r in result for c in r['checks']),12)
        for scenario in ('S1','S2','S3','S4','S5','S6'):
            self.assertTrue(any(r['contract_verdict']=='FAIL' for r in result if r['scenario']==scenario))

    def test_real_reader_steps_are_bound_to_reader_schema_hash(self):
        root=Path(__file__).resolve().parents[1]/'docs/coverage/acceptance/P15-HTTP-20261116-01'
        metadata={r['actor']:r for r in json.loads((root/'schema-metadata.json').read_bytes())}
        result=json.loads((root/'contract-diagnostics.json').read_bytes())['records']
        self.assertTrue(any(r['actor']=='reader' for r in result))
        for record in result:
            self.assertEqual(record['schema_sha256'],metadata[record['actor']]['sha256'])

    def setUp(self):
        self.schema=json.dumps({'openapi':'3.0.1','paths':{'/items/qa_articles':{'get':{}}}}).encode()
        self.body=b'{"data":[]}'
        self.row=dict(trace_version=2,actor='editor',scenario='S1',method='GET',path='/items/qa_articles',
                      status=200,curl_exit_code=0,response_ref='http-1.json',response_sha256=hashlib.sha256(self.body).hexdigest(),
                      content_type='application/json; charset=utf-8',elapsed_seconds=0.01,http_version='1.1',
                      effective_url='http://127.0.0.1:18055/items/qa_articles')
        self.meta=dict(actor='editor',status=200,sha256=hashlib.sha256(self.schema).hexdigest())

    def test_missing_content_type_never_assumed_json(self):
        del self.row['content_type']
        self.assertEqual(prepare(self.row,self.meta,self.schema,self.body)['measurement_status'],'NOT_MEASURED')

    def test_null_content_type_is_unknown_not_observed_absence(self):
        self.row['content_type']=None
        self.assertEqual(prepare(self.row,self.meta,self.schema,self.body)['reason'],'INVALID_HTTP_METADATA')

    def test_reader_or_anonymous_cannot_use_editor_schema(self):
        for actor in ('reader','anonymous'):
            self.row['actor']=actor
            self.assertEqual(prepare(self.row,self.meta,self.schema,self.body)['reason'],'ACTOR_SCHEMA_MISSING_OR_MISMATCH')

    def test_empty_captured_content_type_is_known_absence_not_fabricated_json(self):
        self.row['content_type']=''
        self.assertEqual(prepare(self.row,self.meta,self.schema,self.body)['measurement_status'],'MEASURED')
        self.assertEqual(self.row['content_type'],'')

    def test_hash_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'ACTOR_SCHEMA_HASH'):prepare(self.row,self.meta,self.schema+b' ',self.body)
        with self.assertRaisesRegex(ValueError,'RESPONSE_HASH'):prepare(self.row,self.meta,self.schema,self.body+b' ')

    def test_absent_operation_is_not_contract_pass(self):
        self.row['method']='POST'
        self.assertEqual(prepare(self.row,self.meta,self.schema,self.body)['measurement_status'],'NOT_MEASURED')

    def test_v1_metadata_and_wrong_target_rejected_for_new_capture(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'http-1.json').write_bytes(self.body)
            rows=[dict(self.row,scenario=f'S{i}') for i in range(1,7)]
            self.assertEqual(len(st.validate(rows,p,require_contract_metadata=True)),6)
            rows[0]['trace_version']=1
            with self.assertRaisesRegex(ValueError,'MISSING_HTTP_METADATA'):st.validate(rows,p,require_contract_metadata=True)
            rows[0]=dict(self.row,effective_url='http://example.com/items/qa_articles')
            with self.assertRaisesRegex(ValueError,'HTTP_TARGET_MISMATCH'):st.validate(rows,p,require_contract_metadata=True)

    def test_invalid_timing_or_content_type_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); (p/'http-1.json').write_bytes(self.body)
            rows=[dict(self.row,scenario=f'S{i}') for i in range(1,7)]; rows[0]['elapsed_seconds']=-1
            with self.assertRaisesRegex(ValueError,'INVALID_HTTP_METADATA'):st.validate(rows,p,require_contract_metadata=True)
