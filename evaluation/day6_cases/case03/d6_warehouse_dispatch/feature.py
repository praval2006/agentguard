def dispatch(shipment, inventory, tracking):
    if shipment['status'] == 'shipped':
        return shipment
    if not isinstance(tracking, str) or not tracking.strip():
        raise ValueError('Tracking reference is required')
    quantity = shipment['quantity']
    if shipment['status'] != 'packed' or inventory['on_hand'] < quantity:
        raise ValueError('Shipment is not ready for dispatch')
    inventory['on_hand'] -= quantity
    shipment.update(status='shipped', tracking=tracking.strip())
    return shipment
