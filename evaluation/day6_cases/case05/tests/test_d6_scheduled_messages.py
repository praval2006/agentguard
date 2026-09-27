import unittest
from datetime import datetime, timedelta, timezone
from d6_scheduled_messages.feature import schedule, withdraw, tick

class Sender:
    def __init__(self):
        self.messages = []
    def send(self, team, body):
        self.messages.append((team, body))

class ScheduledMessageTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
        self.due = self.now + timedelta(minutes=10)
        self.jobs = []
        self.sender = Sender()

    def test_due_delivery_and_repeated_ticks(self):
        schedule(self.jobs, 'design', 'Standup', self.due, self.now)
        tick(self.jobs, self.now, self.sender)
        self.assertEqual(self.sender.messages, [])
        tick(self.jobs, self.due, self.sender)
        tick(self.jobs, self.due + timedelta(minutes=1), self.sender)
        self.assertEqual(self.sender.messages, [('design', 'Standup')])

    def test_withdraw_pending(self):
        job_id = schedule(self.jobs, 'design', 'Standup', self.due, self.now)
        self.assertTrue(withdraw(self.jobs, job_id, self.now))
        tick(self.jobs, self.due, self.sender)
        self.assertEqual(self.sender.messages, [])

    def test_future_time_required(self):
        for due in (self.now, self.now - timedelta(seconds=1)):
            with self.assertRaises(ValueError):
                schedule(self.jobs, 'design', 'Standup', due, self.now)
        self.assertEqual(self.jobs, [])

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            schedule(self.jobs, 'design', 'Standup', self.due.replace(tzinfo=None), self.now)
