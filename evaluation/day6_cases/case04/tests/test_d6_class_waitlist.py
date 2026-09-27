import copy
import unittest
from d6_class_waitlist.feature import promote

class WaitlistTests(unittest.TestCase):
    def test_single_waiting_member(self):
        for membership in ('regular', 'priority'):
            room = {'capacity': 2, 'enrolled': [],
                    'waiting': [{'id': 'member-7', 'membership': membership}]}
            self.assertEqual(promote(room), 'member-7')
            self.assertEqual(room['waiting'], [])
            self.assertEqual(room['enrolled'][0]['id'], 'member-7')

    def test_no_vacancy_or_waiters(self):
        for room in (
            {'capacity': 1, 'enrolled': [{'id': 'member-1'}], 'waiting': [{'id': 'member-2'}]},
            {'capacity': 2, 'enrolled': [], 'waiting': []},
        ):
            before = copy.deepcopy(room)
            self.assertIsNone(promote(room))
            self.assertEqual(room, before)

    def test_one_promotion_per_call(self):
        room = {'capacity': 3, 'enrolled': [], 'waiting': [{'id': 'a'}, {'id': 'b'}]}
        selected = promote(room)
        self.assertIn(selected, ('a', 'b'))
        self.assertEqual(len(room['enrolled']), 1)
        self.assertEqual(len(room['waiting']), 1)
