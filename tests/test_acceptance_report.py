"""Report projections use completed outputs, with no model or verification calls."""
from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agentguard.acceptance_contract import create_proposal, build_contract
from agentguard.acceptance_report import build_acceptance_report, format_acceptance_report, report_json
from agentguard import cli


def outcome():
    plan = dict(explicit_requirements=['Original requirement', 'Unrepresented requirement'],
                inferred_behaviors=['Suggested behavior'], ambiguities=['Unresolved policy'],
                scenarios=[dict(name=f'Check {i}', source=source, behavior=f'Behavior {i}', reason='Rationale')
                           for i, source in enumerate(('explicit', 'inferred', 'inferred', 'inferred'))])
    proposal = create_proposal(plan)
    decisions = [dict(revision=proposal.revision, scenario_id=f'{proposal.revision}:scenario:{i}', state=state)
                 for i, state in ((2, 'ACCEPTED'), (3, 'DISMISSED'))]
    contract = build_contract(proposal, decisions)
    grounded = [dict(name=s['name'], source=s['source'], reason=s['reason'],
                     action=dict(type='http_request', method='GET', path='/record'),
                     assertions=[dict(type='status', equals=200)]) for s in contract['selected_plan']['scenarios']]
    envelopes = [dict(execution=dict(established=True, status=200), observation={'raw': 'DO NOT EXPORT'},
                      result=dict(name=s['name'], source=s['source'], verdict=v, reason=None,
                                  assertions=[dict(type='status', expected=200, observed=n, verdict=v, reason=None)]))
                 for s, v, n in zip(grounded, ('PASS', 'FAIL'), (200, 400))]
    return dict(revision=proposal.revision, proposal=plan, contract=contract, grounded=grounded,
                verification=dict(verdict='FAIL', results=envelopes))


class ReportTests(unittest.TestCase):
    def test_review_categories_contract_and_unlinked_requirements(self):
        r = build_acceptance_report(outcome())
        self.assertEqual([x['review_state'] for x in r['reviews']], [None, 'ACCEPTED', 'DISMISSED', 'PENDING'])
        self.assertEqual(len(r['contract']['scenarios']), 2)
        self.assertEqual(r['contract']['scenarios'][1]['source'], 'inferred')
        self.assertEqual(r['verification']['results'][1]['result']['verdict'], 'FAIL')
        self.assertFalse(any('verdict' in x for x in r['reviews']))
        self.assertEqual(r['discovery']['explicit_requirements'][-1], 'Unrepresented requirement')
        self.assertEqual(r['discovery']['ambiguities'], ['Unresolved policy'])
        self.assertEqual(r['requirement_mapping']['state'], 'NO_STRUCTURED_SCENARIO_LINKS')
        self.assertEqual(r['summary']['verdict_counts'], dict(PASS=1, FAIL=1, UNVERIFIED=0))
        self.assertEqual(r['summary']['pending_inferred'], 1)

    def test_verdict_is_copied_not_aggregated(self):
        o = outcome(); o['verification']['verdict'] = 'UNVERIFIED'
        r = build_acceptance_report(o)
        self.assertEqual(r['summary']['overall_verdict'], 'UNVERIFIED')
        self.assertEqual(r['verification']['results'][1]['result']['verdict'], 'FAIL')

    def test_detached_deterministic_no_calls(self):
        o = outcome(); before = deepcopy(o)
        with patch('agentguard.verifier.verify_observation', side_effect=AssertionError), \
             patch('agentguard.reviewed_workflow.resume_reviewed', side_effect=AssertionError), \
             patch('agentguard.providers.openai_provider.OpenAIProvider', side_effect=AssertionError):
            a = build_acceptance_report(o, task_text='Original task')
            b = build_acceptance_report(o, task_text='Original task')
        self.assertEqual(report_json(a), report_json(b)); self.assertEqual(o, before)
        self.assertNotIn('DO NOT EXPORT', report_json(a))
        a['reviews'][0]['name'] = 'Changed'
        self.assertEqual(o, before)
        self.assertEqual(b['task']['provenance'], 'caller_supplied_unbound')
        self.assertIsNone(build_acceptance_report(o)['task']['text'])

    def test_nested_composite_and_sequence_evidence(self):
        for kind in ('composite', 'http_sequence'):
            o = outcome(); s = o['grounded'][0]; envelope = o['verification']['results'][0]
            specs = [dict(action=deepcopy(s['action']), assertions=deepcopy(s['assertions']),
                          **{('label' if kind == 'composite' else 'name'): label}) for label in ('before', 'after')]
            s['action'] = dict(type=kind, **{('children' if kind == 'composite' else 'steps'): specs})
            s['assertions'] = []
            if kind == 'composite':
                del s['assertions']; s['behavior'] = o['proposal']['scenarios'][0]['behavior']
            if kind == 'http_sequence':
                envelope['execution'] = dict(kind=kind, steps=[dict(name=n, established=True) for n in ('before', 'after')], stopped_on_nonpass=False)
            result = envelope['result']; result['assertions'] = []
            if kind == 'http_sequence':
                s['assertions'] = [dict(type='json_equal', left=dict(observation='after', path='label'), right=dict(observation='before', path='label'))]
                result['assertions'] = [dict(type='json_equal', left=s['assertions'][0]['left'], right=s['assertions'][0]['right'], expected='x', observed='x', verdict='PASS', reason=None)]
            result['children'] = [dict(label=label, observation={'secret': 'HIDDEN'}, execution={'established': True},
                                      result=dict(name=label, source='explicit', verdict='PASS', assertions=[], reason=None)) for label in ('before', 'after')]
            r = build_acceptance_report(o)
            projected = r['verification']['results'][0]['result']
            self.assertEqual([c['label'] for c in projected['children']], ['before', 'after'])
            self.assertEqual(projected['assertions'], result['assertions'])
            self.assertNotIn('HIDDEN', report_json(r))
            o['verification']['results'][0]['result']['children'].reverse()
            with self.assertRaisesRegex(ValueError, 'child identity'): build_acceptance_report(o)

    def test_inconsistent_joins_fail_closed(self):
        changes = [lambda o: o.update(revision='wrong'),
                   lambda o: o['grounded'].reverse(),
                   lambda o: o['verification']['results'].reverse(),
                   lambda o: o['verification']['results'].pop(),
                   lambda o: o['contract']['reviews'][2].update(included=True),
                   lambda o: o['verification']['results'][0]['result'].update(source='inferred')]
        for change in changes:
            o = outcome(); change(o)
            with self.assertRaises(ValueError): build_acceptance_report(o)

    def test_registered_evidence_and_empty_contract(self):
        o = outcome()
        o['grounded'][0]['action'] = dict(type='registered_check', check_id='check.v1')
        del o['grounded'][0]['assertions']
        result = o['verification']['results'][0]['result']
        result.update(assertions=[], check_id='check.v1', coverage_id='coverage.v1',
                      coverage_authorized=True, execution_status='success', tests_run=1,
                      failures=0, errors=0, skips=0, expected_failures=0, unexpected_successes=0)
        self.assertEqual(build_acceptance_report(o)['verification']['results'][0]['result'], result)
        plan = dict(explicit_requirements=['Unlinked requirement'], inferred_behaviors=[], ambiguities=[], scenarios=[])
        proposal = create_proposal(plan)
        empty = dict(revision=proposal.revision, proposal=plan, contract=build_contract(proposal),
                     grounded=[], verification=dict(verdict='UNVERIFIED', results=[]))
        r = build_acceptance_report(empty)
        self.assertEqual(r['summary']['overall_verdict'], 'UNVERIFIED')
        self.assertEqual(r['summary']['verdict_counts'], dict(PASS=0, FAIL=0, UNVERIFIED=0))

    def test_formatter_escapes_controls_and_retains_boundaries(self):
        r = build_acceptance_report(outcome(), task_text='Task\x1b[31m')
        text = format_acceptance_report(r)
        self.assertNotIn('\x1b', text)
        for word in ('ACCEPTANCE CONTRACT', 'DISMISSED', 'PENDING', 'AMBIGUITIES', 'VERIFICATION BOUNDARY', 'expected', 'observed'):
            self.assertIn(word, text)

    def test_serialization_bound_and_nonfinite(self):
        for value in ({'x': 'a' * 1_048_576}, {'x': float('nan')}):
            with self.assertRaises(ValueError): report_json(value)

    def test_cli_report_write_and_overwrite_preflight(self):
        from agentguard.reviewed_workflow import prepare_review
        o = outcome()
        artifact = prepare_review('Task', 'Context', reasoning_provider=lambda _: o['proposal'])
        decisions = [dict(revision=o['revision'], scenario_id=r['scenario_id'], state=r['review_state'])
                     for r in o['contract']['reviews'] if r['source'] == 'inferred']
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value in [('review', artifact), ('decisions', decisions)]:
                (root/name).write_text(json.dumps(value))
            (root/'context').write_text('Context')
            args = ['verify-reviewed', '--review', str(root/'review'), '--decisions', str(root/'decisions'),
                    '--context', str(root/'context'), '--report-json', str(root/'report.json')]
            with patch.object(cli, 'OpenAIProvider') as provider, patch.object(cli, 'resume_reviewed', return_value=o) as resume, \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main(args), 1)
                saved = (root/'report.json').read_bytes()
                self.assertEqual(json.loads(saved)['schema'], 'agentguard.acceptance-report.v1')
                provider.assert_called_once(); resume.assert_called_once()
                provider.reset_mock(); resume.reset_mock()
                self.assertEqual(cli.main(args), 3)
                provider.assert_not_called(); resume.assert_not_called()
                self.assertEqual((root/'report.json').read_bytes(), saved)
