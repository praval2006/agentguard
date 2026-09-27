# Day 3 Grounding Validation

## Method and scope

This is a qualitative engineering validation of three frozen Day-2 cases, not an
independent benchmark or proof of general correctness. The planner-style outputs
below were derived from each case's task and context for this checkpoint; they
are not reconstructed Day-2 raw outputs. Grounding then used only that output,
the same context, and the conservative instructions in `agentguard/grounding.py`.
No other implementation files supplied application execution evidence.

The dictionaries are recorded as Python literals. Each planner output was checked
through `plan_acceptance` using an injected callable returning the recorded plan.
Each grounding list was checked through `ground_scenarios` using an injected
callable returning the recorded representations, and every representation was
also checked with `validate_scenario`. These local callables replay authored data;
they are not an external provider or an independent reasoning-quality test.
No HTTP requests or represented test commands were executed.

## 08_api_pagination

### Task summary

Add cursor pagination with newest-first results, default size 25, maximum requested size 100, and complete duplicate-free traversal of static history.

### Repository evidence relevant to execution

The list_activity function filters SQL rows by workspace and orders created_at descending. IDs are unique, timestamps can tie, query parameters are strings, and middleware resolves authenticated workspace membership. No public HTTP path/method, pagination parameter names, cursor response field, runtime data fixture, or existing test command is documented.

### Planner output considered

```python
{'explicit_requirements': ['Check default pages of 25, requested sizes up to 100, and newest-first '
                           'ordering.',
                           'Follow continuation through static history and check that every entry '
                           'appears once, including entries sharing timestamps.',
                           'Check that a next cursor is included when additional entries remain.'],
 'inferred_behaviors': ['Check that pagination returns only activity from the authenticated '
                        'workspace.'],
 'ambiguities': ['Whether sizes above 100 are rejected or capped is unspecified.',
                 'Invalid cursor handling and terminal cursor representation are unspecified.',
                 'The order among equal timestamps is unspecified; complete traversal still '
                 'applies.'],
 'scenarios': [{'name': 'Page sizes and newest-first order',
                'behavior': 'Check default pages of 25, requested sizes up to 100, and '
                            'newest-first ordering.',
                'source': 'explicit',
                'reason': 'The task states default and maximum page sizes and newest-first '
                          'ordering.'},
               {'name': 'Traverse static history including timestamp ties',
                'behavior': 'Follow continuation through static history and check that every entry '
                            'appears once, including entries sharing timestamps.',
                'source': 'explicit',
                'reason': 'The task requires complete duplicate-free traversal; context supplies '
                          'equal-timestamp entries as a relevant boundary.'},
               {'name': 'Continuation when more entries remain',
                'behavior': 'Check that a next cursor is included when additional entries remain.',
                'source': 'explicit',
                'reason': 'The task directly requires a next cursor when more entries are '
                          'available.'},
               {'name': 'Workspace-scoped pagination',
                'behavior': 'Check that pagination returns only activity from the authenticated '
                            'workspace.',
                'source': 'inferred',
                'reason': 'The supplied function filters by authenticated workspace; preserving '
                          'that scope is relevant to pagination.'}]}
```

### Grounded representations

```python
[{'name': 'Page sizes and newest-first order',
  'source': 'explicit',
  'reason': 'The task states default and maximum page sizes and newest-first ordering.',
  'action': {'type': 'unsupported',
             'explanation': 'No HTTP route/method, page-size parameter contract, or existing test '
                            'command is evidenced. Data for page-size and ordering checks is not '
                            'supplied.'}},
 {'name': 'Traverse static history including timestamp ties',
  'source': 'explicit',
  'reason': 'The task requires complete duplicate-free traversal; context supplies equal-timestamp '
            'entries as a relevant boundary.',
  'action': {'type': 'unsupported',
             'explanation': 'No route, cursor interface, static-history fixture, or existing test '
                            'command is evidenced. Multi-request traversal and collection-wide '
                            'uniqueness are beyond a single HTTP action with status/scalar '
                            'assertions.'}},
 {'name': 'Continuation when more entries remain',
  'source': 'explicit',
  'reason': 'The task directly requires a next cursor when more entries are available.',
  'action': {'type': 'unsupported',
             'explanation': 'No route, response cursor field, or fixture demonstrating remaining '
                            'entries is documented. The schema has no generic field-presence '
                            'assertion and no expected cursor value is evidenced.'}},
 {'name': 'Workspace-scoped pagination',
  'source': 'inferred',
  'reason': 'The supplied function filters by authenticated workspace; preserving that scope is '
            'relevant to pagination.',
  'action': {'type': 'unsupported',
             'explanation': 'No HTTP route, authentication inputs, cross-workspace fixture, or '
                            'existing test command is supplied. Collection membership checks are '
                            'not supported by scalar equality assertions.'}}]
```

### Justification and unresolved information

All representations above are `unsupported`. Each preserves its planner name, source, and reason in order; the planner behavior remains recorded above. Each action explanation identifies the missing execution evidence or schema capability. No command, endpoint, fixture identifier, or runtime value was invented. The ambiguities listed in the planner output remain unresolved; even resolving those product questions would not supply the absent execution mechanisms.

## 10_resource_deletion

### Task summary

Add owner-only DELETE /reports/{id}, return 204 on deletion and 404 for missing or other-owned reports, and remove deleted reports from the owner list.

### Repository evidence relevant to execution

The task requests DELETE /reports/{id}; this is a product requirement, not evidence that a runnable route exists. Context shows list_reports and get_report Python handlers, a 404 response for missing/other-owned detail reads, and repository get/for_owner/delete methods. It supplies neither route bindings nor a delete handler. Authentication middleware supplies request.user, but credentials, fixtures, and supported test commands are absent. The detail handler's 404 does not establish the requested DELETE behavior.

### Planner output considered

```python
{'explicit_requirements': ['As the owner, delete an existing report, receive 204, and observe its '
                           'removal from a fresh owner list.',
                           'Attempt deletion as a non-owner; check 404 and preservation of the '
                           'report.',
                           'Delete a nonexistent report and check for 404.'],
 'inferred_behaviors': ['After deletion, check that the former report is no longer retrievable.'],
 'ambiguities': ['Behavior for malformed IDs or storage failure is unspecified.'],
 'scenarios': [{'name': 'Owner deletion and list removal',
                'behavior': 'As the owner, delete an existing report, receive 204, and observe its '
                            'removal from a fresh owner list.',
                'source': 'explicit',
                'reason': 'The task explicitly requires owner deletion, status 204, and '
                          'disappearance from the owner list.'},
               {'name': 'Reject another user',
                'behavior': 'Attempt deletion as a non-owner; check 404 and preservation of the '
                            'report.',
                'source': 'explicit',
                'reason': 'The task explicitly limits deletion to the owner and requires 404 for '
                          'other-owned reports.'},
               {'name': 'Missing report deletion',
                'behavior': 'Delete a nonexistent report and check for 404.',
                'source': 'explicit',
                'reason': 'The task explicitly requires 404 when the report does not exist.'},
               {'name': 'Deleted report cannot be retrieved',
                'behavior': 'After deletion, check that the former report is no longer '
                            'retrievable.',
                'source': 'inferred',
                'reason': 'Removal reasonably implies loss of detail retrieval, and context '
                          'supplies a detail-read handler.'}]}
```

### Grounded representations

```python
[{'name': 'Owner deletion and list removal',
  'source': 'explicit',
  'reason': 'The task explicitly requires owner deletion, status 204, and disappearance from the '
            'owner list.',
  'action': {'type': 'unsupported',
             'explanation': 'The requested DELETE route is not established by repository context; '
                            'list routing, owner authentication, and existing-report fixture are '
                            'also missing. A delete followed by list inspection requires execution '
                            'orchestration beyond a single HTTP action.'}},
 {'name': 'Reject another user',
  'source': 'explicit',
  'reason': 'The task explicitly limits deletion to the owner and requires 404 for other-owned '
            'reports.',
  'action': {'type': 'unsupported',
             'explanation': 'No evidenced DELETE binding, authentication setup, two-user report '
                            'fixture, or existing test command is supplied. The context '
                            'detail-read 404 is not evidence for a DELETE action.'}},
 {'name': 'Missing report deletion',
  'source': 'explicit',
  'reason': 'The task explicitly requires 404 when the report does not exist.',
  'action': {'type': 'unsupported',
             'explanation': 'No repository-backed DELETE route or supported test command is '
                            'evidenced. No identifier with a documented nonexistent-state '
                            'guarantee is supplied; a symbolic name alone would not supply that '
                            'guarantee.'}},
 {'name': 'Deleted report cannot be retrieved',
  'source': 'inferred',
  'reason': 'Removal reasonably implies loss of detail retrieval, and context supplies a '
            'detail-read handler.',
  'action': {'type': 'unsupported',
             'explanation': 'The Python detail handler has no documented HTTP route/method '
                            'binding. No deleted-report fixture or existing test command is '
                            'supplied; naming the handler does not authorize inventing a GET '
                            'endpoint.'}}]
```

### Justification and unresolved information

All representations above are `unsupported`. Each preserves its planner name, source, and reason in order; the planner behavior remains recorded above. Each action explanation identifies the missing execution evidence or schema capability. No command, endpoint, fixture identifier, or runtime value was invented. The ambiguities listed in the planner output remain unresolved; even resolving those product questions would not supply the absent execution mechanisms.

## 01_subscription_cancellation

### Task summary

Cancel an active subscription, remove premium access, and handle repeated cancellation without crashing while retaining a consistent cancelled state.

### Repository evidence relevant to execution

Context contains only cancel_subscription(subscription: dict), which assigns status and returns the dictionary. No HTTP route, existing test command, premium-access observation interface, or fixture setup is supplied. Direct Python invocation is not an MVP scenario action.

### Planner output considered

```python
{'explicit_requirements': ['Cancel an active subscription and check that its status becomes '
                           'cancelled.',
                           'After cancellation, check that the user cannot access premium '
                           'features.',
                           'Repeat cancellation and check that the application does not crash, '
                           'remains cancelled, and does not restore premium access.'],
 'inferred_behaviors': [],
 'ambiguities': ['Premium-access representation and its observable enforcement mechanism are '
                 'unspecified in context.',
                 'Behavior for states other than active or already cancelled is unspecified.'],
 'scenarios': [{'name': 'Cancelled subscription state',
                'behavior': 'Cancel an active subscription and check that its status becomes '
                            'cancelled.',
                'source': 'explicit',
                'reason': 'The task directly requires an active subscription to become cancelled.'},
               {'name': 'Premium access removed',
                'behavior': 'After cancellation, check that the user cannot access premium '
                            'features.',
                'source': 'explicit',
                'reason': 'The task and acceptance intent prohibit premium access after '
                          'cancellation.'},
               {'name': 'Safe repeated cancellation',
                'behavior': 'Repeat cancellation and check that the application does not crash, '
                            'remains cancelled, and does not restore premium access.',
                'source': 'explicit',
                'reason': 'The task requires safe repeated cancellation and a consistent cancelled '
                          'state without premium access.'}]}
```

### Grounded representations

```python
[{'name': 'Cancelled subscription state',
  'source': 'explicit',
  'reason': 'The task directly requires an active subscription to become cancelled.',
  'action': {'type': 'unsupported',
             'explanation': 'Only a Python function is evidenced. There is no supported HTTP route '
                            'or documented existing test command; direct function execution is '
                            'outside the current schema.'}},
 {'name': 'Premium access removed',
  'source': 'explicit',
  'reason': 'The task and acceptance intent prohibit premium access after cancellation.',
  'action': {'type': 'unsupported',
             'explanation': 'No HTTP route, existing test command, or premium-access observation '
                            'mechanism is supplied. No access field, endpoint, or fixture value '
                            'can be invented.'}},
 {'name': 'Safe repeated cancellation',
  'source': 'explicit',
  'reason': 'The task requires safe repeated cancellation and a consistent cancelled state without '
            'premium access.',
  'action': {'type': 'unsupported',
             'explanation': 'Only a Python function is evidenced, with no supported route or '
                            'existing test command. Repeated invocation and premium-access '
                            'observation cannot be expressed from the supplied context using the '
                            'current actions.'}}]
```

### Justification and unresolved information

All representations above are `unsupported`. Each preserves its planner name, source, and reason in order; the planner behavior remains recorded above. Each action explanation identifies the missing execution evidence or schema capability. No command, endpoint, fixture identifier, or runtime value was invented. The ambiguities listed in the planner output remain unresolved; even resolving those product questions would not supply the absent execution mechanisms.

## Overall assessment

1. **Did grounding avoid inventing execution mechanisms?** Yes, in these authored outputs. Function names and SQL queries were not treated as HTTP bindings. A requested DELETE API was not treated as proof of an existing endpoint. No existing test command was documented in any selected context, so none was constructed.
2. **Was useful acceptance intent preserved?** Yes. All 11 planner scenarios remain recorded, with their behavior and grounding metadata, and each has an unsupported representation explaining the missing evidence/capability. Unsupported means the current representation cannot execute the check; it is not an implementation failure.
3. **Were any scenarios safely executable under the current schema?** None could be responsibly represented as executable from these inputs: **0 HTTP, 0 test-command, 11 unsupported**. This does not mean these applications have no routes or tests; it means the supplied evidence does not establish them.
4. **What does this imply for Day 4?** Build the bounded verifier around the supported representations while retaining honest handling of unsupported intent. Executable demonstrations will need explicitly supplied route/method/response contracts, authentication and fixture setup where relevant, or documented existing test commands that cover the intended behavior. Do not retrofit those details into these frozen inputs or silently expand the DSL. Grounding relevance and evidence review remain necessary before execution.
5. **What limitation should be explicit?** Planner relevance is not executability. The current schema cannot directly invoke Python functions, query SQL, orchestrate multi-step flows, or assert arbitrary collection properties. Symbolic variables cannot create missing mechanisms or fixture guarantees. Structural validators establish dictionary validity and metadata correspondence, not evidence truth, semantic completeness, command safety, or general grounding reliability. This all-unsupported sample validates conservative abstention, not successful execution or the ability to distinguish every executable case.

## Contract and regression validation

- Three planner outputs accepted through the existing planner contract.
- Three grounding lists accepted through `ground_scenarios`; all 11 dictionaries separately accepted by `validate_scenario`.
- Original planner scenario order and name/source/reason preserved throughout.

Regression commands run after document creation:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
python3 -m unittest discover -s sample_app/tests -p "test_*.py" -v
```

- AgentGuard: 76/76 passed.
- Sample app: 4/4 passed.

These regression runs are separate from the recorded acceptance scenarios; no scenario action was executed.
