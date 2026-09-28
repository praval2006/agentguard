"""Manual paid reasoning smoke: python3 -m scripts.live_openai_smoke.

Never invoked by tests. Stops after validated planner and grounder output.
"""
import json
import os

from agentguard.grounding import ground_scenarios
from agentguard.planner import plan_acceptance
from agentguard.providers.openai_provider import OpenAIProvider

TASK = (
    'Add a username update feature. A username must be non-empty. '
    'When updated successfully, the API should return the stored username.'
)
REPOSITORY_CONTEXT = '''Fictional interface for this reasoning-only example:
PATCH /profile/username accepts a JSON object containing a username string.
A successful update returns HTTP 200 with a JSON object containing username.
A blank username returns HTTP 400.
'''


def main():
    if not os.environ.get('OPENAI_API_KEY', '').strip():
        raise SystemExit('OPENAI_API_KEY must be configured to run the live smoke.')
    provider = OpenAIProvider()
    planner_output = plan_acceptance(
        TASK, REPOSITORY_CONTEXT, reasoning_provider=provider,
    )
    print('Validated planner output:', flush=True)
    print(json.dumps(planner_output, indent=2), flush=True)
    grounded = ground_scenarios(
        planner_output, REPOSITORY_CONTEXT, grounding_provider=provider,
    )
    print('Validated grounded scenarios:', flush=True)
    print(json.dumps(grounded, indent=2), flush=True)


if __name__ == '__main__':
    main()
