import json
import tempfile
import unittest
from pathlib import Path

from agentguard.events import Event
from agentguard.recorder import JSONLRecorder
from agentguard.tools import read_file


class FlightRecorderTests(unittest.TestCase):
    def test_recorder_writes_json_lines(self):
        contents = read_file("profile.py")
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "events.jsonl"
            recorder = JSONLRecorder(path)
            event = Event(
                run_id="run-1",
                step_id="step-1",
                kind="tool_result",
                status="succeeded",
                summary="profile read succeeded",
                tool="read_file",
                path="profile.py",
            )

            saved = recorder.record(event)
            lines = path.read_text(encoding="utf-8").strip().splitlines()

            self.assertEqual(saved["kind"], "tool_result")
            self.assertEqual(len(lines), 1)
            self.assertEqual(json.loads(lines[0])["status"], "succeeded")
            payload = json.loads(lines[0])
            self.assertEqual(payload, saved)
            self.assertEqual(payload["tool"], "read_file")
            self.assertEqual(payload["path"], "profile.py")
            self.assertEqual(set(payload), {
                "run_id", "step_id", "kind", "status", "summary",
                "dependency_ids", "timestamp", "tool", "path",
            })
            self.assertNotIn(contents, payload.values())
            self.assertNotIn("PROFILE", lines[0])

    def test_read_file_allows_profile_in_sample_app(self):
        contents = read_file("profile.py")
        self.assertIn("PROFILE", contents)
        self.assertIn("user_name", contents)

    def test_read_file_rejects_path_outside_sample_app(self):
        with self.assertRaises(ValueError):
            read_file("../README.md")

    def test_read_file_rejects_symlink_pointing_outside_sample_app(self):
        sample_root = Path(__file__).resolve().parents[1] / "sample_app"
        with tempfile.TemporaryDirectory() as outside_dir:
            target = Path(outside_dir) / "private.txt"
            target.write_text("outside contents", encoding="utf-8")
            with tempfile.TemporaryDirectory(dir=sample_root) as inside_dir:
                link = Path(inside_dir) / "escape.txt"
                link.symlink_to(target)
                with self.assertRaisesRegex(ValueError, "outside the allowed"):
                    read_file(str(link.relative_to(sample_root)))


if __name__ == "__main__":
    unittest.main()
