import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentguard.recorder import JSONLRecorder
from agentguard.tools import read_file


class FlightRecorderTests(unittest.TestCase):
    def setUp(self):
        tmpdir = self.enterContext(tempfile.TemporaryDirectory())
        self.event_path = Path(tmpdir) / "events.jsonl"
        self.recorder = JSONLRecorder(self.event_path)
        self.enterContext(patch("agentguard.tools._DEFAULT_EVENT_PATH", self.event_path))

    def events(self):
        return [json.loads(line) for line in self.event_path.read_text().splitlines()]

    def test_read_records_success_and_rejection(self):
        contents = read_file("profile.py", recorder=self.recorder,
                             run_id="run-1", step_id="step-1")
        with self.assertRaises(ValueError):
            read_file("../README.md", recorder=self.recorder,
                      run_id="run-1", step_id="step-2")
        events = self.events()
        self.assertEqual(len(events), 2)
        self.assertEqual([e["status"] for e in events], ["succeeded", "blocked"])
        self.assertEqual([e["path"] for e in events], ["profile.py", "../README.md"])
        self.assertEqual([e["step_id"] for e in events], ["step-1", "step-2"])
        for event in events:
            self.assertEqual(event["tool"], "read_file")
            self.assertEqual(event["run_id"], "run-1")
            self.assertEqual(event["kind"], "tool_result")
            self.assertTrue(event["timestamp"])
            self.assertEqual(set(event), {
                "run_id", "step_id", "kind", "status", "summary",
                "dependency_ids", "timestamp", "tool", "path",
                "before_hash", "after_hash",
                "exit_code", "output", "output_truncated", "timed_out", "decisions",
            })
            self.assertNotIn(contents, event.values())
        self.assertNotIn("PROFILE", self.event_path.read_text())

    def test_read_file_allows_profile_and_records_by_default(self):
        contents = read_file("profile.py")
        self.assertIn("PROFILE", contents)
        self.assertIn("user_name", contents)
        event, = self.events()
        self.assertEqual(event["status"], "succeeded")
        self.assertTrue(event["run_id"])
        self.assertTrue(event["step_id"])

    def test_read_file_rejects_symlink_pointing_outside_sample_app(self):
        sample_root = Path(__file__).resolve().parents[1] / "sample_app"
        with tempfile.TemporaryDirectory() as outside_dir:
            target = Path(outside_dir) / "private.txt"
            target.write_text("outside contents", encoding="utf-8")
            with tempfile.TemporaryDirectory(dir=sample_root) as inside_dir:
                link = Path(inside_dir) / "escape.txt"
                link.symlink_to(target)
                relative_path = str(link.relative_to(sample_root))
                with self.assertRaisesRegex(ValueError, "outside the allowed"):
                    read_file(relative_path)
                event, = self.events()
                self.assertEqual(event["status"], "blocked")
                self.assertEqual(event["path"], relative_path)
                self.assertEqual(event["tool"], "read_file")
                self.assertNotIn("outside contents", self.event_path.read_text())

    def test_missing_file_records_failure(self):
        with self.assertRaises(FileNotFoundError):
            read_file("missing-file.txt")
        event, = self.events()
        self.assertEqual(event["status"], "failed")
        self.assertEqual(event["path"], "missing-file.txt")

    def test_absolute_path_is_recorded_relative_to_sample_app(self):
        path = Path(__file__).resolve().parents[1] / "sample_app" / "profile.py"
        read_file(str(path))
        event, = self.events()
        self.assertEqual(event["path"], "profile.py")


if __name__ == "__main__":
    unittest.main()
