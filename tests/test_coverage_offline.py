"""Synthetic data only; no SUT, runtime env, packages or historical writes."""
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import coverage_offline as cov


class CoverageOfflineTests(unittest.TestCase):
    def setUp(self):
        self.data = cov.load(cov.ROOT / 'tests/fixtures/coverage-offline')

    def report(self):
        return cov.calculate(self.data, cov.resolve(self.data, True), True)

    def test_manual_many_to_many_alias_fail_blocked_and_source_only(self):
        original = copy.deepcopy(self.data)
        cov.schema_check(self.data)
        cov.reference_check(self.data, True)
        result = self.report()
        self.assertEqual(result['sets'], dict(R=['EXAMPLE-REQ-A','EXAMPLE-REQ-B','EXAMPLE-REQ-C'],
            D=['EXAMPLE-REQ-A','EXAMPLE-REQ-B','EXAMPLE-REQ-C'], E=['EXAMPLE-REQ-A','EXAMPLE-REQ-B'],
            V=['EXAMPLE-REQ-B'], O=['EXAMPLE-OP-DETAIL','EXAMPLE-OP-LIST']))
        self.assertEqual(result['missing_requirement_ids'], ['EXAMPLE-REQ-C'])
        self.assertEqual(result['source_only_ids'], ['EXAMPLE-OP-DETAIL'])
        self.assertEqual(result['metrics']['hit_coverage']['numerator_ids'], ['EXAMPLE-OP-LIST'])
        self.assertEqual(result['observed_execution_dimensions']['cleanup_status']['FAIL'], 1)
        self.assertEqual(self.data, original)

    def test_no_execution_is_not_measured(self):
        self.data['executions'] = []
        result = self.report()
        self.assertEqual(result['metrics']['requirement_design']['measurement_status'], 'MEASURED')
        self.assertEqual(result['metrics']['requirement_execution']['measurement_status'], 'NOT_MEASURED')
        self.assertIsNone(result['metrics']['requirement_verified']['percentage'])

    def test_draft_never_reports_zero_percent(self):
        self.data['selection-manifest']['state'] = 'DRAFT'
        result = self.report()
        self.assertEqual(result['sets']['R'], [])
        self.assertTrue(all(x['percentage'] is None for x in result['metrics'].values()))
        self.assertEqual(len(result['pending_selection_requirement_ids']), 3)

    def test_latest_failed_retry_beats_old_pass_and_keeps_history(self):
        retry = copy.deepcopy(self.data['executions'][0])
        retry.update(execution_id='SAMPLE-RETRY', attempt=2, retry_of_execution_id='SAMPLE-A',
                     execution_status='FAIL', business_verdict='FAIL', tool_status='FAILED', tool_exit_code=1,
                     started_at='2026-01-01T01:00:00Z', finished_at='2026-01-01T01:00:01Z')
        for a in retry['assertion_results']:
            a['verdict'] = 'FAIL'
        self.data['executions'].append(retry)
        result = self.report()
        self.assertEqual(result['sets']['V'], [])
        self.assertIn('SAMPLE-RETRY', result['selected_execution_ids'])
        self.assertNotIn('SAMPLE-A', result['selected_execution_ids'])
        self.assertEqual(len(self.data['executions']), 4)

    def test_predeclared_executions_does_not_choose_other_pass(self):
        selection = self.data['selection-manifest']
        selection.update(run_selection_policy='PREDECLARED_EXECUTIONS', execution_ids=['SAMPLE-B'])
        self.assertEqual(self.report()['sets']['E'], ['EXAMPLE-REQ-A'])

    def test_bad_reference_fails(self):
        self.data['rtm-links'][0]['canonical_test_id'] = 'ABSENT'
        with self.assertRaisesRegex(cov.Invalid, 'TEST_REFERENCE_MISSING'):
            cov.resolve(self.data, True)

    def test_schema_failure_rejected(self):
        self.data['executions'][0]['attempt'] = -1
        with self.assertRaisesRegex(cov.Invalid, 'SCHEMA_VALIDATION_FAILED'):
            cov.schema_check(self.data)

    def test_alias_collision_rejected(self):
        self.data['test-catalog'][1]['aliases'] = ['SAMPLE-ALIAS-A']
        with self.assertRaisesRegex(cov.Invalid, 'AMBIGUOUS_ALIAS'):
            self.report()

    def test_retry_cycle_or_wrong_parent_rejected(self):
        self.data['executions'][0]['retry_of_execution_id'] = 'SAMPLE-A'
        with self.assertRaisesRegex(cov.Invalid, 'RETRY_LINEAGE_INVALID'):
            self.report()

    def test_prerequisite_cycle_rejected(self):
        self.data['test-catalog'][0]['prerequisites'] = ['EXAMPLE-CANONICAL-A']
        with self.assertRaisesRegex(cov.Invalid, 'CATALOG_DEPENDENCY_CYCLE'):
            self.report()

    def test_middleware_deny_not_hit_or_positive(self):
        op = self.data['executions'][0]['operation_evidence'][0]
        op.update(dispatch_verified=False, positive_acceptance=False)
        result = self.report()
        self.assertEqual(result['metrics']['hit_coverage']['numerator_ids'], [])
        self.assertEqual(result['metrics']['positive_acceptance']['numerator_ids'], [])

    def test_cleanup_and_infrastructure_cannot_qualify_pass(self):
        for field, value in [('cleanup_status','FAIL'), ('infrastructure_status','FAILED')]:
            data = copy.deepcopy(self.data)
            data['executions'][0][field] = value
            with self.assertRaisesRegex(cov.Invalid, 'UNQUALIFIED_PASS'):
                cov.resolve(data, True)

    def test_schema_partial_not_invented_as_pass(self):
        self.assertEqual(self.report()['unsupported_metrics']['schema_keyword'], 'NOT_MEASURED')

    def test_mismatched_baseline_rejected(self):
        self.data['executions'][0]['baseline_id'] = 'OTHER'
        with self.assertRaisesRegex(cov.Invalid, 'EXECUTION_BASELINE_MISMATCH'):
            self.report()

    def test_pointer_and_hash_fail_closed(self):
        ref = self.data['executions'][0]['evidence_refs'][0]
        ref.update(kind='ARTIFACT', path='tests/fixtures/coverage-offline/selection-manifest.json',
                   sha256='0'*64)
        with self.assertRaisesRegex(cov.Invalid, 'ARTIFACT_HASH_MISMATCH'):
            cov.reference_check(self.data, True)

    def test_real_mode_refuses_design_examples(self):
        with self.assertRaisesRegex(cov.Invalid, 'EXAMPLE_IN_REAL_BUNDLE'):
            cov.resolve(self.data)

    def test_only_blocked_is_not_evaluable_execution(self):
        self.data['executions'] = [self.data['executions'][2]]
        self.assertEqual(self.report()['metrics']['requirement_execution']['measurement_status'], 'NOT_MEASURED')

    def test_v_needs_mandatory_assertion_for_requirement(self):
        for a in self.data['executions'][0]['assertion_results']:
            if 'EXAMPLE-REQ-B' in a['requirement_ids']:
                a['mandatory'] = False
        self.assertEqual(self.report()['sets']['V'], [])

    def test_utc_order_not_timestamp_spelling(self):
        retry = copy.deepcopy(self.data['executions'][0])
        retry.update(execution_id='SAMPLE-RETRY', attempt=2, retry_of_execution_id='SAMPLE-A',
                     started_at='2026-01-01T01:00:00+02:00', finished_at='2026-01-01T01:00:01+02:00')
        self.data['executions'].append(retry)
        self.assertNotIn('SAMPLE-RETRY', self.report()['selected_execution_ids'])

    def test_non_rest_selection_never_counts_rest(self):
        self.data['selection-manifest']['transports'] = ['GRAPHQL']
        self.assertEqual(self.report()['sets']['O'], [])

    def test_duplicate_assertion_id_is_reference_error(self):
        duplicate = copy.deepcopy(self.data['executions'][0]['assertion_results'][0])
        duplicate['verdict'] = 'FAIL'
        self.data['executions'][0]['assertion_results'].append(duplicate)
        with self.assertRaisesRegex(cov.Invalid, 'DUPLICATE_REGISTRY_KEY'):
            self.report()

    def external_registry(self):
        import hashlib
        path = cov.ROOT / 'docs/coverage/inventory/content-native/capabilities.jsonl'
        record = json.loads(path.read_text(encoding='utf-8').splitlines()[0])
        return dict(format='P08_REFERENCE_REGISTRY_1', records=[dict(id=record['capability_id'],
            kind='CAPABILITY', source_ref=dict(kind='ARTIFACT', path=path.relative_to(cov.ROOT).as_posix(),
            revision=None, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), pointer=None,
            certainty='VERIFIED', gap_ids=[]))])

    def test_proven_sidecar_registry_resolves_gap_target(self):
        registry = self.external_registry()
        self.data['reference-registry'] = registry
        self.data['gaps'][0]['target_ids'].append(registry['records'][0]['id'])
        cov.resolve(self.data, True)

    def test_registry_cannot_invent_id(self):
        self.data['reference-registry'] = self.external_registry()
        self.data['reference-registry']['records'][0]['id'] = 'INVENTED'
        with self.assertRaisesRegex(cov.Invalid, 'EXTERNAL_REGISTRY_ID_MISSING'):
            self.report()

    def test_registry_cannot_change_source_hash(self):
        self.data['reference-registry'] = self.external_registry()
        self.data['reference-registry']['records'][0]['source_ref']['sha256'] = '0'*64
        with self.assertRaisesRegex(cov.Invalid, 'EXTERNAL_REGISTRY_HASH'):
            self.report()

    def test_registry_cannot_bypass_kind(self):
        self.data['reference-registry'] = self.external_registry()
        self.data['reference-registry']['records'][0]['kind'] = 'ANYTHING'
        with self.assertRaisesRegex(cov.Invalid, 'EXTERNAL_REGISTRY_KIND'):
            self.report()

    def test_requirement_group_label_does_not_hide_selected_routes(self):
        self.data['selection-manifest'].update(unit='REQUIREMENT', module_ids=['LEGACY'])
        for req in self.data['requirements']:
            req['module_id'] = 'LEGACY'
        result = self.report()
        self.assertEqual(result['sets']['O'], ['EXAMPLE-OP-DETAIL', 'EXAMPLE-OP-LIST'])


if __name__ == '__main__':
    unittest.main()
