"""Deterministic dispatch and aggregation of already-grounded scenarios."""

from copy import deepcopy

from .execution import execute_test_scenario
from .registered_execution import execute_registered_check
from .coverage_authorization import authorized_registration
from .http_execution import execute_http_scenario
from .sequence_execution import execute_http_sequence
from .planner import MAX_SCENARIOS
from .scenarios import validate_scenario
from .verifier import MAX_EVIDENCE_CHARS, verify_observation, aggregate_composite_results


def _unobserved(scenario, reason=None):
    result = verify_observation(scenario)
    execution_reason = reason if reason is not None else result["reason"]
    execution = {"established": False, "reason": execution_reason[:MAX_EVIDENCE_CHARS]}
    if len(execution_reason) > MAX_EVIDENCE_CHARS:
        execution["reason_truncated"] = True
    if "derivations" in scenario["action"]:
        execution["input_derivations"] = deepcopy(scenario["action"]["derivations"])
    return {"execution": execution, "observation": None, "result": result}


def run_acceptance(scenarios, *, base_url=None, recorder=None, repository_root=None,
                   registry=None, coverage_authorizations=None) -> dict:
    """Validate all inputs before execution; return {verdict, results} in order.

    Accept a list of at most five grounded scenarios. No planning, grounding,
    reasoning, substitution, retries, or individual verdict calculation occurs.
    Missing/blank/non-string HTTP target configuration yields an unobserved
    verifier result. Other target-policy decisions belong to the HTTP executor.
    Executor exceptions propagate rather than silently dropping scenarios.
    Inputs are read only; existing envelopes are retained without copying logs.
    Registered checks require caller-supplied repository_root, registry, and
    coverage_authorizations. Missing/mismatched association prevents execution.
    """
    if not isinstance(scenarios, list) or len(scenarios) > MAX_SCENARIOS:
        raise ValueError(f"scenarios must be a list of at most {MAX_SCENARIOS} entries")
    for scenario in scenarios:
        validate_scenario(scenario)
    scenarios = deepcopy(scenarios)
    # Also validate the snapshot before side effects; no caller-owned child data
    # is used during dispatch. Concurrent mutation during copying is not supported.
    for scenario in scenarios:
        validate_scenario(scenario)
    results = []
    for scenario in scenarios:
        kind = scenario["action"]["type"]
        if kind == "composite":
            envelope = _execute_composite(scenario, base_url)
        elif kind == "http_sequence":
            envelope = execute_http_sequence(scenario, base_url=base_url)
        elif kind == "http_request":
            if not isinstance(base_url, str) or not base_url.strip():
                envelope = _unobserved(scenario, "HTTP target configuration is unavailable")
            else:
                envelope = execute_http_scenario(scenario, base_url=base_url)
        elif kind == "test_command":
            envelope = execute_test_scenario(scenario, recorder=recorder)
        elif kind == "registered_check":
            check = authorized_registration(scenario, registry, coverage_authorizations)
            observation = None
            if repository_root is not None and check is not None:
                observation = execute_registered_check(
                    scenario, repository_root=repository_root, registry=registry)
            result = verify_observation(scenario, observation, registry=registry,
                                        coverage_authorizations=coverage_authorizations)
            envelope = {'execution': {
                'established': observation is not None and observation.get('status') in
                    ('success', 'assertion_failure', 'test_error', 'skipped',
                     'expected_failure', 'unexpected_success'),
                'status': observation.get('status') if observation else 'not_executed',
                'check_id': scenario['action']['check_id'],
                'coverage_id': check.coverage.id if check else None,
                'coverage_authorized': check is not None,
                'reason': result['reason'],
            }, 'observation': observation, 'result': result}
        else:
            envelope = _unobserved(scenario)
        verdict = envelope["result"]["verdict"]
        if verdict not in ("PASS", "FAIL", "UNVERIFIED"):
            raise ValueError("Executor returned an unknown verdict")
        results.append(envelope)
    verdicts = [envelope["result"]["verdict"] for envelope in results]
    overall = ("FAIL" if "FAIL" in verdicts else
               "UNVERIFIED" if not verdicts or "UNVERIFIED" in verdicts else "PASS")
    return {"verdict": overall, "results": results}


def _execute_composite(scenario, base_url):
    """Independent required leaves, no state transfer or isolation guarantee."""
    children = []
    child_results = []
    for child in scenario['action']['children']:
        leaf = dict(name=child['label'], source=scenario['source'],
                    reason=scenario['reason'], action=deepcopy(child['action']))
        if 'assertions' in child:
            leaf['assertions'] = deepcopy(child['assertions'])
        if leaf['action']['type'] == 'unsupported':
            envelope = _unobserved(leaf)
        elif not isinstance(base_url, str) or not base_url.strip():
            envelope = _unobserved(leaf, 'HTTP target configuration is unavailable')
        else:
            envelope = execute_http_scenario(leaf, base_url=base_url)
        verdict = envelope['result']['verdict']
        child_results.append(dict(label=child['label'], verdict=verdict))
        # Keep the existing leaf envelope exactly once; the parent has no raw JSON.
        children.append(dict(label=child['label'], **envelope))
    verdict = aggregate_composite_results(scenario, child_results)
    counts = dict(required=len(children), **{
        label: sum(item['verdict'] == value for item in child_results)
        for label, value in (('pass', 'PASS'), ('fail', 'FAIL'), ('unverified', 'UNVERIFIED'))})
    result = dict(name=scenario['name'], source=scenario['source'],
                  reason=scenario['reason'], behavior=scenario['behavior'],
                  verdict=verdict, assertions=[], child_counts=counts, children=children)
    return dict(execution=dict(kind='composite', required=len(children)),
                observation=None, result=result)
