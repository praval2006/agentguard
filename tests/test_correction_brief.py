from copy import deepcopy
import unittest
from unittest.mock import patch

from test_acceptance_report import outcome
from agentguard.correction_brief import build_correction_brief, INSTRUCTION


class CorrectionBriefTests(unittest.TestCase):
    def test_fail_only_source_and_exact_evidence(self):
        o = outcome(); b = build_correction_brief(o)
        self.assertEqual(len(b['items']), 1)
        item = b['items'][0]
        self.assertEqual(item['source'], 'inferred')
        self.assertEqual(item['accepted_behavior'], 'Behavior 1')
        self.assertEqual(item['evidence'][0]['assertion'], o['verification']['results'][1]['result']['assertions'][0])
        self.assertEqual(item['instruction'], INSTRUCTION)
        self.assertNotIn('root_cause', item)
        self.assertEqual(b['not_sent_for_correction'][0]['verdict'], 'PASS')
        self.assertEqual([r['review_state'] for r in b['not_verified']], ['DISMISSED', 'PENDING'])
        self.assertEqual(b['ambiguities'], ['Unresolved policy'])

    def test_unverified_no_instruction(self):
        o = outcome(); r = o['verification']['results'][1]['result']
        r.update(verdict='UNVERIFIED', assertions=[], reason='No observation')
        b = build_correction_brief(o)
        self.assertEqual(b['items'], [])
        self.assertEqual(b['not_sent_for_correction'][1]['reason'], 'No observation')
        self.assertNotIn('instruction', b['not_sent_for_correction'][1])

    def test_contract_order(self):
        o = outcome(); r = o['verification']['results'][0]['result']
        r['verdict'] = r['assertions'][0]['verdict'] = 'FAIL'
        r['assertions'][0]['observed'] = 404
        self.assertEqual([i['accepted_behavior'] for i in build_correction_brief(o)['items']], ['Behavior 0', 'Behavior 1'])

    def test_deterministic_detached_no_services(self):
        o = outcome(); before = deepcopy(o)
        with patch('agentguard.verifier.verify_observation', side_effect=AssertionError), patch('agentguard.acceptance.run_acceptance', side_effect=AssertionError), patch('agentguard.providers.openai_provider.OpenAIProvider', side_effect=AssertionError):
            a = build_correction_brief(o); b = build_correction_brief(o)
        self.assertEqual(a, b); self.assertEqual(o, before)
        a['items'][0]['evidence'][0]['assertion']['observed'] = 123
        self.assertEqual(o, before)
        self.assertNotIn('DO NOT EXPORT', str(b))

    def test_missing_evidence_and_inconsistent_identity_rejected(self):
        for mutate in (lambda o: o['verification']['results'][1]['result'].update(assertions=[]),
                       lambda o: o['verification']['results'].reverse(),
                       lambda o: o['contract']['reviews'][2].update(included=True),
                       lambda o: o.update(revision='wrong'),
                       lambda o: o['verification']['results'][1]['result']['assertions'][0].pop('observed')):
            o = outcome(); mutate(o)
            with self.assertRaises(ValueError): build_correction_brief(o)

    def test_size_bound(self):
        o = outcome(); o['verification']['results'][0]['observation'] = 'x' * 1_048_576
        with self.assertRaises(ValueError): build_correction_brief(o)

    def test_nested_failure_preserves_location(self):
        o = outcome(); s = o['grounded'][1]; r = o['verification']['results'][1]['result']
        leaf = deepcopy(r)
        s['behavior'] = 'Behavior 1'
        s['action'] = dict(type='composite', children=[dict(label=n, action=dict(type='http_request', method='GET', path='/x'), assertions=s['assertions']) for n in ('one', 'two')])
        del s['assertions']
        r['assertions'] = []
        r['children'] = [dict(label=n, result=dict(leaf, name=n)) for n in ('one', 'two')]
        e = build_correction_brief(o)['items'][0]['evidence']
        self.assertEqual([x['location'] for x in e], [['one'], ['two']])

    def test_exists_and_type_evidence_preserved(self):
        for a in (dict(type='json_exists', path='x', observed=False, verdict='FAIL', reason='Absent'), dict(type='json_type', path='x', expected='string', observed_type='object', verdict='FAIL', reason=None)):
            o = outcome(); o['verification']['results'][1]['result']['assertions'] = [a]
            self.assertEqual(build_correction_brief(o)['items'][0]['evidence'][0]['assertion'], a)

    def test_command_and_registered_evidence_not_invented(self):
        for registered in (False, True):
            o = outcome(); s = o['grounded'][1]
            s['action'] = (dict(type='registered_check', check_id='check.v1') if registered
                           else dict(type='test_command', command=['python3', '-m', 'unittest']))
            del s['assertions']
            r = o['verification']['results'][1]['result']; r['assertions'] = []
            if registered:
                r.update(check_id='check.v1', coverage_id='coverage.v1', coverage_authorized=True,
                         execution_status='assertion_failure', tests_run=1, failures=1,
                         errors=0, skips=0, expected_failures=0, unexpected_successes=0)
            else:
                r.update(expected=0, observed=1)
            e = build_correction_brief(o)['items'][0]['evidence'][0]['result']
            self.assertEqual(e, r)
            if registered: self.assertNotIn('expected', e)
