"""One bounded primitive exercised across preservation, transition and deletion."""
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import hashlib
import threading
import unittest
from unittest.mock import Mock, patch

from agentguard.acceptance import run_acceptance
from agentguard.grounding import ground_scenarios
from agentguard.reviewed_workflow import prepare_review, resume_reviewed
from agentguard.scenarios import validate_scenario
from agentguard.sequence_execution import execute_http_sequence
from agentguard.verifier import verify_observation


def step(name, method='GET', path='/record', status=200, **body):
    action = dict(type='http_request', method=method, path=path)
    if body:
        action['json'] = body
    return dict(name=name, action=action, assertions=[dict(type='status', equals=status)])


def equal(left='after', right='before', path='label'):
    return dict(type='json_equal', left=dict(observation=left, path=path),
                right=dict(observation=right, path=path))


def sequence(steps=None, assertions=None):
    return dict(name='Preserve label', source='explicit', reason='Updating state preserves label',
                action=dict(type='http_sequence', steps=steps if steps is not None else [
                    step('before'), step('update', 'PATCH', state='closed'), step('after')]),
                assertions=assertions if assertions is not None else [equal()])


def observation(values):
    return dict(type='http_sequence_result', steps=[dict(name=name, observation=value)
                for name, value in values])


def response(value):
    return dict(type='http_response', status=200, json={'label': value})


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def handle_request(self):
        server = self.server
        server.calls.append((self.command, self.path))
        status = 200
        if self.command == 'PATCH':
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            server.state.update(body)
            if server.corrupt:
                server.state['label'] = 'changed'
        elif self.command == 'DELETE':
            server.deleted = True
            status = 204
        elif server.deleted:
            status = 404
        data = b'' if status == 204 else json.dumps(server.state).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = do_PATCH = do_DELETE = handle_request


class SequenceTests(unittest.TestCase):
    def test_scalar_equality_and_missing_evidence(self):
        s = sequence([step('before'), step('after')])
        for before, after, expected in [(1, 1.0, 'PASS'), (True, 1, 'FAIL'),
                                        (None, None, 'PASS'), ('a', 'b', 'FAIL'),
                                        ({}, {}, 'UNVERIFIED'), ([], [], 'UNVERIFIED')]:
            with self.subTest(before=before, after=after):
                result = verify_observation(s, observation([
                    ('before', response(before)), ('after', response(after))]))
                self.assertEqual(result['verdict'], expected)
        for evidence in [None, observation([]), observation([('before', response('a'))]),
                         observation([('after', response('a')), ('before', response('a'))]),
                         observation([('before', None), ('after', response('a'))]),
                         observation([('before', response('a')), ('after', {'type': 'http_response', 'status': 200, 'json': {}})])]:
            self.assertEqual(verify_observation(s, evidence)['verdict'], 'UNVERIFIED')

    def test_bounded_selected_evidence_and_nonmutation(self):
        s = sequence([step('before'), step('after')])
        evidence = observation([('before', response('x' * 600)), ('after', response('x' * 599 + 'y'))])
        original = deepcopy((s, evidence))
        result = verify_observation(s, evidence)
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertTrue(result['assertions'][0]['observed_truncated'])
        self.assertEqual(len(result['assertions'][0]['observed']), 512)
        self.assertEqual((s, evidence), original)
        self.assertNotIn('observation', result['children'][0])

    def test_schema_rejects_invalid_references_bounds_and_nesting(self):
        mutations = [
            lambda s: s['assertions'][0]['left'].update(observation='unknown'),
            lambda s: s['assertions'][0]['left'].update(path='a..b'),
            lambda s: s['assertions'][0]['left'].update(path='.'.join(['a'] * 9)),
            lambda s: s['assertions'][0]['left'].update(path='x' * 257),
            lambda s: s['action']['steps'][1].update(name='before'),
            lambda s: s['action']['steps'][0].update(name='x' * 65),
            lambda s: s['action']['steps'][0].update(name='bad.name'),
            lambda s: s['action']['steps'].extend([step('four'), step('five')]),
            lambda s: s['action']['steps'].__delitem__(slice(1, None)),
            lambda s: s['assertions'].extend([equal()] * 8),
            lambda s: s['action']['steps'][0].update(assertions=[]),
            lambda s: s['action']['steps'][0].update(assertions=[dict(type='json_exists', path='label')]),
            lambda s: s['action']['steps'][0]['action'].update(type='http_sequence'),
            lambda s: s['action']['steps'][0]['action'].update(json={'text': 'x' * 32000}),
            lambda s: s.update(behavior='extra'),
            lambda s: s['assertions'][0].update(verdict='PASS'),
        ]
        validate_scenario(sequence())
        validate_scenario(sequence([step('one'), step('two'), step('three'), step('four')], []))
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                s = sequence(); mutate(s)
                with self.assertRaises(ValueError): validate_scenario(s)

    def test_grounding_preserves_identity_and_instructions_without_execution(self):
        s = sequence()
        plan = dict(explicit_requirements=['Preserve label'], inferred_behaviors=[], ambiguities=[],
                    scenarios=[dict(name=s['name'], source=s['source'], reason=s['reason'],
                                    behavior='Preserve label when updating state')])
        provider = Mock(return_value=[s])
        with patch('agentguard.sequence_execution.execute_http_scenario', side_effect=AssertionError):
            self.assertEqual(ground_scenarios(plan, 'Documented interface', grounding_provider=provider), [s])
        provider.assert_called_once()
        instructions = provider.call_args.args[0]['instructions']
        for text in ('http_sequence', 'json_equal', 'No output-to-input substitution',
                     'Do not invent state', 'whole scenario', '2–4'):
            self.assertIn(text, instructions)
        bad = deepcopy(s); bad['assertions'][0]['left']['observation'] = 'invented'
        provider.reset_mock(); provider.return_value = [bad]
        with self.assertRaises(ValueError): ground_scenarios(plan, 'Context', grounding_provider=provider)
        provider.assert_called_once()

    def test_untrusted_derivation_fails_whole_sequence(self):
        from agentguard.derivations import materialize
        s = sequence()
        s['action']['steps'][1]['action']['derive'] = [dict(field='name', rule='blank_string', fact_id='unknown')]
        compiled = materialize(s, policy=None, context='Context')
        validate_scenario(compiled)
        self.assertEqual(compiled['action']['type'], 'unsupported')
        self.assertNotIn('assertions', compiled)
        self.assertEqual(compiled['name'], s['name'])
        from agentguard.derivations import InputConstraint, DerivationPolicy
        context = 'PATCH /record accepts arbitrary nonblank label text.'
        fact = InputConstraint('label', 'PATCH', '/record', 'label', context,
                               'string', 'arbitrary_text', nonblank=True)
        policy = DerivationPolicy(hashlib.sha256(context.encode()).hexdigest(), (fact,))
        s['action']['steps'][1]['action']['derive'] = [
            dict(field='label', rule='neutral_nonblank_text', fact_id='label')]
        original = deepcopy(s)
        compiled = materialize(s, policy=policy, context=context)
        validate_scenario(compiled)
        action = compiled['action']['steps'][1]['action']
        self.assertEqual(action['json']['label'], 'agentguard-test')
        self.assertEqual(action['derivations'][0]['context_sha256'], policy.context_sha256)
        self.assertEqual(s, original)

    def test_missing_target_and_infrastructure_stop_without_retry(self):
        for target in (None, '', ' ', 42):
            with patch('agentguard.sequence_execution.execute_http_scenario') as execute:
                result = execute_http_sequence(sequence(), base_url=target)
            execute.assert_not_called()
            self.assertEqual(result['result']['verdict'], 'UNVERIFIED')
            self.assertEqual(len(result['observation']['steps']), 1)
        def unavailable(leaf, **kwargs):
            return dict(execution={'established': False, 'reason': 'Unavailable'},
                        observation=None, result=verify_observation(leaf))
        with patch('agentguard.sequence_execution.execute_http_scenario', side_effect=unavailable) as execute:
            result = execute_http_sequence(sequence(), base_url='http://127.0.0.1:1')
        execute.assert_called_once()
        self.assertEqual(result['result']['verdict'], 'UNVERIFIED')


class SequenceIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.server.daemon_threads = True
        cls.thread = threading.Thread(target=cls.server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self):
        self.server.state = dict(label='fixed', state='open')
        self.server.calls = []
        self.server.deleted = self.server.corrupt = False

    def test_preservation_and_transition_same_primitive_order_and_delegation(self):
        s = sequence()
        s['action']['steps'][0]['assertions'].append(dict(type='json_field', path='state', equals='open'))
        s['action']['steps'][2]['assertions'].append(dict(type='json_field', path='state', equals='closed'))
        original = deepcopy(s)
        with patch('agentguard.sequence_execution.verify_observation', wraps=verify_observation) as verify:
            result = run_acceptance([s], base_url=self.url)
        self.assertEqual(result['verdict'], 'PASS')
        self.assertEqual(self.server.calls, [('GET', '/record'), ('PATCH', '/record'), ('GET', '/record')])
        self.assertEqual(self.server.state['state'], 'closed')
        self.assertEqual(s, original)
        verify.assert_called_once()
        self.assertEqual(verify.call_args.args[1], result['results'][0]['observation'])

    def test_observed_preservation_contradiction(self):
        self.server.corrupt = True
        result = run_acceptance([sequence()], base_url=self.url)
        assertion = result['results'][0]['result']['assertions'][0]
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertEqual((assertion['expected'], assertion['observed']), ('fixed', 'changed'))

    def test_deletion_and_repeated_operation(self):
        s = sequence([step('delete', 'DELETE', status=204), step('again', 'DELETE', status=204),
                      step('absent', status=404)], [])
        result = run_acceptance([s], base_url=self.url)
        self.assertEqual(result['verdict'], 'PASS')
        self.assertEqual(self.server.calls, [('DELETE', '/record'), ('DELETE', '/record'), ('GET', '/record')])

    def test_failed_precondition_stops_later_mutation(self):
        s = sequence()
        s['action']['steps'][0]['assertions'].append(dict(type='json_field', path='state', equals='closed'))
        result = run_acceptance([s], base_url=self.url)['results'][0]
        self.assertEqual(result['result']['verdict'], 'FAIL')
        self.assertEqual(result['result']['assertions'][0]['verdict'], 'UNVERIFIED')
        self.assertEqual(self.server.calls, [('GET', '/record')])
        self.assertTrue(result['execution']['stopped_on_nonpass'])
        self.assertEqual(result['result']['children'][1]['result']['verdict'], 'UNVERIFIED')

    def test_prevalidation_and_caller_snapshot(self):
        bad = sequence(); bad['action']['steps'][-1]['action']['unexpected'] = True
        with self.assertRaises(ValueError): run_acceptance([sequence(), bad], base_url=self.url)
        self.assertEqual(self.server.calls, [])
        from agentguard.sequence_execution import execute_http_scenario
        s = sequence()
        def mutate(leaf, **kwargs):
            s['action']['steps'].clear()
            return execute_http_scenario(leaf, **kwargs)
        with patch('agentguard.sequence_execution.execute_http_scenario', side_effect=mutate):
            self.assertEqual(run_acceptance([s], base_url=self.url)['verdict'], 'PASS')
        self.assertEqual(len(self.server.calls), 3)

    def test_reviewed_workflow_and_legacy_http(self):
        s = sequence(); s['source'] = 'inferred'
        plan = dict(explicit_requirements=['Update state'], inferred_behaviors=['Preserve label'], ambiguities=[],
                    scenarios=[dict(name=s['name'], source=s['source'], reason=s['reason'], behavior='Preserve label')])
        artifact = prepare_review('Update state', 'Documented context', reasoning_provider=lambda _: plan)
        review = artifact['reviews'][0]
        decisions = [dict(revision=artifact['revision'], scenario_id=review['scenario_id'], state='ACCEPTED')]
        provider = Mock(return_value=[s])
        result = resume_reviewed(artifact, decisions, 'Documented context', grounding_provider=provider, base_url=self.url)
        self.assertEqual(result['verification']['verdict'], 'PASS')
        self.assertEqual(result['grounded'][0]['source'], 'inferred')
        provider.assert_called_once()
        leaf = dict(name='Legacy', source='explicit', reason='Observe state', **{k: v for k, v in step('x').items() if k != 'name'})
        self.assertEqual(run_acceptance([leaf], base_url=self.url)['verdict'], 'PASS')
