from copy import deepcopy
import unittest
from unittest.mock import patch

from agentguard import subscription_demo as demo
from agentguard.http_execution import execute_http_scenario
from agentguard.scenarios import validate_scenario
from agentguard.verifier import verify_observation
from sample_app import subscription
from sample_app.subscription_http import subscription_server


class SubscriptionDemoTests(unittest.TestCase):
    def test_frozen_scenario_valid_and_fresh(self):
        s = demo.acceptance_scenario()
        validate_scenario(s)
        self.assertEqual(s['source'], 'explicit')
        self.assertEqual(s['action'], {'type': 'http_request', 'method': 'POST', 'path': '/subscriptions/1/cancel'})
        self.assertEqual([a['equals'] for a in s['assertions']], [200, 'cancelled', False])
        s['assertions'].clear()
        self.assertEqual(len(demo.acceptance_scenario()['assertions']), 3)

    def test_real_endpoint_function_call_response_and_verifier(self):
        s = demo.acceptance_scenario(); before = deepcopy(s)
        real = subscription.cancel_subscription
        inputs = []
        def capture(state):
            inputs.append(dict(state))
            return real(state)
        with patch('sample_app.subscription.cancel_subscription', side_effect=capture) as cancel:
            with subscription_server() as base_url:
                self.assertRegex(base_url, r'^http://127\.0\.0\.1:[0-9]+$')
                with patch('agentguard.http_execution.verify_observation', wraps=verify_observation) as verify:
                    r = execute_http_scenario(s, base_url=base_url)
        cancel.assert_called_once()
        self.assertEqual(inputs, [{'status': 'active', 'premium_access': True}])
        self.assertEqual(r['observation'], {'type': 'http_response', 'status': 200,
                                          'json': {'status': 'cancelled', 'premium_access': True}})
        verify.assert_called_once_with(s, r['observation'])
        self.assertEqual(r['result'], verify_observation(s, r['observation']))
        self.assertEqual([a['verdict'] for a in r['result']['assertions']], ['PASS', 'PASS', 'FAIL'])
        self.assertEqual(r['result']['assertions'][2]['observed'], True)
        self.assertEqual(r['result']['verdict'], 'FAIL')
        self.assertEqual(s, before)

    def test_full_demo_contrasts_real_green_tests_with_acceptance_failure(self):
        r = demo.run_demo()
        self.assertEqual(r['implementation_tests']['verdict'], 'PASS')
        self.assertEqual(r['implementation_tests']['observed'], 0)
        self.assertEqual(r['acceptance']['verdict'], 'FAIL')
        self.assertEqual(r['repeated_cancellation']['verdict'], 'UNVERIFIED')
        self.assertIn('fresh state', r['repeated_cancellation']['reason'])
        self.assertNotIn('observation', r)

    def test_fixture_keeps_original_defect_and_object_identity(self):
        state = {'status': 'active', 'premium_access': True}
        self.assertIs(subscription.cancel_subscription(state), state)
        self.assertEqual(state, {'status': 'cancelled', 'premium_access': True})

    def test_fixture_does_not_reimplement_cancellation(self):
        with patch('sample_app.subscription.cancel_subscription', return_value={'status': 'sentinel', 'premium_access': True}):
            with subscription_server() as base_url:
                r = execute_http_scenario(demo.acceptance_scenario(), base_url=base_url)
        self.assertEqual(r['observation']['json']['status'], 'sentinel')

    def test_other_routes_are_not_exposed(self):
        s = demo.acceptance_scenario(); s['action']['path'] = '/unrelated'
        with subscription_server() as base_url:
            r = execute_http_scenario(s, base_url=base_url)
        self.assertEqual(r['observation']['status'], 404)

    def test_report_does_not_hardcode_verdicts(self):
        supplied = {'name': 'sentinel', 'verdict': 'UNVERIFIED', 'reason': 'no evidence'}
        with patch('agentguard.subscription_demo.execute_test_scenario', return_value={'result': supplied}), \
             patch('agentguard.subscription_demo.execute_http_scenario', return_value={'result': supplied, 'execution': {'established': False}}):
            r = demo.run_demo()
        self.assertEqual(r['acceptance'], supplied)
        self.assertEqual(r['implementation_tests'], supplied)
