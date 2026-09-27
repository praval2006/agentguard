def start_order(order):
    if order['status'] == 'completed':
        raise ValueError('Completed orders cannot be started')
    if order['status'] not in ('queued', 'in_progress'):
        raise ValueError('Unknown work-order state')
    order['status'] = 'in_progress'
    return order
