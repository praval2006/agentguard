"""Strict MVP scenario dictionaries. Validation only; no execution or substitution.

Common keys: name, source, reason, action; optional variables.
HTTP actions require a nonempty assertions list. Other actions forbid assertions.
Unsupported actions are descriptive records, never executable actions or verdicts.
"""

from math import isfinite


def _shape(value, required, optional, location):
    if not isinstance(value, dict):
        raise ValueError(f"{location} must be a dictionary")
    if not required <= value.keys() or value.keys() - required - optional:
        raise ValueError(f"{location} has missing or unexpected fields")


def _text(value, location):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} must be a nonempty string")


def validate_scenario(scenario: dict) -> None:
    """Return None for a valid scenario; raise ValueError otherwise, without mutation.

    HTTP action: type=http_request, method, path; optional json dict and string
    headers dict. Assertions: status/equals or json_field/path/equals. Dotted
    field paths have nonblank segments; no expression or array-path language.
    Scalar equals values are strings, finite floats, integers, booleans or None.

    Test action: type=test_command, command (nonempty list of nonempty strings).
    This validates representation, not command safety or availability.
    Unsupported action: type=unsupported, explanation (nonempty string).
    Variables require only a dict with nonblank string keys; values are opaque.
    Request json requires a dict; payload content is not interpreted here.
    """
    _shape(scenario, {"name", "source", "reason", "action"},
           {"assertions", "variables"}, "scenario")
    for field in ("name", "reason"):
        _text(scenario[field], field)
    if scenario["source"] not in ("explicit", "inferred"):
        raise ValueError("source must be explicit or inferred")
    if "variables" in scenario:
        if not isinstance(scenario["variables"], dict):
            raise ValueError("variables must be a dictionary")
        for key in scenario["variables"]:
            _text(key, "variable name")

    action = scenario["action"]
    if not isinstance(action, dict):
        raise ValueError("action must be a dictionary")
    kind = action.get("type")
    if kind == "http_request":
        _shape(action, {"type", "method", "path"}, {"json", "headers"}, "action")
        if action["method"] not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            raise ValueError("action.method is not a supported HTTP method")
        _text(action["path"], "action.path")
        if not action["path"].startswith("/"):
            raise ValueError("action.path must begin with /")
        if "json" in action and not isinstance(action["json"], dict):
            raise ValueError("action.json must be a dictionary")
        if "headers" in action:
            headers = action["headers"]
            if not isinstance(headers, dict) or any(
                not isinstance(k, str) or not isinstance(v, str)
                for k, v in headers.items()
            ):
                raise ValueError("action.headers must contain string keys and values")
        assertions = scenario.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            raise ValueError("HTTP scenarios require a nonempty assertions list")
        for assertion in assertions:
            _validate_assertion(assertion)
    elif kind == "test_command":
        _shape(action, {"type", "command"}, set(), "action")
        command = action["command"]
        if not isinstance(command, list) or not command:
            raise ValueError("action.command must be a nonempty argument list")
        for argument in command:
            _text(argument, "command argument")
        if "assertions" in scenario:
            raise ValueError("test_command scenarios must not contain assertions")
    elif kind == "unsupported":
        _shape(action, {"type", "explanation"}, set(), "action")
        _text(action["explanation"], "action.explanation")
        if "assertions" in scenario:
            raise ValueError("unsupported scenarios must not contain assertions")
    else:
        raise ValueError("unknown action type")


def _validate_assertion(assertion):
    if not isinstance(assertion, dict):
        raise ValueError("assertion must be a dictionary")
    kind = assertion.get("type")
    if kind == "status":
        _shape(assertion, {"type", "equals"}, set(), "status assertion")
        value = assertion["equals"]
        if type(value) is not int or not 100 <= value <= 599:
            raise ValueError("status equals must be an integer from 100 through 599")
    elif kind == "json_field":
        _shape(assertion, {"type", "path", "equals"}, set(), "json_field assertion")
        path = assertion["path"]
        _text(path, "json_field.path")
        if any(not part.strip() for part in path.split(".")):
            raise ValueError("json_field.path must have nonempty dotted segments")
        value = assertion["equals"]
        if value is not None and type(value) not in (str, int, float, bool):
            raise ValueError("json_field.equals must be a JSON scalar")
        if type(value) is float and not isfinite(value):
            raise ValueError("json_field.equals must be finite")
    else:
        raise ValueError("unknown assertion type")


def unsupported_scenario(*, name: str, source: str, reason: str,
                         explanation: str) -> dict:
    """Create a validated non-executable record preserving intent and explanation."""
    scenario = {"name": name, "source": source, "reason": reason,
                "action": {"type": "unsupported", "explanation": explanation}}
    validate_scenario(scenario)
    return scenario
