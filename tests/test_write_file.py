import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from agentguard.tools import write_file


class WriteFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        source = Path(__file__).resolve().parents[1] / "sample_app"
        self.root = self.tmp / "sample_app"
        shutil.copytree(source, self.root, ignore=shutil.ignore_patterns('__pycache__'))
        self.log = self.tmp / "events.jsonl"
        self.enterContext(patch('agentguard.tools._SAMPLE_APP_ROOT', self.root))
        self.enterContext(patch('agentguard.tools._DEFAULT_EVENT_PATH', self.log))

    def event(self):
        event, = [json.loads(line) for line in self.log.read_text().splitlines()]
        self.assertEqual(event['tool'], 'write_file')
        return event

    def test_wrong_username_edit_in_temporary_copy(self):
        profile = self.root / 'profile.py'
        before = profile.read_bytes()
        after = before.replace(b'return profile["user_name"]', b'return profile["username"]')
        write_file('profile.py', after.decode(), run_id='write-demo', step_id='step-1')
        self.assertEqual(profile.read_bytes(), after)
        event = self.event()
        self.assertEqual(event['status'], 'succeeded')
        self.assertEqual(event['path'], 'profile.py')
        self.assertEqual(event['before_hash'], hashlib.sha256(before).hexdigest())
        self.assertEqual(event['after_hash'], hashlib.sha256(after).hexdigest())
        self.assertNotIn(before.decode(), event.values())
        self.assertNotIn(after.decode(), event.values())
        self.assertNotIn('username', self.log.read_text())
        result = subprocess.run(
            [sys.executable, '-m', 'unittest', 'discover', '-s', 'sample_app/tests', '-v'],
            cwd=self.tmp, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("KeyError: 'username'", result.stderr)

    def test_rejects_outside_and_preserves_target(self):
        target = self.tmp / 'outside.txt'
        target.write_text('private')
        with self.assertRaises(ValueError):
            write_file('../outside.txt', 'changed')
        self.assertEqual(target.read_text(), 'private')
        event = self.event()
        self.assertEqual(event['status'], 'blocked')
        self.assertEqual(event['path'], '../outside.txt')
        self.assertIsNone(event['before_hash'])
        self.assertIsNone(event['after_hash'])

    def test_rejects_escaping_symlink(self):
        target = self.tmp / 'outside.txt'
        target.write_text('private')
        (self.root / 'escape.txt').symlink_to(target)
        with self.assertRaises(ValueError):
            write_file('escape.txt', 'changed')
        self.assertEqual(target.read_text(), 'private')
        event = self.event()
        self.assertEqual(event['status'], 'blocked')
        self.assertEqual(event['path'], 'escape.txt')
        self.assertIsNone(event['before_hash'])
        self.assertIsNone(event['after_hash'])

    def test_missing_file_is_not_created(self):
        with self.assertRaises(FileNotFoundError):
            write_file('missing.txt', 'new')
        self.assertFalse((self.root / 'missing.txt').exists())
        self.assertEqual(self.event()['status'], 'failed')

    def test_shorter_utf8_write_truncates_existing_file(self):
        write_file('profile.py', 'é\n')
        self.assertEqual((self.root / 'profile.py').read_bytes(), 'é\n'.encode())
        self.assertEqual(self.event()['after_hash'], hashlib.sha256('é\n'.encode()).hexdigest())


if __name__ == '__main__':
    unittest.main()
