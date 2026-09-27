import unittest
from d6_room_reservations.feature import reserve

class ReservationTests(unittest.TestCase):
    def test_regular_durations(self):
        rows = []
        for value in (15, 30, 60, 90):
            result = reserve(value, rows)
            self.assertEqual(result['duration_minutes'], value)
            self.assertEqual(rows[-1], result)
        self.assertEqual([r['id'] for r in rows], [1, 2, 3, 4])

    def test_invalid_durations_leave_rows_alone(self):
        for value in (0, -15, 14, 16, 135, 30.5, '30', True, None):
            with self.subTest(value=value):
                rows = [{'id': 1, 'duration_minutes': 30}]
                before = [dict(r) for r in rows]
                with self.assertRaises(ValueError):
                    reserve(value, rows)
                self.assertEqual(rows, before)

    def test_return_is_detached(self):
        rows = []
        result = reserve(45, rows)
        result['duration_minutes'] = 60
        self.assertEqual(rows[0]['duration_minutes'], 45)
