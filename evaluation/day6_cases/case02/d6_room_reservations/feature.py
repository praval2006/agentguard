def reserve(duration_minutes, reservations):
    if type(duration_minutes) is not int or not 15 <= duration_minutes < 120:
        raise ValueError('Duration must be 15 to 120 whole minutes')
    if duration_minutes % 15:
        raise ValueError('Duration must use 15-minute increments')
    reservation = {'id': len(reservations) + 1, 'duration_minutes': duration_minutes}
    reservations.append(reservation)
    return dict(reservation)
