from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agentguard import execution, tools
from agentguard.recorder import JSONLRecorder
from agentguard.verifier import verify_observation


def scenario(command=None):
    return {"name": "Sample tests", "source": "explicit", "reason": "Run existing tests",
            "action": {"type": "test_command", "command": command if command is not None else
                       ["python3", "-m", "unittest", "discover", "-s", "sample_app/tests", "-v"]}}


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.sample = self.root / "sample_app"
        (self.sample / "tests").mkdir(parents=True)
        (self.sample / "__init__.py").write_text("")
        self.test = self.sample / "tests/test_example.py"
        self.test.write_text('import unittest\nclass Example(unittest.TestCase):\n    def test_ok(self): self.assertTrue(True)\n')
        self.enterContext(patch('agentguard.execution._REPO_ROOT', self.root))
        self.recorder = JSONLRecorder(self.root / "events.jsonl")

    def run_scenario(self, s=None):
        return execution.execute_test_scenario(s or scenario(), recorder=self.recorder)

    def rejected(self, command):
        with patch('agentguard.execution.tools.run_tests') as run:
            result = self.run_scenario(scenario(command))
        run.assert_not_called()
        self.assertEqual(result['result']['verdict'], 'UNVERIFIED')
        self.assertFalse(result['execution']['established'])
        self.assertIsNone(result['observation'])

    def test_real_pass_delegates_verdict_and_records(self):
        with patch('agentguard.execution.verify_observation', wraps=verify_observation) as verify:
            r = self.run_scenario()
        self.assertTrue(r['execution']['established'])
        self.assertEqual(r['result']['verdict'], 'PASS')
        self.assertEqual(verify.call_args.args[1], {'type': 'test_result', 'returncode': 0})
        self.assertTrue(self.recorder.path.exists())

    def test_real_failure_delegates_verdict(self):
        self.test.write_text(self.test.read_text().replace('assertTrue(True)', 'assertTrue(False)'))
        with patch('agentguard.execution.verify_observation', wraps=verify_observation) as verify:
            r = self.run_scenario()
        self.assertTrue(r['execution']['established'])
        self.assertEqual(r['result']['verdict'], 'FAIL')
        self.assertEqual(verify.call_args.args[1], {'type': 'test_result', 'returncode': 1})

    def test_arbitrary_executable(self):
        self.rejected(['echo', 'hello'])

    def test_shell_forms(self):
        for token in ('|', '>', '&&', ';', '$(echo x)'):
            self.rejected(list(execution._ALLOWED_COMMAND) + [token])

    def test_python_code(self):
        self.rejected(['python3', '-c', 'print(1)'])

    def test_other_modules_and_forms(self):
        for cmd in (['python3', '-m', 'pip', 'install', 'x'], ['python3', '-m', 'unittest'],
                    list(execution._ALLOWED_COMMAND) + ['-p', '*.py']):
            self.rejected(cmd)

    def test_absolute_path(self):
        cmd = list(execution._ALLOWED_COMMAND); cmd[5] = str(self.sample / 'tests')
        self.rejected(cmd)

    def test_traversal(self):
        for path in ('../tests', 'sample_app/../tests', 'sample_app/tests/../../elsewhere'):
            cmd = list(execution._ALLOWED_COMMAND); cmd[5] = path
            self.rejected(cmd)

    def test_unapproved_directory(self):
        cmd = list(execution._ALLOWED_COMMAND); cmd[5] = 'tests'
        self.rejected(cmd)

    def test_escaping_file_symlink(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'test_outside.py'; target.write_text('raise RuntimeError()')
            (self.sample / 'tests/test_escape.py').symlink_to(target)
            with patch('agentguard.execution.tools.run_tests') as run:
                r = self.run_scenario()
            run.assert_not_called()
            self.assertEqual(r['result']['verdict'], 'UNVERIFIED')

    def test_escaping_directory_symlink(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.sample / 'external').symlink_to(outside, target_is_directory=True)
            with patch('agentguard.execution.tools.run_tests') as run:
                r = self.run_scenario()
            run.assert_not_called()
            self.assertEqual(r['result']['verdict'], 'UNVERIFIED')

    def test_timeout(self):
        self.test.write_text('import time\ntime.sleep(5)\n')
        with patch('agentguard.tools._TEST_TIMEOUT_SECONDS', 0.1):
            r = self.run_scenario()
        self.assertEqual(r['result']['verdict'], 'UNVERIFIED')
        self.assertTrue(r['execution']['timed_out'])
        self.assertIsNone(r['execution']['returncode'])

    def test_launch_failure(self):
        with patch('agentguard.tools.subprocess.run', side_effect=OSError('private detail')):
            r = self.run_scenario()
        self.assertEqual(r['result']['verdict'], 'UNVERIFIED')
        self.assertNotIn('private detail', str(r))

    def test_bounded_output(self):
        self.test.write_text('print("x" * 10000)\n' + self.test.read_text())
        r = self.run_scenario()
        self.assertTrue(r['execution']['output_truncated'])
        import json
        event = json.loads(self.recorder.path.read_text())
        self.assertLessEqual(len(event['output'].encode()), 4096)
        self.assertNotIn('output', r['execution'])

    def test_malformed_or_non_test_scenario(self):
        for s in ({}, {**scenario(), 'action': {'type': 'unsupported', 'explanation': 'No route'}}):
            with self.assertRaises(ValueError): self.run_scenario(s if s else {'bad': 1})

    def test_no_mutation_fixed_cwd_no_shell_and_scope_restoration(self):
        s = scenario(); before = deepcopy(s)
        real = subprocess.run
        token = tools._ACTIVE_SAMPLE_ROOT.set(Path('/unapproved'))
        try:
            with patch('agentguard.tools.subprocess.run', wraps=real) as run:
                self.run_scenario(s)
            self.assertFalse(run.call_args.kwargs['shell'])
            self.assertEqual(run.call_args.kwargs['cwd'], self.root)
            self.assertEqual(run.call_args.args[0], [sys.executable, '-B', '-m', 'unittest', 'discover', '-s', 'sample_app/tests', '-v'])
            self.assertEqual(tools._ACTIVE_SAMPLE_ROOT.get(), Path('/unapproved'))
        finally:
            tools._ACTIVE_SAMPLE_ROOT.reset(token)
        self.assertEqual(s, before)

    def test_malformed_evidence(self):
        for event in (None, {}, {'tool': 'run_tests', 'path': 'tests', 'timed_out': False,
                                 'output_truncated': False, 'exit_code': True, 'status': 'succeeded'}):
            with patch('agentguard.execution.tools.run_tests', return_value=event):
                self.assertEqual(self.run_scenario()['result']['verdict'], 'UNVERIFIED')

    def test_recorder_failure_is_unverified_and_scope_restores(self):
        with patch.object(self.recorder, 'record', side_effect=OSError('recorder')):
            self.assertEqual(self.run_scenario()['result']['verdict'], 'UNVERIFIED')
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())
