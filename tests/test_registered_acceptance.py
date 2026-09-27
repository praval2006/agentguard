import copy
from dataclasses import FrozenInstanceError, replace
import unittest
from unittest.mock import patch

import test_registered_execution as fixtures
from agentguard.acceptance import run_acceptance
from agentguard.coverage_authorization import CoverageAuthorizations, scenario_identity
from agentguard.verifier import verify_observation
from agentguard import registered_execution


class RegisteredAcceptanceTests(unittest.TestCase):
    setUp = fixtures.RegisteredExecutionTests.setUp
    body = fixtures.RegisteredExecutionTests.body

    def auth(self, scenario=None, check='local.one', coverage='behavior.v1'):
        return CoverageAuthorizations(((scenario_identity(scenario or self.scenario), check, coverage),))

    def run_acceptance(self, scenarios=None, **overrides):
        args=dict(repository_root=self.root, registry=self.registry, coverage_authorizations=self.auth())
        args.update(overrides)
        return run_acceptance(scenarios or [self.scenario], **args)

    def test_real_pass(self):
        before=copy.deepcopy(self.scenario)
        r=self.run_acceptance()
        self.assertEqual(r['verdict'],'PASS')
        self.assertTrue(r['results'][0]['result']['coverage_authorized'])
        self.assertEqual(self.scenario,before)

    def test_real_failure(self):
        self.body('self.fail()')
        self.assertEqual(self.run_acceptance()['verdict'],'FAIL')

    def test_missing_configuration(self):
        for key in ('repository_root','registry','coverage_authorizations'):
            with patch('agentguard.acceptance.execute_registered_check') as execute:
                self.assertEqual(self.run_acceptance(**{key:None})['verdict'],'UNVERIFIED')
                execute.assert_not_called()

    def test_mismatched_authorizations(self):
        for auth in (self.auth(check='another'),self.auth(coverage='other'),{},
                     self.auth(scenario={**self.scenario,'name':'different requirement'})):
            with patch('agentguard.acceptance.execute_registered_check') as execute:
                self.assertEqual(self.run_acceptance(coverage_authorizations=auth)['verdict'],'UNVERIFIED')
                execute.assert_not_called()

    def test_changed_scenario(self):
        auth=self.auth()
        for field in ('name','reason','source'):
            changed=copy.deepcopy(self.scenario)
            changed[field]='inferred' if field=='source' else 'different'
            self.assertEqual(self.run_acceptance([changed],coverage_authorizations=auth)['verdict'],'UNVERIFIED')
        changed=copy.deepcopy(self.scenario); changed['action']['check_id']='another'
        self.assertEqual(self.run_acceptance([changed],coverage_authorizations=auth)['verdict'],'UNVERIFIED')

    def test_model_authority_rejected(self):
        for key in ('covered','approved','coverage_id','argv','cwd','environment','executable','timeout'):
            for location in ('action','scenario'):
                s=copy.deepcopy(self.scenario)
                (s['action'] if location=='action' else s)[key]='forged'
                with self.assertRaises(ValueError): self.run_acceptance([s])

    def test_runtime_nonconclusive(self):
        for body, decorator in (('pass','@unittest.skip("skip")'),
                                ('raise RuntimeError()',''),
                                ('self.fail()','@unittest.expectedFailure'),
                                ('pass','@unittest.expectedFailure'),
                                ('os._exit(4)','')):
            self.body(body,decorator)
            self.assertEqual(self.run_acceptance()['verdict'],'UNVERIFIED')

    def test_timeout(self):
        self.body('import time; time.sleep(5)')
        with patch.object(registered_execution,'TIMEOUT_SECONDS',0.1):
            self.assertEqual(self.run_acceptance()['verdict'],'UNVERIFIED')

    def test_configuration_failure(self):
        self.file.unlink(); self.cwd.rmdir()
        self.assertEqual(self.run_acceptance()['verdict'],'UNVERIFIED')

    def test_immutable_bounded_authorizations(self):
        auth=self.auth()
        with self.assertRaises(FrozenInstanceError): auth.entries=()
        for entries in ([], (('x','id'),), (('x','id','coverage'),)*2,
                        (('x'*32001,'id','coverage'),), (('x','id','coverage'),)*101):
            with self.assertRaises(ValueError): CoverageAuthorizations(entries)

    def test_verifier_no_execution_and_malformed_evidence(self):
        o=registered_execution.execute_registered_check(self.scenario,repository_root=self.root,registry=self.registry)
        with patch('subprocess.Popen',side_effect=AssertionError('execution')), \
             patch('builtins.open',side_effect=AssertionError('read')):
            for change in ({'tests_run':True},{'returncode':True},{'timed_out':True},
                           {'coverage_id':'other'},{'check_id':'other'},{'target':'other'},
                           {'errors':1},{'skips':1},{'unexpected_successes':1},
                           {'status':'success','failures':1},{'extra':'log'}):
                r=verify_observation(self.scenario,{**o,**change},registry=self.registry,coverage_authorizations=self.auth())
                self.assertEqual(r['verdict'],'UNVERIFIED')
            self.assertEqual(verify_observation(self.scenario,o)['verdict'],'UNVERIFIED')

    def test_stale_coverage(self):
        auth=self.auth()
        check=self.registry.checks[0]
        self.registry=replace(self.registry,checks=(replace(check,coverage=replace(check.coverage,id='changed')),))
        self.assertEqual(self.run_acceptance(coverage_authorizations=auth)['verdict'],'UNVERIFIED')

    def test_aggregation(self):
        unsupported={'name':'Unknown','source':'explicit','reason':'Requirement',
                     'action':{'type':'unsupported','explanation':'No mechanism'}}
        http={'name':'HTTP','source':'explicit','reason':'Requirement',
              'action':{'type':'http_request','method':'GET','path':'/'},
              'assertions':[{'type':'status','equals':200}]}
        observation={'type':'http_response','status':200}
        envelope={'execution':{'established':True},'observation':observation,
                  'result':verify_observation(http,observation)}
        with patch('agentguard.acceptance.execute_http_scenario',return_value=envelope):
            self.assertEqual(self.run_acceptance([self.scenario,http],base_url='http://127.0.0.1:1234')['verdict'],'PASS')
            self.assertEqual(self.run_acceptance([self.scenario,unsupported])['verdict'],'UNVERIFIED')
            self.body('self.fail()')
            self.assertEqual(self.run_acceptance([self.scenario,http,unsupported],base_url='http://127.0.0.1:1234')['verdict'],'FAIL')

    def test_validate_all_before_execution(self):
        with patch('agentguard.acceptance.execute_registered_check') as execute:
            with self.assertRaises(ValueError): self.run_acceptance([self.scenario,{}])
            execute.assert_not_called()
