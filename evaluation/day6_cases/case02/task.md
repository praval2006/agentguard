# Reserve a Meeting Room

Allow a meeting organizer to reserve the room for a whole number of minutes.
Reservations must last at least 15 minutes and at most 120 minutes, inclusive,
in 15-minute increments. Reject invalid durations with a clear error and do not
create a reservation. On success return a reservation ID and its duration.
