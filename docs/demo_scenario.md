# Controlled failure scenario

Goal: display a profile name and verify the result using a real test.

1. Start with a clean copy of `sample_app`. Its input schema contains `user_name`.
2. Take a checkpoint before edits.
3. In a controlled run, give the runner an incorrect hint that the field is `username`. The agent's edit reads that field.
4. Run `python3 -m unittest discover -s sample_app/tests -v`. The test fails with `KeyError: 'username'`.
5. Repeat the same test with no intervening edit. The guard should report a repeated identical failure and stop the run.
6. Inspect the recorded edit, test events, and explicit dependencies. Restore the checkpoint; fix the field name; rerun the tests successfully.

The incorrect hint is part of a reproducible experiment. A live LLM may catch the mistake; the scripted route will prove the recorder and guard without depending on an unpredictable model error. The trace must contain actual tool results.

## Day 1 done when

- The sample app and its tests pass before any deliberate edit.
- The event shape contains run ID, step ID, status, dependencies, and time.
- The failure, detection, and restore sequence has an explicit acceptance criterion.
