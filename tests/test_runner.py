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
        self.assertEqual(len(events), 4)
        self.assertEqual(events[-1]["kind"], "run_result")
        self.assertEqual(events[-1]["status"], "failed")
        self.assertEqual(events[-1]["dependency_ids"], ["step-3"])
        events = events[:3]
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
                events = run_script(log_path=log)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[-1]["status"], "failed")
            self.assertEqual(events[-1]["summary"], "tool call limit reached")
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())

    def test_temporary_copy_is_removed_and_scope_restored_on_error(self):
        with self.assertRaisesRegex(RuntimeError, 'stop'):
            with tools.temporary_sample_app() as root:
                self.assertNotEqual(root, tools._SAMPLE_APP_ROOT)
                raise RuntimeError('stop')
        self.assertFalse(root.exists())
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())

    def test_success_and_failure_cli_have_separate_linked_runs(self):
        import contextlib
        import io
        from agentguard.runner import main

        source = tools._SAMPLE_APP_ROOT / 'profile.py'
        before = source.read_bytes()
        run_ids = []
        real_write = tools.write_file
        edits = []

        def capture_write(path, contents, **kwargs):
            edits.append(contents)
            return real_write(path, contents, **kwargs)

        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / 'events.jsonl'
            with patch('agentguard.tools._DEFAULT_EVENT_PATH', log):
                with patch('agentguard.tools.write_file', side_effect=capture_write):
                    for scenario, exit_code in [('success', 0), ('failure', 1)]:
                        output = io.StringIO()
                        with contextlib.redirect_stdout(output):
                            main([scenario])
                        events = [json.loads(line) for line in output.getvalue().splitlines()[:4]]
                        final = events.pop()
                        self.assertEqual(final["status"], "completed" if exit_code == 0 else "failed")
                        self.assertEqual([d.split(":")[0] for d in final["decisions"]],
                                         ["read_file", "write_file", "run_tests", final["status"]])
                        self.assertEqual(len({e['run_id'] for e in events}), 1)
                        run_ids.append(events[0]['run_id'])
                        self.assertEqual([e['step_id'] for e in events], ['step-1', 'step-2', 'step-3'])
                        self.assertEqual([e['dependency_ids'] for e in events], [[], ['step-1'], ['step-2']])
                        self.assertNotEqual(events[1]['before_hash'], events[1]['after_hash'])
                        self.assertEqual(events[-1]['exit_code'], exit_code)
                        self.assertEqual(events[-1]['status'], 'succeeded' if exit_code == 0 else 'failed')
                        self.assertIn('OK' if exit_code == 0 else "KeyError: 'username'", events[-1]['output'])
            self.assertEqual(len(log.read_text().splitlines()), 8)
        self.assertNotEqual(*run_ids)
        self.assertIn('return profile["user_name"]  # Use the profile schema key.', edits[0])
        self.assertEqual(source.read_bytes(), before)
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())

    def test_unknown_scenario_rejected_before_tools(self):
        with patch('agentguard.runner.tools.temporary_sample_app') as temporary:
            with self.assertRaises(ValueError):
                run_script(scenario='unknown')
            temporary.assert_not_called()

    def test_failed_read_stops_without_edit_or_tests(self):
        from agentguard.events import Event

        def fail_read(path, **kwargs):
            kwargs['recorder'].record(Event(
                run_id=kwargs['run_id'], step_id=kwargs['step_id'],
                kind='tool_result', status='failed', summary='read failed',
                tool='read_file', path=path,
            ))
            raise OSError('read failed')

        with tempfile.TemporaryDirectory() as directory:
            with patch('agentguard.runner.tools.read_file', side_effect=fail_read):
                with patch('agentguard.runner.tools.write_file') as write:
                    with patch('agentguard.runner.tools.run_tests') as test:
                        events = run_script(log_path=Path(directory) / 'events.jsonl')
            write.assert_not_called()
            test.assert_not_called()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[-1]['status'], 'failed')
        self.assertEqual(events[-1]['dependency_ids'], ['step-1'])
        self.assertIsNone(tools._ACTIVE_SAMPLE_ROOT.get())
