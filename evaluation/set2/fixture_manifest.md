# Evaluation Set 2 fixture manifest

Protocol: `evaluation/evaluation_set_2_protocol.md`, frozen at `af01992`.
Fixture freeze: the commit titled `Freeze Evaluation Set 2 fixtures` containing
this manifest (use its Git object ID; no self-referential hash is embedded).
Architecture baseline: `56d7cf8`. Date: 2026-09-28.

This manifest is evaluation administration, not a planner/grounder input.
Only each case's task.md and context.md are designated later reasoning inputs.
All fixtures were authored by Codex in this project conversation. No independent
blinding or independent fixture authorship is claimed.

## Cases and implementation-test records

Commands below were executed from the project root using the stated cwd change.
Each suite ran once and exited 0 with 3 tests and OK (15 tests total). No application
or test correction followed those executions. The separately registered payroll
check was not executed and is not included in these implementation-test counts.

### 01_roast_temperature: Roast temperature validation

- Frozen category: Inclusive boundary.
- Description: Stateless coffee-roast temperature validation.
- Task: `evaluation/set2/01_roast_temperature/task.md`.
- Context: `evaluation/set2/01_roast_temperature/context.md`.
- Repository root: `evaluation/set2/01_roast_temperature/repository/`.
- Implementation tests: `repository/test_app.py`.
- Result: 3 tests, OK, exit 0.

```sh
cd evaluation/set2/01_roast_temperature/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```

### 02_parcel_label: Parcel label preview

- Frozen category: Multiple required observable properties.
- Description: Stateless recipient, postal code and service label preview.
- Task: `evaluation/set2/02_parcel_label/task.md`.
- Context: `evaluation/set2/02_parcel_label/context.md`.
- Repository root: `evaluation/set2/02_parcel_label/repository/`.
- Implementation tests: `repository/test_app.py`.
- Result: 3 tests, OK, exit 0.

```sh
cd evaluation/set2/02_parcel_label/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```

### 03_payroll: Weekly hourly pay

- Frozen category: Registered repository check.
- Description: Integer-cent regular and overtime pay calculation.
- Task: `evaluation/set2/03_payroll/task.md`.
- Context: `evaluation/set2/03_payroll/context.md`.
- Repository root: `evaluation/set2/03_payroll/repository/`.
- Implementation tests: `repository/test_app.py`.
- Result: 3 tests, OK, exit 0.

```sh
cd evaluation/set2/03_payroll/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```

### 04_tournament: Tournament standings

- Frozen category: Insufficient evidence / product ambiguity.
- Description: Points-ordered standings; task asks for fairness for ties without specifying a tie policy.
- Task: `evaluation/set2/04_tournament/task.md`.
- Context: `evaluation/set2/04_tournament/context.md`.
- Repository root: `evaluation/set2/04_tournament/repository/`.
- Implementation tests: `repository/test_app.py`.
- Result: 3 tests, OK, exit 0.

```sh
cd evaluation/set2/04_tournament/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```

### 05_quiz_attempt: Arithmetic practice attempts

- Frozen category: Beyond current capability.
- Description: Runtime attempt identifiers connect answer submission and later result retrieval.
- Task: `evaluation/set2/05_quiz_attempt/task.md`.
- Context: `evaluation/set2/05_quiz_attempt/context.md`.
- Repository root: `evaluation/set2/05_quiz_attempt/repository/`.
- Implementation tests: `repository/test_app.py`.
- Result: 3 tests, OK, exit 0.

```sh
cd evaluation/set2/05_quiz_attempt/repository && python3 -B -m unittest discover -s . -p 'test_app.py' -v
```

## Interfaces and trusted setup

Cases 1, 2, 4 and 5 supply repository/server.py context managers using the shared
http_server.py adapter. The adapter binds only numeric loopback and closes on
context exit. Import with the case repository and project root on sys.path.
Application dispatch is exercised directly by ordinary tests; no new case server
or acceptance scenario was executed in this checkpoint. Source parsing validated
all new Python files. Cases 1, 2 and 4 retain no application state; Case 5 retains
attempts for the lifetime of its server instance. Case 3 is a local Python callable.

Case 3 trusted static setup:

- Root: `evaluation/set2/03_payroll/repository`.
- Check source: `acceptance_checks.py`.
- Registry: `checks.json`, cwd `.`, runner `unittest`.
- Target: `acceptance_checks.WeeklyPayCheck.test_weekly_gross`.
- Check ID: `payroll.weekly_gross`.
- Coverage ID: `payroll.weekly_gross.v1`; description is frozen in the registry.
- Registry was loaded with the existing strict parser without check execution.
- Exact scenario coverage authorization: pending/unavailable. No authorization
  artifact or future scenario identity was created. Registry metadata is not an
  authorization. No later post-hoc trust decision is permitted by this checkpoint.

Case 3's trusted registered check and registry metadata were authored by Codex during the explicitly authorized pre-reasoning fixture-construction phase. They were frozen before AgentGuard planner/grounder reasoning. Therefore this evaluates the registered-check trust architecture under role-separated setup; it does not demonstrate independently human-authored acceptance coverage.

This records the user's explicit role-based clarification without changing the
frozen protocol. After freeze, the planner/grounder cannot write or modify checks,
registry, coverage metadata, or trust configuration. It cannot authorize semantic
coverage. If exact authorization cannot legitimately be supplied under the frozen
trust model, retain that limitation; do not predict an identity, weaken matching,
or rewrite a scenario. These setup artifacts do not establish independent coverage.

## Audit and validation

Keyword audit before administrative documentation was added:
`rg -ni 'intentional|bug|broken|missing|AgentGuard|expected verdict|should catch|PASS|FAIL|UNVERIFIED' evaluation/set2`
returned no matches. Manual review of task/context/source, comments, and test names
found no equivalent experiment or outcome hints. This manifest and the work log
contain methodology terms and are excluded from reasoning inputs.
All context source excerpts match their app.py verbatim; context lengths are
1146, 1280, 1083, 1362, and 1921 characters respectively, below 32,000 each.
The tournament context describes current ordering without presenting it as required
tie policy. No task/context includes implementation-test results or future scenarios.

Separate unchanged regression command:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

283 tests, OK, exit 0. Escalation allowed existing loopback regression tests.
Regression tests exercise existing components; this was not evaluation reasoning
or a rerun of historical evaluation harnesses.

No Set-2 planner/grounder calls, planner outputs, grounded scenarios, acceptance
verification, or acceptance results occurred. The registered check was not run.
No AgentGuard production code/tests, protocol, sample app, Day-5, Day-6, or
registered-check smoke artifacts changed. Historical evaluation harnesses were
not rerun. No desired verdict distribution guided fixture construction.

## Frozen input inventory (SHA-256)

Hashes cover every fixture file and shared adapter, excluding this manifest.

- `01_roast_temperature/context.md`: `bf63cebc1a9a1c023f827a42ed2eacd2fe3f01345b11ff25196069cdb49d1350`
- `01_roast_temperature/repository/README.md`: `bd144e2a53b42c814c95d9988006b2e4617a78a80a7945fbb25c0f4cc0917874`
- `01_roast_temperature/repository/app.py`: `ed6c194ef6a647d24b89756e4270e798609de9b1f1feecd391c49225d5b5eeb4`
- `01_roast_temperature/repository/server.py`: `749776b0eee7f4b00ffbf9e486aaa67ebca8a4e56358050c58bcf12cd313da9b`
- `01_roast_temperature/repository/test_app.py`: `31d13257b8ab553f11ba9d4b5d5445459dfbe59782dee45dea863b7119e46c4f`
- `01_roast_temperature/task.md`: `6afd8682bb7071bccd1beeb96686c6a94929116c98b6c5020e8e00fd14afec08`
- `02_parcel_label/context.md`: `46cfc637f5416248d3d14362c2c225e933acf737800911b5724c65d4b7be9f86`
- `02_parcel_label/repository/README.md`: `cadb6996340f5bb5b86f27b9b9cb0d65f5cc7567974399fabb619a700425f321`
- `02_parcel_label/repository/app.py`: `91a487e469b756b43a5c0edfe2b930c8d07b6ad5747299a8939d979d67d31d16`
- `02_parcel_label/repository/server.py`: `749776b0eee7f4b00ffbf9e486aaa67ebca8a4e56358050c58bcf12cd313da9b`
- `02_parcel_label/repository/test_app.py`: `0e4b82c5fe90be73779ff4e3288e487438f16a1bb92424df7cee0376c8605b62`
- `02_parcel_label/task.md`: `7399739d1c5badb50ae88ca5f5f4b61e1caa327fa7d006b0601ecdff000b0cdd`
- `03_payroll/context.md`: `7e3eeff28055ea9e58d982f0ef473dcec03a45f3a93253c12c86a0efd82d9f2f`
- `03_payroll/repository/README.md`: `7ee253751733fb7f56b0d7a2b9657ea5a67ae1c7baf7a61682b619eb9ba032a0`
- `03_payroll/repository/acceptance_checks.py`: `200d94dfd00a227069db45c3a96ab8b0750e69046e535924e1c05dae28340511`
- `03_payroll/repository/app.py`: `dc276a4de1ac459d86cbfa647a1abba03c6bd0e417d0654f2bb6e3287d52a244`
- `03_payroll/repository/checks.json`: `140a123740c1b148235365f33a339441146b9b415599ae0751076b1eb4248ff0`
- `03_payroll/repository/test_app.py`: `9eedde46b0426205c88678f76e74cc1bd06bc23d6e4e689a455a2865af74aa94`
- `03_payroll/task.md`: `b8bd5253aaea58ae7517cd832c3c2cd423c993a7dacd80ee0c3795f907572010`
- `04_tournament/context.md`: `956e02586550af2c8f141b1fa20d6e3be5d5a3f0ca8ba4b646f767c07ca8d91a`
- `04_tournament/repository/README.md`: `0742faa1573e9449919dba8eb58952919637d28f339bf41dd0f562ee88335f63`
- `04_tournament/repository/app.py`: `9539c218c58077263432c7163e4b1bedce1fdc7e5c7a0f0572a44eec2e64315a`
- `04_tournament/repository/server.py`: `749776b0eee7f4b00ffbf9e486aaa67ebca8a4e56358050c58bcf12cd313da9b`
- `04_tournament/repository/test_app.py`: `66476c2b676e469f4e4d93d4a4684ef80ce1c0d7c359c16185f7d83e7f605f32`
- `04_tournament/task.md`: `5dc508211a8cd244516728d06f8413fe806701751238dc70fd21d5c5fb73aa47`
- `05_quiz_attempt/context.md`: `4a4c6c1228ee2b892a1829a9b11cd0a4a7b0f71dc678c67d5c0f881fbf723975`
- `05_quiz_attempt/repository/README.md`: `1c256c7b17b6c0d57267d010bc942eafbf9e6f879198296d9e67248142d3cbcf`
- `05_quiz_attempt/repository/app.py`: `a07dfdfbd4fd84d227757271e9f286d795d821735819da7ff99332b751d8cead`
- `05_quiz_attempt/repository/server.py`: `68f5622e1a6d13551f6941e5b37f3729677c86f7ec8f2f3347861cd8e5476fd1`
- `05_quiz_attempt/repository/test_app.py`: `b1a41a55abf9b191187c975958868491ae7ec6be2320fdf70b739b54e777ddf4`
- `05_quiz_attempt/task.md`: `a1e79cb08543190cece88073a10d03a53d45dc5d3bbf1aa854610e4b5680de65`
- `http_server.py`: `73bbbf2d99f2c81f64c647e006013241acf961597259bdb92616eff913605238`
