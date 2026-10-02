"""Deterministic assertion core for supplied observations; no execution or I/O."""

from math import isfinite

from .scenarios import validate_scenario, sequence_leaf

MAX_EVIDENCE_CHARS = 512
MAX_JSON_NODES = 10_000
MAX_JSON_DEPTH = 32
MAX_JSON_TEXT_CHARS = 32_000


def aggregate_composite_results(scenario, child_results):
    """Pure aggregation of exact ordered {label, verdict} records.

    Requires the validated frozen parent to detect missing/duplicate/reordered
    children. Malformed input raises ValueError, never a vacuous PASS. Verdicts
    are caller-supplied evidence; this helper neither executes nor authenticates.
    """
    validate_scenario(scenario)
    if scenario['action']['type'] != 'composite':
        raise ValueError('composite scenario required')
    children = scenario['action']['children']
    if type(child_results) is not list or len(child_results) != len(children):
        raise ValueError('one result per required child is required')
    verdicts = []
    for child, result in zip(children, child_results):
        if type(result) is not dict or set(result) != {'label', 'verdict'}:
            raise ValueError('child result must contain exactly label and verdict')
        if type(result['label']) is not str or result['label'] != child['label']:
            raise ValueError('child identity/order mismatch')
        if type(result['verdict']) is not str or result['verdict'] not in ('PASS', 'FAIL', 'UNVERIFIED'):
            raise ValueError('unknown child verdict')
        verdicts.append(result['verdict'])
    return ('FAIL' if 'FAIL' in verdicts else
            'UNVERIFIED' if 'UNVERIFIED' in verdicts else 'PASS')


def _json_available(value):
    # Iterative, bounded traversal rejects cycles, non-JSON objects and nonfinite numbers.
    pending = [(value, 0)]
    nodes = text = 0
    while pending:
        item, depth = pending.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
            return False
        kind = type(item)
        if kind is str:
            text += len(item)
        elif kind is float:
            if not isfinite(item):
                return False
        elif kind in (int, bool) or item is None:
            pass
        elif kind is dict:
            if len(item) + len(pending) + nodes > MAX_JSON_NODES:
                return False
            for key, child in item.items():
                if type(key) is not str:
                    return False
                text += len(key)
                pending.append((child, depth + 1))
        elif kind is list:
            if len(item) + len(pending) + nodes > MAX_JSON_NODES:
                return False
            pending.extend((child, depth + 1) for child in item)
        else:
            return False
        if text > MAX_JSON_TEXT_CHARS:
            return False
    return True


def _evidence(result, key, value):
    if type(value) is str and len(value) > MAX_EVIDENCE_CHARS:
        result[key] = value[:MAX_EVIDENCE_CHARS]
        result[key + "_truncated"] = True
    elif type(value) in (dict, list):
        # Containers contradict scalar expectations; do not copy unrelated nested data.
        result[key + "_type"] = "object" if type(value) is dict else "array"
    else:
        result[key] = value


def _equal(expected, observed):
    # JSON booleans are distinct from numbers; integer and float are one numeric category.
    if type(expected) in (int, float) and type(observed) in (int, float):
        return expected == observed
    return type(expected) is type(observed) and expected == observed


def verify_observation(scenario: dict, observation=None, *, registry=None,
                       coverage_authorizations=None) -> dict:
    """Validate scenario first, then return name/source/verdict/assertions/reason.

    Observations are exact plain dictionaries:
    HTTP: type='http_response', status=int 100..599, optional parsed json.
    Command: type='test_result', returncode=int (booleans excluded).
    No extra envelope fields are accepted. Invalid HTTP status/type/envelope means
    the response is not established. Invalid/oversized optional JSON makes only
    JSON assertions unobservable; valid status evidence is retained.

    Assertion results contain type, optional path, expected, verdict, reason,
    and observed when available (null is preserved). Long evidence strings have
    a *_truncated flag; container observations have observed_type only. Command
    results instead add expected=0 and observed when a valid return code exists.
    Unsupported explanations are preserved as reason. No full response, headers,
    output logs, variables or request payloads are copied into results.

    Caller must supply genuine observations associated with this scenario. This
    core validates representation, not provenance or whether execution occurred.
    Registered checks additionally require separately supplied Registry and
    CoverageAuthorizations objects. These are trusted caller inputs, not model
    data; coverage association is not semantic completeness or source freshness.
    Comparisons use complete values before evidence truncation. Input is unchanged.
    """
    validate_scenario(scenario)
    if scenario['action']['type'] == 'http_sequence':
        return _verify_sequence(scenario, observation)
    return _verify_leaf(scenario, observation, registry, coverage_authorizations)


def _verify_leaf(scenario, observation, registry=None, coverage_authorizations=None):
    result = {"name": scenario["name"], "source": scenario["source"],
              "verdict": "UNVERIFIED", "assertions": [], "reason": None}
    kind = scenario["action"]["type"]
    if kind == "registered_check":
        return _verify_registered(scenario, observation, result, registry,
                                  coverage_authorizations)
    if kind == "unsupported":
        result["reason"] = scenario["action"]["explanation"]
        return result
    if kind == "test_command":
        result["expected"] = 0
        if (type(observation) is not dict or set(observation) != {"type", "returncode"}
                or type(observation["type"]) is not str
                or observation["type"] != "test_result"
                or type(observation["returncode"]) is not int):
            result["reason"] = "Missing or malformed test-result observation"
        else:
            result["observed"] = observation["returncode"]
            result["verdict"] = "PASS" if observation["returncode"] == 0 else "FAIL"
        return result

    valid_response = (type(observation) is dict
                      and {"type", "status"} <= observation.keys()
                      and not observation.keys() - {"type", "status", "json"}
                      and type(observation["type"]) is str
                      and observation["type"] == "http_response"
                      and type(observation["status"]) is int
                      and 100 <= observation["status"] <= 599)
    json_available = (valid_response and "json" in observation
                      and _json_available(observation["json"]))
    for assertion in scenario["assertions"]:
        if assertion["type"] in ("json_exists", "json_type"):
            result["assertions"].append(_verify_json_shape(
                assertion, observation, valid_response, json_available))
            continue
        item = {"type": assertion["type"], "verdict": "UNVERIFIED", "reason": None}
        _evidence(item, "expected", assertion["equals"])
        if assertion["type"] == "json_field":
            item["path"] = assertion["path"]
        available = False
        if not valid_response:
            item["reason"] = "Missing or malformed HTTP-response observation"
        elif assertion["type"] == "status":
            observed = observation["status"]
            available = True
        elif not json_available:
            item["reason"] = "Parsed JSON unavailable, invalid, or exceeds observation bounds"
        else:
            observed = observation["json"]
            available = True
            for segment in assertion["path"].split("."):
                if type(observed) is not dict or segment not in observed:
                    available = False
                    item["reason"] = "JSON field path is not observable"
                    break
                observed = observed[segment]
        if available:
            item["verdict"] = "PASS" if _equal(assertion["equals"], observed) else "FAIL"
            _evidence(item, "observed", observed)
        result["assertions"].append(item)
    verdicts = [item["verdict"] for item in result["assertions"]]
    if "FAIL" in verdicts:
        result["verdict"] = "FAIL"
    elif "UNVERIFIED" in verdicts:
        result["reason"] = "One or more required assertions lack sufficient observation"
    else:
        result["verdict"] = "PASS"
    return result


def _verify_json_shape(assertion, observation, valid_response, json_available):
    """Report presence/types only, never selected values. Parsed-value semantics:
    integral finite floats count as integers; no lexical precision claim is made.
    Missing paths contradict existence but leave type unobservable.
    """
    kind = assertion['type']
    item = dict(type=kind, verdict='UNVERIFIED', reason=None)
    _evidence(item, 'path', assertion['path'])
    if kind == 'json_type':
        item['expected'] = assertion['equals']
    if not valid_response:
        item['reason'] = 'Missing or malformed HTTP-response observation'
        return item
    if not json_available:
        item['reason'] = 'Parsed JSON unavailable, invalid, or exceeds observation bounds'
        return item
    value = observation['json']
    present = True
    for segment in assertion['path'].split('.'):
        if type(value) is not dict or segment not in value:
            present = False
            break
        value = value[segment]
    if kind == 'json_exists':
        item.update(observed=present, verdict='PASS' if present else 'FAIL')
        if not present:
            item['reason'] = 'Requested JSON field is absent'
        return item
    if not present:
        item['reason'] = 'JSON field path is not observable'
        return item
    if value is None: observed_type = 'null'
    elif type(value) is bool: observed_type = 'boolean'
    elif type(value) is str: observed_type = 'string'
    elif type(value) is dict: observed_type = 'object'
    elif type(value) is list: observed_type = 'array'
    elif type(value) is int or value.is_integer(): observed_type = 'integer'
    else: observed_type = 'number'
    matches = assertion['equals'] == observed_type or (
        assertion['equals'] == 'number' and observed_type == 'integer')
    item.update(observed_type=observed_type, verdict='PASS' if matches else 'FAIL')
    return item


def _verify_registered(scenario, observation, result, registry, authorizations):
    from .coverage_authorization import authorized_registration
    check = authorized_registration(scenario, registry, authorizations)
    result.update(check_id=scenario['action']['check_id'], coverage_id=None,
                  coverage_authorized=check is not None)
    if check is None:
        result['reason'] = 'Missing or mismatched trusted coverage authorization'
        return result
    result['coverage_id'] = check.coverage.id
    counts = ('tests_run', 'failures', 'errors', 'skips', 'expected_failures', 'unexpected_successes')
    keys = {'check_id', 'coverage_id', 'target', 'status', 'returncode', 'timed_out',
            'output_truncated', *counts}
    result['reason'] = 'Missing, malformed, or nonconclusive registered-check observation'
    if type(observation) is not dict or set(observation) != keys:
        return result
    if (observation['check_id'] != check.id or observation['coverage_id'] != check.coverage.id
            or observation['target'] != check.target
            or type(observation['timed_out']) is not bool
            or type(observation['output_truncated']) is not bool):
        return result
    statuses = {'success', 'assertion_failure', 'test_error', 'load_error', 'skipped',
                'expected_failure', 'unexpected_success', 'zero_tests', 'multiple_tests',
                'malformed_result', 'process_crash', 'timeout', 'unknown_check',
                'configuration_error', 'execution_error'}
    if type(observation['status']) is not str or observation['status'] not in statuses:
        return result
    result['execution_status'] = observation['status']
    if (observation['timed_out'] or type(observation['returncode']) is not int
            or observation['returncode'] != 0
            or any(type(observation[k]) is not int or not 0 <= observation[k] <= 1000000 for k in counts)
            or observation['tests_run'] != 1):
        return result
    for key in counts:
        result[key] = observation[key]
    if any(observation[k] for k in counts[2:]):
        return result
    if observation['status'] == 'success' and observation['failures'] == 0:
        result.update(verdict='PASS', reason='Authorized check completed one successful test')
    elif observation['status'] == 'assertion_failure' and observation['failures'] > 0:
        result.update(verdict='FAIL', reason='Authorized check observed an assertion failure')
    return result


def _verify_sequence(scenario, observation):
    """Verify an ordered observation prefix, never model-supplied verdicts."""
    steps = scenario['action']['steps']
    valid = (type(observation) is dict and set(observation) == {'type', 'steps'}
             and observation['type'] == 'http_sequence_result'
             and type(observation['steps']) is list
             and len(observation['steps']) <= len(steps))
    records = observation['steps'] if valid else []
    if any(type(record) is not dict or set(record) != {'name', 'observation'}
           or record['name'] != step['name'] for record, step in zip(records, steps)):
        records = []
    captured = {}
    children = []
    continuing = True
    for index, step in enumerate(steps):
        observed = records[index]['observation'] if continuing and index < len(records) else None
        result = _verify_leaf(sequence_leaf(scenario, step), observed)
        # Only successful required steps expose scalar values to later comparisons.
        if result['verdict'] == 'PASS':
            captured[step['name']] = observed
        else:
            continuing = False
        children.append(dict(label=step['name'], result=result))
    assertions = []
    for assertion in scenario['assertions']:
        item = dict(type='json_equal', left=dict(assertion['left']), right=dict(assertion['right']),
                    verdict='UNVERIFIED', reason=None)
        left_ok, left = _sequence_value(captured, assertion['left'])
        right_ok, right = _sequence_value(captured, assertion['right'])
        if right_ok:
            _evidence(item, 'expected', right)
        if left_ok:
            _evidence(item, 'observed', left)
        if left_ok and right_ok:
            item['verdict'] = 'PASS' if _equal(right, left) else 'FAIL'
        else:
            item['reason'] = 'Required named observation or scalar JSON path is unavailable'
        assertions.append(item)
    verdicts = [c['result']['verdict'] for c in children] + [a['verdict'] for a in assertions]
    verdict = ('FAIL' if 'FAIL' in verdicts else
               'UNVERIFIED' if 'UNVERIFIED' in verdicts else 'PASS')
    return dict(name=scenario['name'], source=scenario['source'], verdict=verdict,
                assertions=assertions, children=children,
                reason='Required sequence evidence is unavailable' if verdict == 'UNVERIFIED' else None)


def _sequence_value(captured, reference):
    observation = captured.get(reference['observation'])
    if (observation is None or 'json' not in observation
            or not _json_available(observation['json'])):
        return False, None
    value = observation['json']
    for segment in reference['path'].split('.'):
        if type(value) is not dict or segment not in value:
            return False, None
        value = value[segment]
    # Collection comparison is deliberately not part of this primitive.
    return (False, None) if type(value) in (dict, list) else (True, value)
