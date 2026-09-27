import unittest
from d6_warehouse_dispatch.feature import dispatch

class DispatchTests(unittest.TestCase):
    def test_shipment_and_stock(self):
        shipment = {'status': 'packed', 'quantity': 3, 'tracking': None}
        inventory = {'on_hand': 10, 'reserved': 3}
        self.assertIs(dispatch(shipment, inventory, ' ZX12 '), shipment)
        self.assertEqual(shipment['status'], 'shipped')
        self.assertEqual(shipment['tracking'], 'ZX12')
        self.assertEqual(inventory['on_hand'], 7)

    def test_repeat_does_not_deduct_again(self):
        shipment = {'status': 'packed', 'quantity': 3, 'tracking': None}
        inventory = {'on_hand': 10, 'reserved': 3}
        dispatch(shipment, inventory, 'ZX12')
        before = dict(inventory)
        dispatch(shipment, inventory, 'ZX12')
        self.assertEqual(inventory, before)

    def test_rejected_dispatch_preserves_records(self):
        for stock, tracking in ((2, 'ZX12'), (10, ''), (10, '   ')):
            shipment = {'status': 'packed', 'quantity': 3, 'tracking': None}
            inventory = {'on_hand': stock, 'reserved': 3}
            before = dict(shipment), dict(inventory)
            with self.assertRaises(ValueError):
                dispatch(shipment, inventory, tracking)
            self.assertEqual((shipment, inventory), before)
