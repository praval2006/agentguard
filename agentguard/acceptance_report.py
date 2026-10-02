"""Deterministic projection of a completed reviewed workflow; no verification."""
import json

from .acceptance_contract import create_proposal, build_contract
from .scenarios import validate_scenario

SCHEMA = 'agentguard.acceptance-report.v1'
MAX_REPORT_BYTES = 1_048_576
VERDICTS = ('PASS', 'FAIL', 'UNVERIFIED')
BOUNDARY = {
    'PASS': 'Observed evidence matched the accepted behavior.',
    'FAIL': 'Observed evidence contradicted the accepted behavior.',
    'UNVERIFIED': 'AgentGuard could not establish the behavior with its supported observations.',
    'limitations': [
        'The report does not establish complete software correctness.',
        'Unsupported behavior may remain UNVERIFIED.',
        'Dismissed and pending suggestions were not verified.',
        'Ambiguity is not automatically treated as failure.',
        'Report generation does not perform verification.',
        'Planner rationale is interpretation, not observed evidence.',
    ],
}


def report_json(report):
    """Stable bounded JSON; no truncation, file access or model invocation."""
    encoder = json.JSONEncoder(ensure_ascii=True, allow_nan=False, sort_keys=True, indent=2)
    chunks = []
    size = 1
    try:
        for chunk in encoder.iterencode(report):
            size += len(chunk.encode('utf-8'))
            if size > MAX_REPORT_BYTES:
                raise ValueError('Report exceeds serialization bound')
            chunks.append(chunk)
    except (TypeError, RecursionError) as error:
        raise ValueError('Report must be bounded JSON') from error
    return ''.join(chunks) + '\n'


def _same(left, right):
    return report_json(left) == report_json(right)


def _require(condition, message):
    if not condition:
        raise ValueError('Report input: ' + message)


def _result(scenario, envelope, *, nested=False):
    _require(type(envelope) is dict and type(envelope.get('result')) is dict,
             'missing result envelope')
    result = envelope['result']
    _require(result.get('name') == scenario['name'] and result.get('source') == scenario['source'],
             'result identity/order mismatch')
    _require(result.get('verdict') in VERDICTS and type(result.get('assertions')) is list
             and 'reason' in result, 'malformed result')
    _require(all(type(a) is dict and a.get('verdict') in VERDICTS
                 and type(a.get('type')) is str for a in result['assertions']),
             'malformed assertion evidence')
    # Results are authoritative, not re-evaluated. Only known selected evidence
    # fields are reportable; raw observations and request payloads are excluded.
    allowed = {'name', 'source', 'verdict', 'assertions', 'reason', 'expected', 'observed',
               'expected_truncated', 'observed_truncated', 'behavior', 'child_counts', 'children',
               'check_id', 'coverage_id', 'coverage_authorized', 'execution_status', 'tests_run',
               'failures', 'errors', 'skips', 'expected_failures', 'unexpected_successes'}
    _require(not result.keys() - allowed, 'unknown result fields')
    projected = {k: v for k, v in result.items() if k != 'children'}
    kind = scenario['action']['type']
    if kind in ('composite', 'http_sequence'):
        _require(not nested, 'unexpected nested action')
        specs = scenario['action']['children' if kind == 'composite' else 'steps']
        children = result.get('children')
        _require(type(children) is list and len(children) == len(specs), 'child count mismatch')
        projected['children'] = []
        for spec, child in zip(specs, children):
            label = spec['label' if kind == 'composite' else 'name']
            _require(type(child) is dict and child.get('label') == label, 'child identity/order mismatch')
            leaf = dict(name=label, source=scenario['source'], reason=scenario['reason'], action=spec['action'])
            item = dict(label=label, result=_result(leaf, child, nested=True))
            if 'execution' in child:
                item['execution'] = _execution(child['execution'])
            projected['children'].append(item)
    else:
        _require('children' not in result, 'unexpected child results')
    return projected


def _execution(value):
    _require(type(value) is dict, 'invalid execution metadata')
    # Existing executor metadata only. Do not export raw observations, logs,
    # request bodies, headers, variables or full response JSON.
    allowed = {'established', 'reason', 'reason_truncated', 'method', 'status', 'body_truncated',
               'json_available', 'command', 'returncode', 'timed_out', 'output_truncated',
               'input_derivations', 'kind', 'required', 'steps', 'stopped_on_nonpass', 'name',
               'check_id', 'coverage_id', 'coverage_authorized'}
    _require(not value.keys() - allowed, 'unknown execution metadata')
    if 'steps' in value:
        _require(type(value['steps']) is list and len(value['steps']) <= 4, 'invalid execution steps')
        for step in value['steps']:
            _require(type(step) is dict and 'steps' not in step, 'nested execution metadata')
            _execution(step)
    return value


def build_acceptance_report(outcome, *, task_text=None):
    """Join the trusted resume_reviewed return using its guaranteed positional order.

    Revalidate proposal/review identities, then check the selected/grounded/result
    alignment. This detects structural mixups, not falsification or semantically
    different same-name/source results. Original task text is optional caller data,
    NOT bound by the current proposal revision. No verifier or executor is called.
    """
    _require(type(outcome) is dict and set(outcome) == {
        'revision', 'proposal', 'contract', 'grounded', 'verification'}, 'invalid workflow fields')
    _require(task_text is None or (type(task_text) is str and bool(task_text.strip())
                                  and len(task_text) <= 32000), 'invalid task text')
    proposal = create_proposal(outcome['proposal'])
    _require(outcome['revision'] == proposal.revision, 'revision mismatch')
    contract = outcome['contract']
    _require(type(contract) is dict and type(contract.get('reviews')) is list, 'invalid contract')
    decisions = []
    for review in contract['reviews']:
        _require(type(review) is dict, 'invalid review')
        if review.get('source') == 'inferred':
            decisions.append(dict(revision=proposal.revision, scenario_id=review.get('scenario_id'),
                                  state=review.get('review_state')))
    _require(_same(contract, build_contract(proposal, decisions)), 'inconsistent reviewed contract')
    selected = [r for r in contract['reviews'] if r['included']]
    grounded = outcome['grounded']
    verification = outcome['verification']
    _require(type(verification) is dict and set(verification) == {'verdict', 'results'}
             and verification['verdict'] in VERDICTS, 'invalid verification summary')
    results = verification['results']
    _require(type(grounded) is list and type(results) is list
             and len(selected) == len(grounded) == len(results), 'selected result count mismatch')
    entries = []
    for review, scenario, envelope in zip(selected, grounded, results):
        validate_scenario(scenario)
        _require(all(scenario[k] == review[k] for k in ('name', 'source', 'reason')),
                 'grounded identity/order mismatch')
        if 'behavior' in scenario:
            _require(scenario['behavior'] == review['behavior'], 'grounded behavior mismatch')
        _require(type(envelope) is dict, 'invalid execution envelope')
        execution = _execution(envelope.get('execution'))
        if scenario['action']['type'] == 'http_sequence':
            names = [s['name'] for s in scenario['action']['steps']]
            _require(type(execution.get('steps')) is list and
                     [s.get('name') for s in execution['steps']] == names[:len(execution['steps'])],
                     'execution observation order mismatch')
        entries.append(dict(scenario_id=review['scenario_id'], position=review['position'],
                            action_type=scenario['action']['type'],
                            execution=execution,
                            result=_result(scenario, envelope)))
    reviews = contract['reviews']
    summary = dict(overall_verdict=verification['verdict'], selected_scenarios=len(selected),
                   verdict_counts={v: sum(e['result']['verdict'] == v for e in entries) for v in VERDICTS},
                   explicit_scenarios=sum(r['source'] == 'explicit' for r in reviews),
                   accepted_inferred=sum(r['review_state'] == 'ACCEPTED' for r in reviews),
                   dismissed_inferred=sum(r['review_state'] == 'DISMISSED' for r in reviews),
                   pending_inferred=sum(r['review_state'] == 'PENDING' for r in reviews),
                   ambiguities=len(outcome['proposal']['ambiguities']))
    report = dict(schema=SCHEMA, revision=proposal.revision,
                  task=dict(text=task_text, provenance='caller_supplied_unbound' if task_text is not None
                            else 'not_retained_by_reviewed_workflow'),
                  discovery={k: outcome['proposal'][k] for k in
                             ('explicit_requirements', 'inferred_behaviors', 'ambiguities')},
                  requirement_mapping=dict(state='NO_STRUCTURED_SCENARIO_LINKS',
                      explanation='Requirement-list coverage is not established: no requirement-to-scenario IDs are supplied. '
                                  'Items without a scenario are not represented by a verification scenario; no verdict is assigned to list items.'),
                  reviews=reviews, contract=dict(scenarios=selected), summary=summary,
                  verification=dict(overall_verdict=verification['verdict'], results=entries), boundary=BOUNDARY)
    # Finite bounded JSON roundtrip provides a detached, deterministic snapshot.
    return json.loads(report_json(report))


def format_acceptance_report(report):
    """Terminal-friendly projection, escaping all caller/model/evidence strings."""
    def display(value):
        return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True)
    lines = ['AGENTGUARD', 'ACCEPTANCE VERIFICATION REPORT', '', 'Review revision: ' + report['revision'],
             'Task: ' + display(report['task']['text']), 'Task provenance: ' + report['task']['provenance']]
    for field, title in (('explicit_requirements', 'EXPLICIT REQUIREMENTS'),
                         ('inferred_behaviors', 'AGENTGUARD SUGGESTIONS'), ('ambiguities', 'AMBIGUITIES')):
        lines += ['', title + ' (planner interpretation)']
        lines += [display(item) for item in report['discovery'][field]] or ['(none)']
    lines += ['', report['requirement_mapping']['explanation'], '', 'ACCEPTANCE REVIEW']
    for review in report['reviews']:
        lines += [display(review['name']) + ' / ' + ('EXPLICIT' if review['source'] == 'explicit' else 'AGENTGUARD SUGGESTION'),
                  'Decision: ' + (review['review_state'] or 'AUTOMATICALLY INCLUDED'),
                  'Scenario: ' + review['scenario_id'], 'Behavior: ' + display(review['behavior']),
                  'Model rationale (not evidence): ' + display(review['reason']),
                  'Included in verification' if review['included'] else 'Not included in verification']
    lines += ['', 'ACCEPTANCE CONTRACT', f"{report['summary']['selected_scenarios']} behaviors selected"]
    lines += [r['scenario_id'] + ': ' + display(r['name']) for r in report['contract']['scenarios']]
    lines += ['', 'VERIFICATION SUMMARY', 'Overall: ' + report['summary']['overall_verdict']]
    lines += [f"{v}: {report['summary']['verdict_counts'][v]}" for v in VERDICTS]
    for index, entry in enumerate(report['verification']['results'], 1):
        lines += ['', f'RESULT {index:02d}', 'Scenario: ' + entry['scenario_id'],
                  'Action: ' + entry['action_type'], 'Evidence (verifier output):',
                  json.dumps(entry['result'], ensure_ascii=True, allow_nan=False, indent=2),
                  'Execution metadata: ' + display(entry['execution'])]
    lines += ['', 'VERIFICATION BOUNDARY']
    lines += [v + ': ' + report['boundary'][v] for v in VERDICTS]
    lines += report['boundary']['limitations']
    return '\n'.join(lines)
