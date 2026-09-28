"""Offline CLI composition and presentation tests, no OpenAI requests."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from agentguard import cli
from agentguard.acceptance import run_acceptance
from agentguard.verifier import verify_observation
from agentguard.providers.openai_provider import OpenAIProviderError


def plan():
    return dict(explicit_requirements=['Requirement'], inferred_behaviors=['Inference'],
                ambiguities=['Decision'], scenarios=[dict(name='Example',source='explicit',
                reason='Task',behavior='Observe status')])


def scenario():
    return dict(name='Example',source='explicit',reason='Task',
                action=dict(type='http_request',method='GET',path='/example'),
                assertions=[dict(type='status',equals=200)])


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.task=Path(self.tmp.name)/'task.md';self.task.write_text('Task',encoding='utf-8')
        self.context=Path(self.tmp.name)/'context.md';self.context.write_text('Context',encoding='utf-8')
        self.args=['verify','--task',str(self.task),'--context',str(self.context)]
        self.provider=Mock(side_effect=[plan(),[scenario()]])
        self.factory=patch.object(cli,'OpenAIProvider',return_value=self.provider).start()
        self.addCleanup(patch.stopall)
        self.execution=patch.object(cli,'run_acceptance',wraps=run_acceptance).start()

    def invoke(self,extra=()):
        stdout,stderr=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr):
            code=cli.main(self.args+list(extra))
        return code,stdout.getvalue(),stderr.getvalue()

    def test_help_and_argument_error(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            with self.assertRaises(SystemExit) as caught:cli.main(['--help'])
        self.assertEqual(caught.exception.code,0);self.assertIn('verify',out.getvalue())
        self.args=['verify'];self.assertEqual(self.invoke()[0],3)
        self.factory.assert_not_called()

    def test_pass_fail_unverified_and_composition(self):
        for observed,expected_code,verdict in ((200,0,'PASS'),(500,1,'FAIL'),(None,2,'UNVERIFIED')):
            with self.subTest(verdict=verdict):
                self.provider.reset_mock(side_effect=True);self.provider.side_effect=[plan(),[scenario()]]
                self.factory.reset_mock();self.execution.reset_mock()
                observation=None if observed is None else dict(type='http_response',status=observed)
                envelope=dict(execution={},observation=observation,result=verify_observation(scenario(),observation))
                with patch('agentguard.acceptance.execute_http_scenario',return_value=envelope) as http:
                    code,out,err=self.invoke(['--base-url','http://127.0.0.1:1234'])
                self.assertEqual(code,expected_code);self.assertIn('Overall: '+verdict,out);self.assertFalse(err)
                self.assertIn('expected=200',out)
                if observed:self.assertIn('observed='+str(observed),out)
                self.factory.assert_called_once();self.assertEqual(self.provider.call_count,2)
                first,second=[c.args[0] for c in self.provider.call_args_list]
                self.assertEqual(first['task_text'],'Task');self.assertEqual(first['repository_context'],'Context')
                self.assertEqual(second['planner_output'],plan());self.assertEqual(second['repository_context'],'Context')
                self.execution.assert_called_once_with([scenario()],base_url='http://127.0.0.1:1234')
                http.assert_called_once()

    def test_mixed_aggregation_is_core_owned(self):
        p=plan();p['scenarios'].append(dict(p['scenarios'][0],name='Unavailable'))
        unsupported=dict(name='Unavailable',source='explicit',reason='Task',action=dict(type='unsupported',explanation='No evidence'))
        self.provider.side_effect=[p,[scenario(),unsupported]]
        obs=dict(type='http_response',status=400)
        with patch('agentguard.acceptance.execute_http_scenario',return_value=dict(execution={},observation=obs,result=verify_observation(scenario(),obs))):
            code,out,_=self.invoke(['--base-url','http://127.0.0.1:1234'])
        self.assertEqual(code,1);self.assertIn('[UNVERIFIED]',out);self.assertIn('Overall: FAIL',out)

    def test_show_reasoning_and_missing_target(self):
        code,out,_=self.invoke(['--show-reasoning'])
        self.assertEqual(code,2)
        for value in ('Requirement','Inference','Decision','http_request','HTTP target configuration is unavailable'):self.assertIn(value,out)

    def test_default_hides_reasoning(self):
        _,out,_=self.invoke()
        self.assertNotIn('Explicit requirements:',out);self.assertNotIn('Inference',out)

    def test_missing_files(self):
        for flag in ('--task','--context'):
            old=self.args[:];self.args[self.args.index(flag)+1]=str(Path(self.tmp.name)/'absent')
            self.assertEqual(self.invoke()[0],3);self.args=old
        self.factory.assert_not_called();self.execution.assert_not_called()

    def test_empty_invalid_utf8_oversized_and_unreadable_inputs(self):
        for path in (self.task,self.context):
            original=path.read_bytes()
            for value in (b'',b' \n',b'\xff',b'a'*32001):
                path.write_bytes(value);self.assertEqual(self.invoke()[0],3)
            path.write_bytes(original)
        with patch.object(Path,'open',side_effect=PermissionError('secret')):
            code,_,err=self.invoke();self.assertEqual(code,3);self.assertNotIn('secret',err)
        self.factory.assert_not_called()

    def test_configuration_failure(self):
        self.factory.side_effect=OpenAIProviderError('secret-key')
        code,_,err=self.invoke();self.assertEqual(code,3);self.assertIn('configuration',err)
        self.assertNotIn('secret-key',err);self.execution.assert_not_called()

    def test_provider_failure_stops_without_retry(self):
        self.provider.side_effect=OpenAIProviderError('secret')
        code,_,err=self.invoke();self.assertEqual(code,3);self.assertIn('planning',err)
        self.assertNotIn('secret',err);self.provider.assert_called_once();self.execution.assert_not_called()

    def test_planner_validation_failure_stops_execution(self):
        self.provider.side_effect=[{'verdict':'PASS'}]
        self.assertEqual(self.invoke()[0],3);self.provider.assert_called_once();self.execution.assert_not_called()

    def test_grounding_failure_stops_execution(self):
        for second in ([dict(scenario(),verdict='PASS')],OpenAIProviderError('secret')):
            self.provider.reset_mock(side_effect=True);self.provider.side_effect=[plan(),second]
            code,_,err=self.invoke();self.assertEqual(code,3);self.assertIn('grounding',err)
            self.assertEqual(self.provider.call_count,2);self.execution.assert_not_called()

    def test_runtime_error_not_verdict(self):
        self.execution.side_effect=RuntimeError('secret')
        code,out,err=self.invoke();self.assertEqual(code,3);self.assertEqual(out,'')
        self.assertNotIn('secret',err);self.assertIn('acceptance execution',err)

    def test_formatter_preserves_null_missing_types_and_children(self):
        leaf=dict(execution={},result=dict(name='escape\x1b',verdict='FAIL',reason=None,assertions=[
            dict(type='json_field',path='x',expected=False,observed=None,verdict='FAIL',reason=None),
            dict(type='json_type',path='y',expected='string',observed_type='object',verdict='FAIL',reason=None),
            dict(type='json_field',path='z',expected='long',expected_truncated=True,verdict='UNVERIFIED',reason='Missing')]))
        parent=dict(execution={},result=dict(name='Parent',verdict='FAIL',reason='Task',assertions=[],children=[leaf]))
        result=dict(verdict='FAIL',results=[parent]);before=json.dumps(result)
        text=cli.format_report('task',plan(),[scenario()],result)
        self.assertIn('observed=null',text);self.assertIn('observed_type="object"',text)
        self.assertIn('expected_truncated=true',text);self.assertNotIn('\x1b',text)
        self.assertEqual(json.dumps(result),before)

    def test_bounded_unicode_read(self):
        self.task.write_text('é'*32000,encoding='utf-8')
        self.assertEqual(len(cli._read_text(self.task)),32000)
        self.task.write_text('é'*32001,encoding='utf-8')
        with self.assertRaises(ValueError):cli._read_text(self.task)

if __name__=='__main__':unittest.main()
