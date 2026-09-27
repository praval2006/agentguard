"""Replay saved grounded scenarios: python3 -m evaluation.day5c_execute."""

import json
from pathlib import Path

from agentguard.acceptance import run_acceptance
from sample_app.subscription_http import subscription_server


def main():
    path = Path(__file__).with_name("day5c_grounded_scenarios.json")
    scenarios = json.loads(path.read_text(encoding="utf-8"))
    with subscription_server() as base_url:
        result = run_acceptance(scenarios, base_url=base_url)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
