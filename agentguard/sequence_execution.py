"""Bounded ordered requests against one target; no state transfer or retries."""

from copy import deepcopy

from .http_execution import execute_http_scenario
from .scenarios import validate_scenario, sequence_leaf
from .verifier import verify_observation


def execute_http_sequence(scenario, *, base_url=None):
    """Stop after the first non-PASS required step. Never reset target state.

    Existing per-request transport policy and deadlines apply. Captured responses
    are only verifier inputs, never request templates. No rollback or isolation.
    """
    validate_scenario(scenario)
    if scenario['action']['type'] != 'http_sequence':
        raise ValueError('HTTP sequence required')
    scenario = deepcopy(scenario)
    validate_scenario(scenario)
    records = []
    executions = []
    stopped = False
    for step in scenario['action']['steps']:
        leaf = sequence_leaf(scenario, step)
        if not isinstance(base_url, str) or not base_url.strip():
            envelope = dict(execution=dict(established=False,
                reason='HTTP target configuration is unavailable'), observation=None,
                result=verify_observation(leaf))
        else:
            envelope = execute_http_scenario(leaf, base_url=base_url)
        verdict = envelope['result']['verdict']
        if verdict not in ('PASS', 'FAIL', 'UNVERIFIED'):
            raise ValueError('Executor returned an unknown verdict')
        records.append(dict(name=step['name'], observation=deepcopy(envelope['observation'])))
        executions.append(dict(name=step['name'], **envelope['execution']))
        if verdict != 'PASS':
            stopped = True
            break
    observation = dict(type='http_sequence_result', steps=records)
    return dict(execution=dict(kind='http_sequence', steps=executions,
                               stopped_on_nonpass=stopped), observation=observation,
                result=verify_observation(scenario, observation))
