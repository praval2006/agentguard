import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agentguard import tools
from agentguard.runner import run_script


class RunnerTests(unittest.TestCase):
    def test_three_linked_steps_fail_only_in_copy(self):
        source = tools._SAMPLE_APP_ROOT / 'profile.py'
        before = source.read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'events.jsonl'
            events = run_script(log_path=log)
            self.assertEqual(events, [json.loads(line) for line in log.read_text().splitlines()])
        self.assertEqual(source.read_bytes(), before)
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())
        self.assertEqual(len(events), 3)
        self.assertEqual(len({e['run_id'] for e in events}), 1)
        self.assertEqual([e['step_id'] for e in events], ['step-1', 'step-2', 'step-3'])
        self.assertEqual([e['dependency_ids'] for e in events], [[], ['step-1'], ['step-2']])
        self.assertEqual([e['tool'] for e in events], ['read_file', 'write_file', 'run_tests'])
        self.assertEqual([e['status'] for e in events], ['succeeded', 'succeeded', 'failed'])
        self.assertEqual(events[-1]['exit_code'], 1)
        self.assertIn("KeyError: 'username'", events[-1]['output'])
        self.assertNotEqual(events[1]['before_hash'], events[1]['after_hash'])

    def test_step_limit_stops_before_next_tool(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'events.jsonl'
            with patch('agentguard.runner.MAX_STEPS', 1):
                with self.assertRaisesRegex(RuntimeError, 'step limit'):
                    run_script(log_path=log)
            self.assertEqual(len(log.read_text().splitlines()), 1)
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())

    def test_temporary_copy_is_removed_and_scope_restored_on_error(self):
        with self.assertRaisesRegex(RuntimeError, 'stop'):
            with tools.temporary_sample_app() as root:
                self.assertNotEqual(root, tools._SAMPLE_APP_ROOT)
                raise RuntimeError('stop')
        self.assertFalse(root.exists())
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())
