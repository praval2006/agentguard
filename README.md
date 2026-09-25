# AgentGuard and FlightRecorder

Day 1 scaffold for the LovHack MVP. The `sample_app` is the small repository the agent will later inspect and edit. Its data uses `user_name`; displaying `username` instead will produce a real failing test.

## Start here

Requires Python 3.10 or newer. No packages are needed for the scaffold.

```bash
cd agentguard
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s sample_app/tests -v
python3 -m sample_app.profile
```

Both test commands should pass initially. During the failure demo, the agent will change `sample_app/profile.py`, and the sample app test will fail until that change is corrected or restored.

## Layout

- `sample_app/`: tiny profile application and its real test.
- `agentguard/`: event contract, recorder, and guard placeholders.
- `tests/`: tests for AgentGuard's event contract.
- `docs/`: scenario and completion criteria.

The next step is to implement a bounded runner with `read_file`, `write_file`, and `run_tests` tools that can operate only inside `sample_app`.
