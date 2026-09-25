import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from agentguard.tools import run_tests


class RunTestsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        source = Path(__file__).resolve().parents[1] / 'sample_app'
        self.root = self.tmp / 'sample_app'
        shutil.copytree(source, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.log = self.tmp / 'events.jsonl'
        self.enterContext(patch('agentguard.tools._SAMPLE_APP_ROOT', self.root))
        self.enterContext(patch('agentguard.tools._DEFAULT_EVENT_PATH', self.log))

    def check_saved(self, event):
        self.assertEqual(json.loads(self.log.read_text()), event)
        self.assertEqual(event['tool'], 'run_tests')
        self.assertEqual(event['path'], 'tests')

    def test_clean_copy_passes(self):
        event = run_tests(run_id='test-run', step_id='test-step')
        self.check_saved(event)
        self.assertEqual(event['exit_code'], 0)
        self.assertEqual(event['status'], 'succeeded')
        self.assertIn('Ran 2 tests', event['output'])
        self.assertIn('OK', event['output'])
        self.assertFalse(event['timed_out'])

    def test_wrong_username_copy_fails(self):
        profile = self.root / 'profile.py'
        profile.write_text(profile.read_text().replace(
            'return profile["user_name"]', 'return profile["username"]'))
        event = run_tests()
        self.check_saved(event)
        self.assertEqual(event['exit_code'], 1)
        self.assertEqual(event['status'], 'failed')
        self.assertIn("KeyError: 'username'", event['output'])
        self.assertFalse(event['timed_out'])

    def test_timeout_is_recorded(self):
        (self.root / 'tests' / 'test_slow.py').write_text(
            'import time\ntime.sleep(30)\n')
        with patch('agentguard.tools._TEST_TIMEOUT_SECONDS', 0.2):
            event = run_tests()
        self.check_saved(event)
        self.assertTrue(event['timed_out'])
        self.assertEqual(event['status'], 'failed')
        self.assertIsNone(event['exit_code'])

    def test_output_is_bounded(self):
        (self.root / 'tests' / 'test_loud.py').write_text(
            'print("x" * 10000, flush=True)\n')
        event = run_tests()
        self.check_saved(event)
        self.assertEqual(event['exit_code'], 0)
        self.assertTrue(event['output_truncated'])
        self.assertLessEqual(len(event['output']), 4096)

    def test_arbitrary_command_not_accepted(self):
        with self.assertRaises(TypeError):
            run_tests(command='echo unexpected')
        self.assertFalse(self.log.exists())

    def test_launch_failure_is_recorded(self):
        with patch('agentguard.tools.subprocess.run', side_effect=OSError):
            event = run_tests()
        self.check_saved(event)
        self.assertEqual(event['status'], 'failed')
        self.assertIsNone(event['exit_code'])
        self.assertFalse(event['timed_out'])


if __name__ == '__main__':
    unittest.main()
