"""Offline review/resume integration; no paid requests or application execution."""
from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from agentguard import cli, reviewed_workflow as workflow


def plan(sources=('explicit', 'inferred', 'explicit', 'inferred', 'inferred')):
    return dict(explicit_requirements=['Original requirement'],
                inferred_behaviors=['UNLINKED SUGGESTION MUST NOT REACH GROUNDER'],
                ambiguities=['Unresolved product decision'],
                scenarios=[dict(name=chr(65+i), behavior=f'Behavior {i}', reason=f'Rationale {i}',
                                source=source) for i, source in enumerate(sources)])


def prepare(sources=('explicit', 'inferred', 'explicit', 'inferred', 'inferred')):
    return workflow.prepare_review('Task', 'Context', reasoning_provider=Mock(return_value=plan(sources)))


def decision(a, i, state):
    return dict(revision=a['revision'], scenario_id=a['reviews'][i]['scenario_id'], state=state)


def ground(request):
    return [dict(name=s['name'], source=s['source'], reason=s['reason'],
                 action=dict(type='unsupported', explanation='No supported mechanism'))
            for s in request['planner_output']['scenarios']]


class ReviewedWorkflowTests(unittest.TestCase):
    def test_prepare_stops_at_review(self):
        provider = Mock(return_value=plan())
        with patch.object(workflow, 'ground_scenarios') as g, patch.object(workflow, 'run_acceptance') as e:
            a = workflow.prepare_review('Task', 'Context', reasoning_provider=provider)
        provider.assert_called_once(); g.assert_not_called(); e.assert_not_called()
        self.assertEqual(a['reviews'][1]['review_state'], 'PENDING')
        self.assertNotIn('verdict', json.dumps(a)); self.assertEqual(a['proposal'], plan())

    def test_explicit_only_no_decisions(self):
        a = prepare(('explicit',)); provider = Mock(side_effect=ground)
        outcome = workflow.resume_reviewed(a, [], 'Context', grounding_provider=provider)
        self.assertEqual(provider.call_args.args[0]['planner_output']['scenarios'], a['proposal']['scenarios'])
        self.assertEqual(len(outcome['verification']['results']), 1)

    def test_mixed_selection_and_no_planner_on_resume(self):
        a = prepare(); ds = [decision(a, 1, 'ACCEPTED'), decision(a, 3, 'DISMISSED'), decision(a, 4, 'ACCEPTED')]
        provider = Mock(side_effect=ground)
        with patch.object(workflow, 'plan_acceptance') as planner:
            outcome = workflow.resume_reviewed(a, ds, 'Context', grounding_provider=provider)
        planner.assert_not_called(); provider.assert_called_once()
        selected = provider.call_args.args[0]['planner_output']
        self.assertEqual([s['name'] for s in selected['scenarios']], list('ABCE'))
        self.assertEqual(selected['scenarios'][1], a['proposal']['scenarios'][1])
        self.assertEqual(selected['inferred_behaviors'], [])
        self.assertNotIn('Behavior 3', json.dumps(provider.call_args.args[0]))
        self.assertEqual(outcome['proposal'], a['proposal'])
        self.assertEqual(outcome['contract']['reviews'][3]['review_state'], 'DISMISSED')
        self.assertEqual([e['result']['name'] for e in outcome['verification']['results']], list('ABCE'))

    def test_pending_and_dismissed_have_no_verdicts(self):
        a = prepare(); provider = Mock(side_effect=ground)
        outcome = workflow.resume_reviewed(a, [decision(a, 1, 'DISMISSED')], 'Context', grounding_provider=provider)
        self.assertEqual([s['name'] for s in provider.call_args.args[0]['planner_output']['scenarios']], ['A', 'C'])
        for review in outcome['contract']['reviews']:
            self.assertNotIn('verdict', review)
        self.assertEqual(len(outcome['verification']['results']), 2)

    def test_empty_selection_uses_existing_empty_semantics(self):
        for ds_state in (None, 'DISMISSED'):
            a = prepare(('inferred',)); provider = Mock(side_effect=ground)
            ds = [] if ds_state is None else [decision(a, 0, ds_state)]
            outcome = workflow.resume_reviewed(a, ds, 'Context', grounding_provider=provider)
            self.assertEqual(provider.call_args.args[0]['planner_output']['scenarios'], [])
            self.assertEqual(outcome['verification'], dict(verdict='UNVERIFIED', results=[]))

    def test_ambiguities_preserved_not_scenarios(self):
        a = prepare(()); provider = Mock(side_effect=ground)
        out = workflow.resume_reviewed(a, [], 'Context', grounding_provider=provider)
        self.assertEqual(out['proposal']['ambiguities'], ['Unresolved product decision'])
        self.assertEqual(provider.call_args.args[0]['planner_output']['ambiguities'], a['proposal']['ambiguities'])
        self.assertEqual(out['grounded'], [])

    def test_stale_unknown_invalid_decisions_stop_before_grounding(self):
        a = prepare(); base = decision(a, 1, 'ACCEPTED')
        bad = [dict(base, revision='stale'), dict(base, scenario_id='unknown'),
               dict(base, state='PASS'), dict(base, source='explicit'), decision(a, 0, 'ACCEPTED')]
        for d in bad:
            with self.subTest(d=d), patch.object(workflow, 'ground_scenarios') as g, patch.object(workflow, 'run_acceptance') as e:
                with self.assertRaises(ValueError): workflow.resume_reviewed(a, [d], 'Context', grounding_provider=Mock())
                g.assert_not_called(); e.assert_not_called()

    def test_artifact_tampering_is_rejected(self):
        a = prepare(); variants = []
        for field, value in [('revision','stale'), ('schema','v2'), ('context_sha256','bad'), ('reviews',[])]:
            b = deepcopy(a); b[field] = value; variants.append(b)
        b = deepcopy(a); b['proposal']['scenarios'][1]['source'] = 'explicit'; variants.append(b)
        b = deepcopy(a); b['reviews'][1]['review_state'] = 'ACCEPTED'; variants.append(b)
        b = deepcopy(a); b['reviews'][0]['included'] = 1; variants.append(b)
        variants.extend([None, {}, dict(a, extra=True)])
        for b in variants:
            with patch.object(workflow, 'ground_scenarios') as g:
                with self.assertRaises(ValueError): workflow.resume_reviewed(b, [], 'Context', grounding_provider=Mock())
                g.assert_not_called()

    def test_context_validation_before_provider(self):
        for context in (None, '', ' ', 'X'*32001, 'Changed'):
            with patch.object(workflow, 'ground_scenarios') as g:
                with self.assertRaises(ValueError): workflow.resume_reviewed(prepare(), [], context, grounding_provider=Mock())
                g.assert_not_called()
        provider = Mock()
        with self.assertRaises(ValueError): workflow.prepare_review('Task', '', reasoning_provider=provider)
        provider.assert_not_called()

    def test_roundtrip_and_nonmutation(self):
        a = prepare(); restored = json.loads(json.dumps(a)); ds = [decision(a, 1, 'ACCEPTED')]
        before = deepcopy((a, ds)); provider = Mock(side_effect=ground)
        out = workflow.resume_reviewed(restored, ds, 'Context', grounding_provider=provider)
        self.assertEqual((a, ds), before)
        out['proposal']['scenarios'].clear(); out['contract']['reviews'].clear()
        self.assertEqual(a, before[0])
        self.assertEqual(a, prepare())

    def test_grounder_cannot_add_excluded_scenarios(self):
        a = prepare(); provider = Mock(return_value=ground(dict(planner_output=a['proposal'])))
        with patch.object(workflow, 'run_acceptance') as e:
            with self.assertRaises(ValueError): workflow.resume_reviewed(a, [], 'Context', grounding_provider=provider)
            e.assert_not_called()
        provider.assert_called_once()

    def test_provider_failure_no_retry_or_execution(self):
        provider = Mock(side_effect=RuntimeError('unavailable'))
        with patch.object(workflow, 'run_acceptance') as e:
            with self.assertRaises(RuntimeError): workflow.resume_reviewed(prepare(), [], 'Context', grounding_provider=provider)
            e.assert_not_called()
        provider.assert_called_once()

    def test_approval_does_not_authorize_registered_execution(self):
        a = prepare(('inferred',))
        candidate = dict(name='A', source='inferred', reason='Rationale 0',
                         action=dict(type='registered_check', check_id='example'))
        with patch('agentguard.acceptance.execute_registered_check') as execute:
            out = workflow.resume_reviewed(a, [decision(a,0,'ACCEPTED')], 'Context',
                                           grounding_provider=Mock(return_value=[candidate]))
        execute.assert_not_called()
        envelope = out['verification']['results'][0]
        self.assertFalse(envelope['execution']['coverage_authorized'])
        self.assertEqual(envelope['result']['verdict'], 'UNVERIFIED')

    def test_approval_does_not_bypass_http_policy(self):
        a = prepare(('inferred',))
        candidate = dict(name='A', source='inferred', reason='Rationale 0',
                         action=dict(type='http_request', method='GET', path='/'),
                         assertions=[dict(type='status', equals=200)])
        out = workflow.resume_reviewed(a, [decision(a,0,'ACCEPTED')], 'Context',
                                       grounding_provider=Mock(return_value=[candidate]),
                                       base_url='https://example.com')
        self.assertEqual(out['verification']['verdict'], 'UNVERIFIED')
        self.assertFalse(out['verification']['results'][0]['execution']['established'])

    def test_execution_config_is_separate_and_result_not_recomputed(self):
        a = prepare(('explicit',)); sentinel = {'verdict':'FAIL','results':[]}
        config = dict(base_url='http://127.0.0.1:1234', recorder=object(), repository_root='root',
                      registry=object(), coverage_authorizations=object())
        with patch.object(workflow, 'run_acceptance', return_value=sentinel) as executor:
            out = workflow.resume_reviewed(a, [], 'Context', grounding_provider=Mock(side_effect=ground), **config)
        executor.assert_called_once_with(out['grounded'], **config)
        self.assertIs(out['verification'], sentinel)


class ReviewedCLITests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup); self.root = Path(tmp.name)
        self.task = self.root/'task.md'; self.task.write_text('Task')
        self.context = self.root/'context.md'; self.context.write_text('Context')
        self.review = self.root/'review.json'; self.decisions = self.root/'decisions.json'

    def invoke(self, args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err): code = cli.main(args)
        return code, out.getvalue(), err.getvalue()

    def args(self):
        return ['verify-reviewed', '--review', str(self.review), '--decisions', str(self.decisions), '--context', str(self.context)]

    def save(self):
        a = prepare(); self.review.write_text(json.dumps(a)); self.decisions.write_text('[]'); return a

    def test_review_writes_artifact_and_stops(self):
        with patch.object(cli, 'OpenAIProvider', return_value=Mock(return_value=plan())) as factory, patch.object(workflow,'ground_scenarios') as g, patch.object(workflow,'run_acceptance') as e:
            code, out, err = self.invoke(['review','--task',str(self.task),'--context',str(self.context),'--output',str(self.review)])
        self.assertEqual(code,0); self.assertFalse(err); g.assert_not_called(); e.assert_not_called()
        factory.return_value.assert_called_once()
        for label in ('EXPLICIT','AGENTGUARD SUGGESTION','AMBIGUITY','PENDING','not verified evidence'): self.assertIn(label,out)
        workflow.validate_review(json.loads(self.review.read_text()), 'Context')
        self.assertNotIn('Overall:',out)

    def test_resume_selected_only_and_exit_code(self):
        a = self.save(); self.decisions.write_text(json.dumps([decision(a,1,'ACCEPTED'),decision(a,3,'DISMISSED')]))
        provider = Mock(side_effect=ground)
        with patch.object(cli,'OpenAIProvider',return_value=provider): code,out,err = self.invoke(self.args())
        self.assertEqual(code,2); self.assertFalse(err); self.assertIn('Overall: UNVERIFIED',out)
        provider.assert_called_once()
        self.assertEqual([s['name'] for s in provider.call_args.args[0]['planner_output']['scenarios']],list('ABC'))
        self.assertNotIn('[UNVERIFIED] "D"',out); self.assertIn('DISMISSED',out)

    def test_reviewed_cli_preserves_existing_pass_fail_exit_codes(self):
        from agentguard.verifier import verify_observation
        a = prepare(('explicit',)); self.review.write_text(json.dumps(a)); self.decisions.write_text('[]')
        candidate = dict(name='A', source='explicit', reason='Rationale 0',
                         action=dict(type='http_request', method='GET', path='/'),
                         assertions=[dict(type='status', equals=200)])
        for status, code, verdict in ((200,0,'PASS'),(500,1,'FAIL')):
            observation = dict(type='http_response', status=status)
            envelope = dict(execution={}, observation=observation,
                            result=verify_observation(candidate, observation))
            with patch.object(cli,'OpenAIProvider',return_value=Mock(return_value=[candidate])), patch('agentguard.acceptance.execute_http_scenario',return_value=envelope):
                actual,out,err = self.invoke(self.args()+['--base-url','http://127.0.0.1:1234'])
            self.assertEqual(actual,code); self.assertIn('Overall: '+verdict,out); self.assertFalse(err)

    def test_bad_files_fail_before_provider(self):
        self.save()
        for content in ('null', '{}', '[{"state":"ACCEPTED"}]', '[', '[NaN]', '{"a":1,"a":2}'):
            self.decisions.write_text(content)
            with patch.object(cli,'OpenAIProvider') as provider:
                code,out,err = self.invoke(self.args())
            self.assertEqual(code,3); self.assertFalse(out); self.assertIn('No acceptance verdict',err); provider.assert_not_called()

    def test_tampered_review_and_missing_context_fail(self):
        a = self.save(); a['revision'] = 'stale'; self.review.write_text(json.dumps(a))
        with patch.object(cli,'OpenAIProvider') as provider:
            self.assertEqual(self.invoke(self.args())[0],3); provider.assert_not_called()
        self.save(); self.context.unlink()
        with patch.object(cli,'OpenAIProvider') as provider:
            self.assertEqual(self.invoke(self.args())[0],3); provider.assert_not_called()

    def test_review_refuses_overwrite_before_paid_call(self):
        self.review.write_text('preserve')
        with patch.object(cli,'OpenAIProvider') as provider:
            result = self.invoke(['review','--task',str(self.task),'--context',str(self.context),'--output',str(self.review)])
        self.assertEqual(result[0],3); provider.assert_not_called(); self.assertEqual(self.review.read_text(),'preserve')

    def test_artifact_read_bounds(self):
        self.review.write_text(' '* (workflow.MAX_ARTIFACT_CHARS+1))
        with self.assertRaises(ValueError): cli._read_json(self.review)


if __name__ == '__main__': unittest.main()
