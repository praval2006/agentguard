# Day 6 Fixture Manifest

## case01

- Case identifier: `case01`
- Category: Straightforward state-transition behavior.
- Task: `evaluation/day6_cases/case01/task.md`
- Context: `evaluation/day6_cases/case01/context.md`
- Implementation files: `evaluation/day6_cases/case01/d6_work_orders/__init__.py`, `evaluation/day6_cases/case01/d6_work_orders/feature.py`, `evaluation/day6_cases/case01/d6_work_orders/http_interface.py`
- Test file: `evaluation/day6_cases/case01/tests/test_d6_work_orders.py`
- Exact implementation-test command (repository root):

```bash
(cd evaluation/day6_cases/case01 && python3 -B -m unittest discover -s tests -v)
```

- Implementation-test result: 4/4 tests passed; unittest `OK`; exit code 0.
- Infrastructure repairs: none.

## case02

- Case identifier: `case02`
- Category: Boundary/validation behavior.
- Task: `evaluation/day6_cases/case02/task.md`
- Context: `evaluation/day6_cases/case02/context.md`
- Implementation files: `evaluation/day6_cases/case02/d6_room_reservations/__init__.py`, `evaluation/day6_cases/case02/d6_room_reservations/feature.py`, `evaluation/day6_cases/case02/d6_room_reservations/http_interface.py`
- Test file: `evaluation/day6_cases/case02/tests/test_d6_room_reservations.py`
- Exact implementation-test command (repository root):

```bash
(cd evaluation/day6_cases/case02 && python3 -B -m unittest discover -s tests -v)
```

- Implementation-test result: 3/3 tests passed; unittest `OK`; exit code 0.
- Infrastructure repairs: none.

## case03

- Case identifier: `case03`
- Category: Interaction between multiple related state fields.
- Task: `evaluation/day6_cases/case03/task.md`
- Context: `evaluation/day6_cases/case03/context.md`
- Implementation files: `evaluation/day6_cases/case03/d6_warehouse_dispatch/__init__.py`, `evaluation/day6_cases/case03/d6_warehouse_dispatch/feature.py`
- Test file: `evaluation/day6_cases/case03/tests/test_d6_warehouse_dispatch.py`
- Exact implementation-test command (repository root):

```bash
(cd evaluation/day6_cases/case03 && python3 -B -m unittest discover -s tests -v)
```

- Implementation-test result: 3/3 tests passed; unittest `OK`; exit code 0.
- Infrastructure repairs: none.

## case04

- Case identifier: `case04`
- Category: Behavior containing a genuine product ambiguity.
- Task: `evaluation/day6_cases/case04/task.md`
- Context: `evaluation/day6_cases/case04/context.md`
- Implementation files: `evaluation/day6_cases/case04/d6_class_waitlist/__init__.py`, `evaluation/day6_cases/case04/d6_class_waitlist/feature.py`
- Test file: `evaluation/day6_cases/case04/tests/test_d6_class_waitlist.py`
- Exact implementation-test command (repository root):

```bash
(cd evaluation/day6_cases/case04 && python3 -B -m unittest discover -s tests -v)
```

- Implementation-test result: 3/3 tests passed; unittest `OK`; exit code 0.
- Infrastructure repairs: none.

## case05

- Case identifier: `case05`
- Category: Behavior that may exceed current execution capability.
- Task: `evaluation/day6_cases/case05/task.md`
- Context: `evaluation/day6_cases/case05/context.md`
- Implementation files: `evaluation/day6_cases/case05/d6_scheduled_messages/__init__.py`, `evaluation/day6_cases/case05/d6_scheduled_messages/feature.py`
- Test file: `evaluation/day6_cases/case05/tests/test_d6_scheduled_messages.py`
- Exact implementation-test command (repository root):

```bash
(cd evaluation/day6_cases/case05 && python3 -B -m unittest discover -s tests -v)
```

- Implementation-test result: 4/4 tests passed; unittest `OK`; exit code 0.
- Infrastructure repairs: none.
