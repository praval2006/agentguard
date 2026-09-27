import unittest
from d6_work_orders.feature import start_order

class WorkOrderTests(unittest.TestCase):
    def test_start(self):
        order = {'status': 'queued', 'description': 'Inspect pump'}
        self.assertIs(start_order(order), order)
        self.assertEqual(order, {'status': 'in_progress', 'description': 'Inspect pump'})

    def test_start_twice(self):
        order = {'status': 'queued', 'description': 'Inspect pump'}
        start_order(order)
        self.assertEqual(start_order(order)['status'], 'in_progress')

    def test_completed_unchanged(self):
        order = {'status': 'completed', 'description': 'Inspect pump'}
        before = dict(order)
        with self.assertRaises(ValueError):
            start_order(order)
        self.assertEqual(order, before)

    def test_unknown_state(self):
        with self.assertRaises(ValueError):
            start_order({'status': 'other'})
