from datetime import timezone

def schedule(jobs, team, body, due_at, now):
    for value in (due_at, now):
        if value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
            raise ValueError('Use UTC timestamps')
    if due_at <= now:
        raise ValueError('Choose a future delivery time')
    job = {'id': len(jobs) + 1, 'team': team, 'body': body,
           'due_at': due_at, 'state': 'pending'}
    jobs.append(job)
    return job['id']

def withdraw(jobs, job_id, now):
    job = next(job for job in jobs if job['id'] == job_id)
    if job['state'] == 'pending' and now < job['due_at']:
        job['state'] = 'withdrawn'
        return True
    return False

def tick(jobs, now, sender):
    for job in jobs:
        if job['state'] == 'pending' and job['due_at'] <= now:
            sender.send(job['team'], job['body'])
            job['state'] = 'delivered'
