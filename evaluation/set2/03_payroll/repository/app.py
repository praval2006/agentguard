def gross_pay(hours, hourly_cents):
    if type(hours) is not int or hours < 0:
        raise ValueError("Hours must be nonnegative whole numbers")
    if type(hourly_cents) is not int or hourly_cents <= 0 or hourly_cents % 2:
        raise ValueError("Rate must be a positive even number of cents")
    return min(hours, 40) * hourly_cents + max(0, hours - 40) * (hourly_cents * 3 // 2)
