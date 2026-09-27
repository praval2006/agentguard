"""Controlled integration proof. Run: python3 -m agentguard.subscription_demo."""

import json
from pathlib import Path
import tempfile

from sample_app.subscription_http import subscription_server
from .execution import execute_test_scenario
from .http_execution import execute_http_scenario
from .recorder import JSONLRecorder
from .scenarios import unsupported_scenario
from .verifier import verify_observation


def acceptance_scenario():
    """Fresh copy of the frozen agreed check; no inferred or generated routes.

    Cancellation and access expectations come from the original task. The route,
    concrete controlled ID, and HTTP 200 are the demo fixture's explicit interface.
    """
    return {
        "name": "Cancellation removes premium access",
        "source": "explicit",
        "reason": "The original task requires cancellation to leave status cancelled and remove premium access.",
        "action": {"type": "http_request", "method": "POST", "path": "/subscriptions/1/cancel"},
        "assertions": [
            {"type": "status", "equals": 200},
            {"type": "json_field", "path": "status", "equals": "cancelled"},
            {"type": "json_field", "path": "premium_access", "equals": False},
        ],
    }


def run_demo():
    """Run existing tests and one real HTTP acceptance check, returning report data.

    Temporary recording preserves the existing test-tool contract without leaving
    raw test logs in the report. No live planner/grounding provider is involved.
    """
    tests = {"name": "Existing sample-app implementation tests", "source": "explicit",
             "reason": "Show the existing implementation-test baseline without changing it.",
             "action": {"type": "test_command", "command": [
                 "python3", "-m", "unittest", "discover", "-s", "sample_app/tests", "-v"]}}
    with tempfile.TemporaryDirectory(prefix="agentguard-demo-") as directory:
        implementation = execute_test_scenario(tests, recorder=JSONLRecorder(Path(directory) / "events.jsonl"))
    with subscription_server() as base_url:
        acceptance = execute_http_scenario(acceptance_scenario(), base_url=base_url)
    repeated = unsupported_scenario(
        name="Safe repeated cancellation", source="explicit",
        reason="The original task requires repeated cancellation not to crash.",
        explanation="This single-request scenario uses fresh state; repeated cancellation of the same state is not established.",
    )
    return {"scope": "Controlled integration proof, not evidence of general effectiveness.",
            "implementation_tests": implementation["result"],
            "acceptance": acceptance["result"],
            "acceptance_execution": acceptance["execution"],
            "repeated_cancellation": verify_observation(repeated)}


def main():
    print(json.dumps(run_demo(), indent=2))


if __name__ == "__main__":
    main()
