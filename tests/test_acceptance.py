from copy import deepcopy
import unittest
from unittest.mock import patch

from agentguard.acceptance import run_acceptance
from agentguard.scenarios import unsupported_scenario
from agentguard.subscription_demo import acceptance_scenario
from agentguard.verifier import verify_observation
from sample_app.subscription_http import subscription_server


def command(name='Tests'):
    return {'name': name, 'source': 'explicit', 'reason': 'Run existing tests',
            'action': {'type': 'test_command', 'command': ['python3', '-m', 'unittest', 'discover', '-s', 'sample_app/tests', '-v']}}


def unsupported():
    return unsupported_scenario(name='Repeat', source='explicit', reason='Repeat safely', explanation='No multi-step capability')


def envelope(s, code):
    observation = None if code is None else {'type': 'test_result', 'returncode': code}
    return {'execution': {'established': code is not None}, 'observation': observation,
            'result': verify_observation(s, observation)}


class AcceptanceTests(unittest.TestCase):
    def mixed(self, codes, expected):
        scenarios = [command(str(i)) for i in range(len(codes))]
        outputs = [envelope(s, code) for s, code in zip(scenarios, codes)]
        with patch('agentguard.acceptance.execute_test_scenario', side_effect=outputs):
            report = run_acceptance(scenarios)
        self.assertEqual(report['verdict'], expected)
        self.assertEqual(report['results'], outputs)

    def test_empty(self):
        self.assertEqual(run_acceptance([]), {'verdict': 'UNVERIFIED', 'results': []})

    def test_unsupported_never_executes(self):
        s = unsupported()
        with patch('agentguard.acceptance.execute_http_scenario') as http, patch('agentguard.acceptance.execute_test_scenario') as test, patch('agentguard.acceptance.verify_observation', wraps=verify_observation) as verify:
            r = run_acceptance([s])
        http.assert_not_called(); test.assert_not_called(); verify.assert_called_once_with(s)
        self.assertEqual(r['verdict'], 'UNVERIFIED')
        self.assertEqual(r['results'][0], {'execution': {'established': False, 'reason': s['action']['explanation']}, 'observation': None, 'result': verify_observation(s)})

    def test_all_pass(self): self.mixed([0, 0], 'PASS')
    def test_pass_unverified(self): self.mixed([0, None], 'UNVERIFIED')
    def test_pass_fail(self): self.mixed([0, 1], 'FAIL')
    def test_pass_fail_unverified(self): self.mixed([0, 1, None], 'FAIL')

    def test_http_dispatch_and_verdict_ownership(self):
        s = acceptance_scenario()
        # Deliberately inconsistent observation: orchestration must not recompute results.
        supplied = {'execution': {'established': True}, 'observation': {'type': 'http_response', 'status': 500},
                    'result': {'name': s['name'], 'verdict': 'PASS'}}
        with patch('agentguard.acceptance.execute_http_scenario', return_value=supplied) as execute:
            r = run_acceptance([s], base_url='http://127.0.0.1:1234')
        execute.assert_called_once_with(s, base_url='http://127.0.0.1:1234')
        self.assertIs(r['results'][0], supplied)
        self.assertEqual(r['verdict'], 'PASS')

    def test_command_dispatch_recorder(self):
        s = command(); recorder = object()
        with patch('agentguard.acceptance.execute_test_scenario', return_value=envelope(s, 0)) as execute:
            run_acceptance([s], recorder=recorder)
        execute.assert_called_once_with(s, recorder=recorder)

    def test_order_and_nonmutation(self):
        scenarios = [unsupported(), command('second'), acceptance_scenario()]
        before = deepcopy(scenarios)
        with patch('agentguard.acceptance.execute_test_scenario', return_value=envelope(scenarios[1], 0)):
            r = run_acceptance(scenarios)
        self.assertEqual([x['result']['name'] for x in r['results']], [s['name'] for s in scenarios])
        self.assertEqual(scenarios, before)

    def test_rejects_malformed_before_any_execution(self):
        with patch('agentguard.acceptance.execute_test_scenario') as execute:
            with self.assertRaises(ValueError): run_acceptance([command(), {}])
        execute.assert_not_called()

    def test_container_and_count_bound(self):
        for value in (None, {}, (), 'prose', [unsupported()] * 6):
            with self.assertRaises(ValueError): run_acceptance(value)
        self.assertEqual(len(run_acceptance([unsupported()] * 5)['results']), 5)

    def test_missing_http_target(self):
        for value in (None, '', ' ', 1, {}):
            with patch('agentguard.acceptance.execute_http_scenario') as execute:
                r = run_acceptance([acceptance_scenario()], base_url=value)
            execute.assert_not_called()
            self.assertEqual(r['verdict'], 'UNVERIFIED')
            self.assertIsNone(r['results'][0]['observation'])
            self.assertIn('unavailable', r['results'][0]['execution']['reason'])

    def test_invalid_origin_uses_existing_policy(self):
        r = run_acceptance([acceptance_scenario()], base_url='http://example.invalid:80')
        self.assertEqual(r['verdict'], 'UNVERIFIED')
        self.assertFalse(r['results'][0]['execution']['established'])

    def test_infrastructure_inability_preserved(self):
        s = command(); supplied = envelope(s, None)
        supplied['execution']['reason'] = 'Test process timed out'
        with patch('agentguard.acceptance.execute_test_scenario', return_value=supplied):
            r = run_acceptance([s])
        self.assertEqual(r, {'verdict': 'UNVERIFIED', 'results': [supplied]})

    def test_real_controlled_http(self):
        s = acceptance_scenario(); before = deepcopy(s)
        with subscription_server() as base_url:
            r = run_acceptance([s, unsupported()], base_url=base_url)
        self.assertEqual(r['verdict'], 'FAIL')
        first = r['results'][0]
        self.assertEqual(first['observation']['json'], {'status': 'cancelled', 'premium_access': True})
        self.assertEqual([a['verdict'] for a in first['result']['assertions']], ['PASS', 'PASS', 'FAIL'])
        self.assertEqual(r['results'][1]['result']['verdict'], 'UNVERIFIED')
        self.assertEqual(s, before)

    def test_bounded_unsupported_metadata(self):
        s = unsupported(); s['action']['explanation'] = 'x' * 1000
        r = run_acceptance([s])['results'][0]
        self.assertEqual(len(r['execution']['reason']), 512)
        self.assertTrue(r['execution']['reason_truncated'])
        self.assertEqual(r['result']['reason'], 'x' * 1000)

    def test_executor_exception_propagates(self):
        with patch('agentguard.acceptance.execute_test_scenario', side_effect=RuntimeError('unexpected')):
            with self.assertRaisesRegex(RuntimeError, 'unexpected'): run_acceptance([command()])

    def test_unknown_verdict_rejected(self):
        with patch('agentguard.acceptance.execute_test_scenario', return_value={'result': {'verdict': 'MAYBE'}}):
            with self.assertRaises(ValueError): run_acceptance([command()])
