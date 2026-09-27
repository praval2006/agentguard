import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from agentguard.check_registry import parse_registry
from agentguard import registered_execution as execution


class RegisteredExecutionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.cwd = self.root / 'service'
        self.cwd.mkdir()
        self.file = self.cwd / 'test_local.py'
        self.file.write_text('import unittest\nclass Check(unittest.TestCase):\n    def test_one(self): self.assertTrue(True)\n')
        self.registry = parse_registry(json.dumps({'version':1,'checks':[{
            'id':'local.one','runner':'unittest','cwd':'service',
            'target':'test_local.Check.test_one',
            'coverage':{'id':'behavior.v1','description':'Metadata, not coverage proof'}}]}), repository_root=self.root)
        self.scenario = {'name':'Local check','source':'explicit','reason':'Requirement',
                         'action':{'type':'registered_check','check_id':'local.one'}}

    def run_check(self):
        return execution.execute_registered_check(self.scenario, repository_root=self.root, registry=self.registry)

    def body(self, body, decorator=''):
        self.file.write_text('import unittest, os\nclass Check(unittest.TestCase):\n' +
            (f'    {decorator}\n' if decorator else '') + '    def test_one(self):\n        ' + body + '\n')

    def test_success_and_process_contract(self):
        self.body(f'self.assertEqual(os.getcwd(), {str(self.cwd)!r})')
        with patch.object(execution.subprocess, 'Popen', wraps=subprocess.Popen) as start:
            result = self.run_check()
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['tests_run'], 1)
        self.assertEqual(result['coverage_id'], 'behavior.v1')
        self.assertEqual(result['target'], 'test_local.Check.test_one')
        self.assertNotIn('verdict', result)
        self.assertFalse(start.call_args.kwargs['shell'])
        self.assertEqual(start.call_args.kwargs['stdin'], subprocess.DEVNULL)
        self.assertEqual(start.call_args.args[0][1:3], ['-I','-B'])
        self.assertNotIn('env', start.call_args.kwargs)

    def test_assertion_failure(self):
        self.body('self.assertEqual(1, 2)')
        r=self.run_check()
        self.assertEqual((r['status'],r['failures'],r['errors']), ('assertion_failure',1,0))

    def test_runtime_error(self):
        self.body('raise RuntimeError("private")')
        r=self.run_check()
        self.assertEqual((r['status'],r['errors']), ('test_error',1))
        self.assertNotIn('private', str(r))

    def test_setup_error(self):
        self.file.write_text('import unittest\nclass Check(unittest.TestCase):\n    def setUp(self): raise RuntimeError()\n    def test_one(self): pass\n')
        self.assertEqual(self.run_check()['status'],'test_error')

    def test_load_error(self):
        self.file.write_text('raise ImportError("missing dependency")\n')
        self.assertEqual(self.run_check()['status'],'load_error')

    def test_skip(self):
        self.body('pass', '@unittest.skip("skip")')
        self.assertEqual(self.run_check()['status'],'skipped')

    def test_expected_failure(self):
        self.body('self.fail()', '@unittest.expectedFailure')
        self.assertEqual(self.run_check()['status'],'expected_failure')

    def test_unexpected_success(self):
        self.body('pass', '@unittest.expectedFailure')
        self.assertEqual(self.run_check()['status'],'unexpected_success')

    def test_cardinality(self):
        for count, status in ((0,'zero_tests'),(2,'multiple_tests')):
            self.file.write_text(f'import unittest\nclass Check(unittest.TestCase):\n    def countTestCases(self): return {count}\n    def test_one(self): raise AssertionError("must not run")\n')
            self.assertEqual(self.run_check()['status'], status)

    def test_timeout(self):
        self.body('import time; time.sleep(10)')
        with patch.object(execution,'TIMEOUT_SECONDS',0.1): r=self.run_check()
        self.assertEqual(r['status'],'timeout')
        self.assertTrue(r['timed_out'])
        self.assertIsNone(r['returncode'])

    def test_crash(self):
        self.body('os._exit(7)')
        r=self.run_check()
        self.assertEqual((r['status'],r['returncode']),('process_crash',7))

    def test_missing_result(self):
        self.body('os._exit(0)')
        self.assertEqual(self.run_check()['status'],'malformed_result')

    def test_result_channel_bounds_and_schema(self):
        for payload in (b'{}', b'x'*2049, b'{"status":"success","status":"success"}'):
            self.body(f'import sys; os.write(int(sys.argv[-1]), {payload!r}); os._exit(0)')
            self.assertEqual(self.run_check()['status'],'malformed_result')

    def test_stdout_cannot_spoof_result(self):
        self.body('print(\'{"status":"success"}\'); self.fail()')
        self.assertEqual(self.run_check()['status'],'assertion_failure')

    def test_output_bound(self):
        self.body('print("x"*100000)')
        r=self.run_check()
        self.assertTrue(r['output_truncated'])
        self.assertLess(len(json.dumps(r)), 1000)

    def test_launch_failure(self):
        with patch.object(execution.subprocess,'Popen',side_effect=OSError('private')):
            self.assertEqual(self.run_check()['status'],'execution_error')

    def test_unknown_and_invalid_registry(self):
        self.scenario['action']['check_id']='unknown'
        with patch.object(execution.subprocess,'Popen') as start:
            self.assertEqual(self.run_check()['status'],'unknown_check')
            self.registry = None
            self.assertEqual(self.run_check()['status'],'configuration_error')
            start.assert_not_called()

    def test_injection_rejected(self):
        for key in ('argv','cwd','executable','environment','target','timeout','runner'):
            self.scenario['action'][key]='injected'
            with self.assertRaises(ValueError): self.run_check()
            del self.scenario['action'][key]

    def test_wrong_action(self):
        self.scenario['action']={'type':'unsupported','explanation':'No mechanism'}
        with self.assertRaises(ValueError): self.run_check()

    def test_symlink_revalidation(self):
        self.file.unlink()
        self.file.symlink_to(Path('/tmp/outside.py'))
        with patch.object(execution.subprocess,'Popen') as start:
            self.assertEqual(self.run_check()['status'],'configuration_error')
            start.assert_not_called()

    def test_missing_cwd(self):
        self.file.unlink(); self.cwd.rmdir()
        self.assertEqual(self.run_check()['status'],'configuration_error')

    def test_changed_cwd_symlink(self):
        self.file.unlink(); self.cwd.rmdir(); self.cwd.symlink_to(self.root, target_is_directory=True)
        self.assertEqual(self.run_check()['status'],'configuration_error')

    def test_root_mismatch(self):
        r=execution.execute_registered_check(self.scenario, repository_root=self.cwd, registry=self.registry)
        self.assertEqual(r['status'],'configuration_error')

    def test_result_validation(self):
        valid=dict(status='success',tests_run=1,failures=0,errors=0,skips=0,expected_failures=0,unexpected_successes=0)
        for patch_value in ({'tests_run':True},{'extra':1},{'status':'PASS'},{'errors':1},{'tests_run':0}):
            with self.assertRaises(ValueError): execution._validate_result({**valid,**patch_value})
