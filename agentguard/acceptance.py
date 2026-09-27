"""Deterministic dispatch and aggregation of already-grounded scenarios."""

from .execution import execute_test_scenario
from .http_execution import execute_http_scenario
from .planner import MAX_SCENARIOS
from .scenarios import validate_scenario
from .verifier import MAX_EVIDENCE_CHARS, verify_observation


def _unobserved(scenario, reason=None):
    result = verify_observation(scenario)
    execution_reason = reason if reason is not None else result["reason"]
    execution = {"established": False, "reason": execution_reason[:MAX_EVIDENCE_CHARS]}
    if len(execution_reason) > MAX_EVIDENCE_CHARS:
        execution["reason_truncated"] = True
    return {"execution": execution, "observation": None, "result": result}


def run_acceptance(scenarios, *, base_url=None, recorder=None) -> dict:
    """Validate all inputs before execution; return {verdict, results} in order.

    Accept a list of at most five grounded scenarios. No planning, grounding,
    reasoning, substitution, retries, or individual verdict calculation occurs.
    Missing/blank/non-string HTTP target configuration yields an unobserved
    verifier result. Other target-policy decisions belong to the HTTP executor.
    Executor exceptions propagate rather than silently dropping scenarios.
    Inputs are read only; existing envelopes are retained without copying logs.
    """
    if not isinstance(scenarios, list) or len(scenarios) > MAX_SCENARIOS:
        raise ValueError(f"scenarios must be a list of at most {MAX_SCENARIOS} entries")
    for scenario in scenarios:
        validate_scenario(scenario)
    results = []
    for scenario in scenarios:
        kind = scenario["action"]["type"]
        if kind == "http_request":
            if not isinstance(base_url, str) or not base_url.strip():
                envelope = _unobserved(scenario, "HTTP target configuration is unavailable")
            else:
                envelope = execute_http_scenario(scenario, base_url=base_url)
        elif kind == "test_command":
            envelope = execute_test_scenario(scenario, recorder=recorder)
        else:  # validate_scenario permits only unsupported as the remaining variant.
            envelope = _unobserved(scenario)
        verdict = envelope["result"]["verdict"]
        if verdict not in ("PASS", "FAIL", "UNVERIFIED"):
            raise ValueError("Executor returned an unknown verdict")
        results.append(envelope)
    verdicts = [envelope["result"]["verdict"] for envelope in results]
    overall = ("FAIL" if "FAIL" in verdicts else
               "UNVERIFIED" if not verdicts or "UNVERIFIED" in verdicts else "PASS")
    return {"verdict": overall, "results": results}
