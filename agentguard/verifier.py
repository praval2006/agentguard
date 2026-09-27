"""Deterministic assertion core for supplied observations; no execution or I/O."""

from math import isfinite

from .scenarios import validate_scenario

MAX_EVIDENCE_CHARS = 512
MAX_JSON_NODES = 10_000
MAX_JSON_DEPTH = 32
MAX_JSON_TEXT_CHARS = 32_000


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


def verify_observation(scenario: dict, observation=None) -> dict:
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
    Comparisons use complete values before evidence truncation. Input is unchanged.
    """
    validate_scenario(scenario)
    result = {"name": scenario["name"], "source": scenario["source"],
              "verdict": "UNVERIFIED", "assertions": [], "reason": None}
    kind = scenario["action"]["type"]
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
