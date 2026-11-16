"""Offline P01 1.1 tests on P10-derived evidence; no API or artifact writes."""
import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import coverage_offline as c


class ScopedAssertionTests(unittest.TestCase):
    def setUp(self):
        self.data=c.load(c.ROOT/'docs/coverage/acceptance/M2-COVERAGE-20261116/bundle')

    def tc13(self):
        return next(r for r in self.data['executions'] if r['canonical_test_id']=='P3-CONTRACT-QA_ARTICLES-OBJECT')

    def test_real_scope_13_evaluated_12_verified_tc13_excluded(self):
        original=copy.deepcopy(self.data)
        c.schema_check(self.data); c.reference_check(self.data,False)
        result=c.calculate(self.data,c.resolve(self.data))
        self.assertEqual([len(result['sets'][k]) for k in ('R','D','E','V')],[13,13,13,12])
        self.assertNotIn('LEGACY-TC13',result['sets']['V'])
        self.assertEqual(result['observed_execution_dimensions']['contract_verdict'],{'NOT_RUN':12,'FAIL':1})
        self.assertEqual(self.data,original)

    def test_v1_schema_and_legacy_result_remain_unchanged(self):
        old=c.load(c.ROOT/'docs/coverage/acceptance/M2-P15-20261116/bundle')
        c.schema_check(old)
        self.assertEqual(c.calculate(old,c.resolve(old))['sets']['V'],[])

    def test_cannot_turn_tc13_fail_into_pass(self):
        self.tc13()['execution_status']='PASS'
        with self.assertRaises(c.Invalid):c.resolve(self.data)

    def test_contract_mandatory_cannot_be_removed_from_scope(self):
        e=next(x for x in self.data['assertion-scopes']['entries'] if x['canonical_test_id']==self.tc13()['canonical_test_id'])
        e['mandatory_dimensions']=['BUSINESS']
        with self.assertRaisesRegex(c.Invalid,'CONTRACT_SCOPE_CANNOT_BE_REMOVED'):c.resolve(self.data)

    def test_missing_contract_evidence_never_passes(self):
        r=self.tc13(); r.update(execution_status='PASS',contract_verdict='NOT_RUN')
        r['assertion_results']=[a for a in r['assertion_results'] if a['dimension']!='CONTRACT']
        with self.assertRaisesRegex(c.Invalid,'MANDATORY_DIMENSION'):c.resolve(self.data)

    def test_empty_scope_cannot_pass(self):
        self.data['assertion-scopes']['entries'][0]['mandatory_dimensions']=[]
        with self.assertRaisesRegex(c.Invalid,'BUSINESS_SCOPE_CANNOT_BE_REMOVED'):c.resolve(self.data)

    def test_missing_evidence_not_a_pass(self):
        self.data['executions'][0]['assertion_results'][0]['evidence_refs']=[]
        with self.assertRaisesRegex(c.Invalid,'MANDATORY_DIMENSION'):c.resolve(self.data)

    def test_oracle_scope_cannot_be_rebound(self):
        self.data['assertion-scopes']['entries'][0]['source_refs']=[]
        with self.assertRaisesRegex(c.Invalid,'ASSERTION_SCOPE_ORACLE_BINDING'):c.resolve(self.data)

    def test_unprovided_scope_or_wrong_baseline_rejected(self):
        original=copy.deepcopy(self.data)
        del self.data['assertion-scopes']
        with self.assertRaisesRegex(c.Invalid,'ASSERTION_SCOPE_MISSING'):c.resolve(self.data)
        self.data=original; self.data['assertion-scopes']['baseline_id']='OTHER'
        with self.assertRaisesRegex(c.Invalid,'ASSERTION_SCOPE_BASELINE'):c.resolve(self.data)

    def test_auth_dimension_not_silently_discarded(self):
        r=next(r for r in self.data['executions'] if r['canonical_test_id']=='P3-AUTHZ-DR-047')
        r['assertion_results']=[a for a in r['assertion_results'] if a['dimension']!='AUTHORIZATION']
        with self.assertRaisesRegex(c.Invalid,'MANDATORY_DIMENSION'):c.resolve(self.data)

    def test_cleanup_failure_rejects_pass(self):
        self.data['executions'][0]['cleanup_status']='FAIL'
        with self.assertRaisesRegex(c.Invalid,'UNQUALIFIED_PASS'):c.resolve(self.data)

    def test_bad_evidence_hash_rejected(self):
        self.data['executions'][0]['evidence_refs'][0]['sha256']='0'*64
        with self.assertRaisesRegex(c.Invalid,'ARTIFACT_HASH_MISMATCH'):c.reference_check(self.data,False)

    def test_unsupported_version_has_no_schema_fallback(self):
        with self.assertRaisesRegex(c.Invalid,'UNSUPPORTED_EXECUTION_SCHEMA_VERSION'):
            c.bundle_schema('executions','9.0.0')
