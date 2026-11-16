"""Offline CI failure-path and publication checks. No Docker/API calls."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import ci_m2 as ci


def complete_report():
    cases=[dict(canonical_test_id='S'+str(i),status='passed') for i in range(1,13)]
    cases.append(dict(canonical_test_id='P3-CONTRACT-QA_ARTICLES-OBJECT',status='failed',
                      verdicts=dict(business='passed',contract='failed'),cleanup_status='passed'))
    return dict(cases=cases,cleanup='passed',execution_complete=True)


class CI(unittest.TestCase):
    def test_private_acl_failure_blocks_before_credentials_or_API(self):
        with tempfile.TemporaryDirectory() as d,patch.object(ci,'ROOT',Path(d)),patch.object(ci,'source_state',return_value={'harness_sha':'fixture','uncommitted_code':True}),patch.object(ci.subprocess,'run',side_effect=lambda args,**kw:SimpleNamespace(returncode=1 if 'ls-files' in args else 0)),patch.object(ci,'check_private_profile',side_effect=ValueError('BLOCKED_PRIVATE_ACL')),patch.object(ci,'secret_values') as secret,patch.object(ci.p09,'verify') as api:
            self.assertEqual(ci.execute('acl-fixture'),2)
            secret.assert_not_called();api.assert_not_called()
            report=ci.load(Path(d)/'artifacts/runs/m2-ci/acl-fixture/public/ci-summary.json')
            self.assertEqual(report['harness_reason'],'BLOCKED_PRIVATE_ACL')

    def test_tracked_profile_blocks_before_acl_helper_or_secret(self):
        with tempfile.TemporaryDirectory() as d,patch.object(ci,'ROOT',Path(d)),patch.object(ci,'source_state',return_value={'harness_sha':'fixture','uncommitted_code':False}),patch.object(ci.subprocess,'run',return_value=SimpleNamespace(returncode=0)),patch.object(ci,'check_private_profile') as acl,patch.object(ci,'secret_values') as secret:
            self.assertEqual(ci.execute('tracked-profile'),2)
            acl.assert_not_called();secret.assert_not_called()
            self.assertEqual(ci.load(Path(d)/'artifacts/runs/m2-ci/tracked-profile/public/ci-summary.json')['harness_reason'],'PRIVATE_PROFILE_TRACKED')

    def test_remote_dirty_source_never_executes_private_acl_helper(self):
        context={'GITHUB_ACTIONS':'true','GITHUB_EVENT_NAME':'workflow_dispatch','GITHUB_REPOSITORY':'minnhi09/Directus-Testing','GITHUB_REF':'refs/heads/main','GITHUB_SHA':'fixture'}
        with tempfile.TemporaryDirectory() as d,patch.object(ci,'ROOT',Path(d)),patch.dict(ci.os.environ,context),patch.object(ci,'source_state',return_value={'harness_sha':'fixture','uncommitted_code':True}),patch.object(ci,'check_private_profile') as acl,patch.object(ci,'secret_values') as secret:
            self.assertEqual(ci.execute('dirty-source',remote=True),2)
            acl.assert_not_called();secret.assert_not_called()
            self.assertEqual(ci.finalize('dirty-source',remote=True),2)
            acl.assert_not_called();secret.assert_not_called()

    def test_known_fail_is_not_harness_error_or_green(self):
        state=ci.regression_state(complete_report(),1)
        self.assertEqual(state,'KNOWN_TC13_CONTRACT_FAIL')
        self.assertEqual(ci.final_code(state,'FAIL','PASS'),1)
        self.assertEqual(ci.final_code(state,'PASS','PASS'),1)

    def test_cleanup_incomplete_and_exit_mismatch_fail_infrastructure(self):
        for field,value in [('cleanup','failed'),('execution_complete',False)]:
            report=complete_report();report[field]=value
            self.assertEqual(ci.regression_state(report,1),'HARNESS_INFRA_OR_CLEANUP_ERROR')
        self.assertEqual(ci.regression_state(complete_report(),0),'HARNESS_INFRA_OR_CLEANUP_ERROR')
        self.assertEqual(ci.final_code('PASS','NOT_MEASURED','PASS'),2)
        self.assertEqual(ci.final_code('PASS','PASS','UNVERIFIED'),2)

    def test_noncontract_tc13_failure_is_not_known_issue(self):
        report=complete_report();report['cases'][-1]['verdicts']['business']='failed'
        self.assertEqual(ci.regression_state(report,1),'SUT_ASSERTION_FAIL')

    def test_secret_blocks_entire_publication_without_changing_raw(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); source=root/'private';source.mkdir()
            raw=b'{"unchanged":"secret-value-12345678901234567890"}'
            (source/'a.json').write_text('{}');(source/'raw-oas.json').write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'SECRET'):
                ci.publish(source,root/'public',['secret-value-12345678901234567890'])
            self.assertFalse((root/'public').exists())
            self.assertEqual((source/'raw-oas.json').read_bytes(),raw)

    def test_bearer_and_token_patterns_rejected(self):
        for value in [b'Authorization: Bearer abcdefghijklmnopqrstuvwxyz',b'{"access_token":"12345678901234567890"}',b'Set-Cookie: private']:
            with self.assertRaises(ValueError):ci.safe_bytes(value,[])

    def test_escape_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'stage';root.mkdir()
            with self.assertRaises(ValueError):ci.contained(root,root/'../outside')
            with patch.object(Path,'is_symlink',return_value=True):
                with self.assertRaises(ValueError):ci.contained(root,root/'inside')

    def test_clean_publication_has_real_hash_index(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'private';source.mkdir();(source/'report.json').write_text('{"status":"FAIL"}')
            ci.publish(source,root/'public',[])
            index=ci.load(root/'public/artifact-index.json')
            self.assertEqual(index['report.json']['sha256'],ci.hashlib.sha256((source/'report.json').read_bytes()).hexdigest())
            self.assertEqual(ci.load(root/'public/report.json')['status'],'FAIL')
            ci.publish(root/'public',root/'second',[])
            self.assertNotIn('artifact-index.json',ci.load(root/'second/artifact-index.json'))

    def simulate(self, regression_code=1, cleanup='passed', diagnostic_code=0):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);root=Path(self.tmp.name)
        private=root/'runtime/profiles'/ci.NS/'p09.env';private.parent.mkdir(parents=True)
        private.write_text('P09_ADMIN_PASSWORD=private-test-secret-value-123456789\n')
        profile=root/'profile.json';ci.save(profile,{'services':{'runner':{'image':'pinned-test-image'}}})
        files=('scripts/ci_m2.py','scripts/p10_regression.py','scripts/p09_runtime.py','scripts/lab-components.sh','scripts/windows/jq','scripts/check_scenario_contracts.py','scripts/contract_checks.py','.github/workflows/p10-integration-preflight.yml','scripts/private_profile_acl.ps1')
        for name in files:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture-source')
        calls=[]
        def run(args,**kwargs):
            calls.append(args)
            if args[0]=='git':
                return SimpleNamespace(returncode=1 if 'ls-files' in args else 0)
            if 'scripts/p09_runtime.py' in args:
                ci.save(Path(args[args.index('--report')+1]),{'status':'READY'})
                return SimpleNamespace(returncode=0)
            if 'scripts/p10_regression.py' in args:
                rid=args[args.index('--run-id')+1];report=complete_report();report['cleanup']=cleanup
                ci.save(root/'docs/coverage/runs'/rid/'run-report.json',report)
                return SimpleNamespace(returncode=regression_code)
            if args[0]=='docker':
                return SimpleNamespace(returncode=diagnostic_code,stdout=b'{"records":[{"contract_verdict":"FAIL"}]}')
            self.fail('Unexpected process')
        def pack(run,work,dest):dest.mkdir(parents=True)
        with patch.object(ci,'ROOT',root),patch.object(ci,'check_private_profile',return_value={'status':'PASS','secret_bytes_read':0}),patch.object(ci.p09,'PROFILE',profile),patch.object(ci.subprocess,'run',side_effect=run),patch.object(ci.subprocess,'check_output',side_effect=lambda args,**kw: '' if '--others' in args else 'fixture-sha'),patch.object(ci,'pack',side_effect=pack),patch.object(ci.p09,'owned_resources'),patch.object(ci.p09,'private_values',return_value={}),patch.object(ci.p09,'verify',return_value={'checks':{'fixture':True}}):
            code=ci.execute('unit-fixture')
        return code,ci.load(root/'artifacts/runs/m2-ci/unit-fixture/public/ci-summary.json'),calls

    def test_product_exit_one_continues_diagnostic_and_publishes_fail(self):
        code,summary,calls=self.simulate()
        self.assertEqual(code,1)
        self.assertEqual(summary['regression'],'KNOWN_TC13_CONTRACT_FAIL')
        self.assertEqual(summary['diagnostic'],'FAIL')
        self.assertEqual(summary['cleanup'],'PASS')
        self.assertEqual(len([a for a in calls if 'scripts/p10_regression.py' in a]),1)
        self.assertTrue(any(a[0]=='docker' and 'none' in a for a in calls))

    def test_bad_cleanup_stops_before_diagnostic(self):
        code,summary,calls=self.simulate(cleanup='failed')
        self.assertEqual(code,2)
        self.assertFalse(any(a[0]=='docker' for a in calls))
        self.assertEqual(summary['cleanup'],'UNVERIFIED')

    def test_diagnostic_tool_error_is_harness_error(self):
        code,summary,_=self.simulate(diagnostic_code=2)
        self.assertEqual(code,2)
        self.assertEqual(summary['harness_reason'],'DIAGNOSTIC_PROCESS_FAILED')

    def test_publication_error_is_visible_in_uploaded_summary(self):
        with patch.object(ci,'publish',side_effect=ValueError('synthetic-publication-failure')):
            code,summary,_=self.simulate()
        self.assertEqual(code,2)
        self.assertEqual(summary['state'],'BLOCKED_ARTIFACT_SAFETY')
        self.assertEqual(summary['final_exit_code'],2)
        self.assertFalse(summary['publication_complete'])

    def test_workflow_finalizer_and_upload_run_after_failure(self):
        workflow=ci.load(Path(__file__).resolve().parents[1]/'.github/workflows/p10-integration-preflight.yml')
        self.assertEqual(set(workflow['on']),{'workflow_dispatch'})
        job=workflow['jobs']['preflight']
        self.assertIn("refs/heads/main",job['if'])
        self.assertFalse(workflow['concurrency']['cancel-in-progress'])
        self.assertFalse(any(s.get('continue-on-error') for s in job['steps']))
        self.assertEqual([s['if'] for s in job['steps'][-2:]],['always()','always()'])
        self.assertEqual(job['steps'][-1]['with']['if-no-files-found'],'error')
        self.assertTrue(job['steps'][-1]['with']['path'].endswith('/public/'))

    def test_remote_untrusted_context_rejected_before_secret_read(self):
        with patch.dict(ci.os.environ,{},clear=True),patch.object(ci,'secret_values') as secret:
            with self.assertRaisesRegex(ValueError,'UNTRUSTED'):
                ci.execute('untrusted',remote=True)
            secret.assert_not_called()

    def test_remote_sha_and_committed_baseline_are_required(self):
        with self.assertRaisesRegex(ValueError,'REVISION_MISMATCH'):
            ci.check_remote_source({'harness_sha':'actual','uncommitted_code':False},'other')
        with self.assertRaisesRegex(ValueError,'SOURCE_NOT_COMMITTED'):
            ci.check_remote_source({'harness_sha':'actual','uncommitted_code':True},'actual')
        ci.check_remote_source({'harness_sha':'actual','uncommitted_code':False},'actual')
        self.assertIn('docs/coverage/baselines',ci.TRUSTED_INPUTS)

    def test_partial_regression_report_still_collected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);run=root/'run';run.mkdir()
            ci.save(run/'run-report.json',{'status':'BLOCKED','cases':[]})
            ci.collect_regression(run,root/'work',root/'evidence')
            self.assertEqual(ci.load(root/'evidence/run-report.json')['status'],'BLOCKED')

    def test_pack_uses_real_schema_export_and_query_safe_restore_ref(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);work=root/'work';(work/'export').mkdir(parents=True)
            exports=[]
            for i,actor in enumerate(('admin','editor','reader','anonymous')):
                body=b'{"openapi":"3.0.1","paths":{}}'
                schema=work/'schemas/r06-k05-v2'/f'{actor}.json';schema.parent.mkdir(parents=True,exist_ok=True);schema.write_bytes(body)
                (work/'export'/f'http-{i}.json').write_bytes(body)
                exports.append(dict(method='GET',path='/server/specs/oas',actor=actor,status=200,curl_exit_code=0,
                                    trace_version=2,response_ref=f'http-{i}.json',content_type='application/json',recorded_at='OFFLINE_FIXTURE'))
            (work/'export/scenario-trace.ndjson').write_text('\n'.join(map(json.dumps,exports)))
            scenarios=work/'scenarios';scenarios.mkdir();rows=[]
            for i in range(1,9):
                path='/items/qa_articles?limit=-1&sort=id' if i<8 else '/items/qa_categories?limit=-1&sort=id'
                rows.append(dict(scenario='S'+str(i) if i<7 else 'VERIFY',actor='editor' if i<7 else 'admin',
                                 method='GET',path=path,status=200,curl_exit_code=0,trace_version=2,
                                 response_ref=f'http-{i}.json',content_type='application/json',elapsed_seconds=0.1,
                                 http_version='1.1',effective_url='http://127.0.0.1:18055'+path))
                ci.save(scenarios/f'http-{i}.json',{'data':[{'id':1}]})
            (scenarios/'scenario-trace.ndjson').write_text('\n'.join(map(json.dumps,rows)))
            for name in ('scenario-report','scenario-outcomes','database-oracle'):ci.save(scenarios/(name+'.json'),{'fixture':'OFFLINE_ONLY'})
            for coll in ('articles','categories'):ci.save(scenarios/('baseline-'+coll+'.json'),{'data':[{'id':1}]})
            ci.pack(root/'run',work,root/'capture')
            self.assertEqual(len(ci.load(root/'capture/trace.json')),6)
            self.assertEqual(len(ci.load(root/'capture/verification-trace.json')),2)
            metadata=ci.load(root/'capture/schema-metadata.json')
            self.assertEqual(metadata[-1]['actor'],'anonymous');self.assertFalse(metadata[-1]['authorization_sent'])
            # Corruption is rejected, with no fallback to another actor schema.
            (work/'schemas/r06-k05-v2/reader.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'EXPORT_MISMATCH'):ci.pack(root/'run',work,root/'bad-capture')

    def test_missing_pipeline_finalizer_never_claims_cleanup_pass(self):
        with tempfile.TemporaryDirectory() as d,patch.object(ci,'ROOT',Path(d)):
            self.assertEqual(ci.finalize('interrupted'),2)
            result=ci.load(Path(d)/'artifacts/runs/m2-ci/interrupted/public/workflow-finalizer.json')
            self.assertEqual(result['cleanup'],'UNVERIFIED')
            self.assertFalse(result['automatic_reset_or_broad_restore'])


if __name__=='__main__':unittest.main()
