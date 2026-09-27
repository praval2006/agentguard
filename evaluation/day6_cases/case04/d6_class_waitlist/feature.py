def promote(classroom):
    if len(classroom['enrolled']) >= classroom['capacity'] or not classroom['waiting']:
        return None
    attendee = classroom['waiting'].pop(0)
    classroom['enrolled'].append(attendee)
    return attendee['id']
