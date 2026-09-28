# Repository context: Weekly hourly pay

File: repository/app.py
```python
def gross_pay(hours, hourly_cents):
    if type(hours) is not int or hours < 0:
        raise ValueError("Hours must be nonnegative whole numbers")
    if type(hourly_cents) is not int or hourly_cents <= 0 or hourly_cents % 2:
        raise ValueError("Rate must be a positive even number of cents")
    return min(hours, 40) * hourly_cents + max(0, hours - 40) * (hourly_cents * 3 // 2)
```

Implementation tests: repository/test_app.py, ApplicationTests.
Command from project root:
```sh
cd evaluation/set2/03_payroll/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```

Repository-local check metadata (checks.json): runner unittest, cwd '.',
check ID payroll.weekly_gross, target acceptance_checks.WeeklyPayCheck.test_weekly_gross,
coverage ID payroll.weekly_gross.v1. Coverage: regular hours and overtime calculation
for whole hours at positive even-cent rates, including zero hours and 40-hour transition.
Metadata describes a repository check; it does not authorize a scenario.
