import unittest
from copy import deepcopy
from contextlib import ExitStack
from unittest.mock import patch

from agentguard.verifier import verify_observation, MAX_EVIDENCE_CHARS, MAX_JSON_DEPTH


def status(value=200):
    return {"type": "status", "equals": value}


def field(value="ready", path="item.state"):
    return {"type": "json_field", "path": path, "equals": value}


def http(*assertions):
    return {"name": "Read item", "source": "explicit", "reason": "Requested behavior",
            "action": {"type": "http_request", "method": "GET", "path": "/items/{id}"},
            "assertions": list(assertions) or [status()]}


def command():
    return {"name": "Tests", "source": "inferred", "reason": "Regression coverage",
            "action": {"type": "test_command", "command": ["example-tests"]}}


def response(**kwargs):
    return {"type": "http_response", "status": 200, **kwargs}


class VerifierTests(unittest.TestCase):
    def test_status_pass(self):
        r = verify_observation(http(), response())
        self.assertEqual(r["verdict"], "PASS")
        self.assertEqual(r["assertions"][0]["observed"], 200)

    def test_status_fail(self):
        self.assertEqual(verify_observation(http(), response(status=500))["verdict"], "FAIL")

    def test_json_field_pass(self):
        self.assertEqual(verify_observation(http(field(3, "count")), response(json={"count": 3}))["verdict"], "PASS")

    def test_json_field_fail(self):
        r = verify_observation(http(field()), response(json={"item": {"state": "pending"}}))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["assertions"][0]["expected"], "ready")
        self.assertEqual(r["assertions"][0]["observed"], "pending")

    def test_nested_path(self):
        self.assertEqual(verify_observation(http(field(2, "a.b.c")), response(json={"a": {"b": {"c": 2}}}))["verdict"], "PASS")

    def test_observed_null(self):
        r = verify_observation(http(field(None, "value")), response(json={"value": None}))
        self.assertEqual(r["verdict"], "PASS")
        self.assertIn("observed", r["assertions"][0])
        self.assertIsNone(r["assertions"][0]["observed"])

    def test_missing_field(self):
        r = verify_observation(http(field(None)), response(json={"item": {}}))
        self.assertEqual(r["verdict"], "UNVERIFIED")
        self.assertNotIn("observed", r["assertions"][0])
        self.assertTrue(r["reason"])

    def test_missing_json(self):
        self.assertEqual(verify_observation(http(field()), response())["verdict"], "UNVERIFIED")

    def test_all_assertions_pass(self):
        self.assertEqual(verify_observation(http(status(), field()), response(json={"item": {"state": "ready"}}))["verdict"], "PASS")

    def test_one_assertion_fails(self):
        self.assertEqual(verify_observation(http(status(), field()), response(json={"item": {"state": "other"}}))["verdict"], "FAIL")

    def test_pass_and_unverified(self):
        r = verify_observation(http(status(), field()), response())
        self.assertEqual(r["verdict"], "UNVERIFIED")
        self.assertEqual([a["verdict"] for a in r["assertions"]], ["PASS", "UNVERIFIED"])

    def test_fail_and_unverified(self):
        r = verify_observation(http(status(), field()), response(status=500))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual([a["verdict"] for a in r["assertions"]], ["FAIL", "UNVERIFIED"])

    def test_command_pass(self):
        r = verify_observation(command(), {"type": "test_result", "returncode": 0})
        self.assertEqual(r, {"name": "Tests", "source": "inferred", "verdict": "PASS",
                             "assertions": [], "reason": None, "expected": 0, "observed": 0})

    def test_command_failure(self):
        for code in (1, -9, 127):
            self.assertEqual(verify_observation(command(), {"type": "test_result", "returncode": code})["verdict"], "FAIL")

    def test_invalid_command_observations(self):
        for observation in (None, {}, [], {"type": "test_result"},
                            *({"type": "test_result", "returncode": x} for x in (None, True, False, 0.0, "0", object()))):
            r = verify_observation(command(), observation)
            self.assertEqual(r["verdict"], "UNVERIFIED")
            self.assertNotIn("observed", r)

    def test_unsupported_without_observation(self):
        s = {"name": "Layout", "source": "inferred", "reason": "Visual requirement",
             "action": {"type": "unsupported", "explanation": "No browser capability"}}
        r = verify_observation(s)
        self.assertEqual(r["verdict"], "UNVERIFIED")
        self.assertEqual(r["reason"], s["action"]["explanation"])
        self.assertEqual(verify_observation(s, response()), r)

    def test_invalid_scenario_raises_first(self):
        with self.assertRaises(ValueError): verify_observation({}, None)
        s = http()
        s["action"]["method"] = "EXEC"
        with self.assertRaises(ValueError): verify_observation(s, response())

    def test_wrong_observation_type(self):
        self.assertEqual(verify_observation(http(), {"type": "test_result", "returncode": 0})["verdict"], "UNVERIFIED")
        self.assertEqual(verify_observation(command(), response())["verdict"], "UNVERIFIED")

    def test_inputs_not_mutated_and_deterministic(self):
        s = http(field())
        o = response(json={"item": {"state": "ready"}, "unrelated": "private"})
        before = deepcopy((s, o))
        r = verify_observation(s, o)
        self.assertEqual(r, verify_observation(s, o))
        self.assertEqual((s, o), before)
        self.assertNotIn("private", str(r))

    def test_status_boundaries_and_invalid_status(self):
        for code in (100, 599):
            self.assertEqual(verify_observation(http(status(code)), response(status=code))["verdict"], "PASS")
        for code in (99, 600, True, False, None, 200.0, "200"):
            self.assertEqual(verify_observation(http(), response(status=code))["verdict"], "UNVERIFIED")
        self.assertEqual(verify_observation(http(), {"type": "http_response"})["verdict"], "UNVERIFIED")

    def test_no_array_indexing_or_intermediate_null(self):
        for payload in ({"item": None}, {"item": []}, {"item": "ready"}, None):
            self.assertEqual(verify_observation(http(field()), response(json=payload))["verdict"], "UNVERIFIED")
        self.assertEqual(verify_observation(http(field(3, "items.0")), response(json={"items": [3]}))["verdict"], "UNVERIFIED")

    def test_boolean_numeric_equality(self):
        for expected, observed in ((True, 1), (False, 0), (1, True), (0, False), (None, False)):
            self.assertEqual(verify_observation(http(field(expected, "v")), response(json={"v": observed}))["verdict"], "FAIL")
        self.assertEqual(verify_observation(http(field(1, "v")), response(json={"v": 1.0}))["verdict"], "PASS")

    def test_container_is_observed_contradiction_without_copying_contents(self):
        for value in ({"secret": "private"}, ["private"]):
            r = verify_observation(http(field("scalar", "v")), response(json={"v": value}))
            self.assertEqual(r["verdict"], "FAIL")
            self.assertIn("observed_type", r["assertions"][0])
            self.assertNotIn("private", str(r))

    def test_malformed_json_preserves_status_evidence(self):
        cycle = {}; cycle["self"] = cycle
        for payload in ({"v": object()}, {1: "x"}, {"v": float("nan")}, {"v": float("inf")}, cycle):
            r = verify_observation(http(status(), field()), response(status=500, json=payload))
            self.assertEqual(r["verdict"], "FAIL")
            self.assertEqual(r["assertions"][1]["verdict"], "UNVERIFIED")

    def test_strict_envelopes(self):
        for s, o in ((http(), {**response(), "error": "timeout"}),
                     (command(), {"type": "test_result", "returncode": 0, "output": "private"})):
            self.assertEqual(verify_observation(s, o)["verdict"], "UNVERIFIED")

    def test_evidence_truncation_does_not_change_comparison(self):
        expected = "x" * (MAX_EVIDENCE_CHARS + 1)
        r = verify_observation(http(field(expected, "v")), response(json={"v": expected + "y"}))
        a = r["assertions"][0]
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(a["expected_truncated"] and a["observed_truncated"])
        self.assertEqual(len(a["observed"]), MAX_EVIDENCE_CHARS)

    def test_json_bounds(self):
        deep = {}
        for _ in range(MAX_JSON_DEPTH + 1): deep = {"v": deep}
        for payload in (deep, {"v": "x" * 32001}, [0] * 10001):
            self.assertEqual(verify_observation(http(field()), response(json=payload))["verdict"], "UNVERIFIED")

    def test_no_external_access(self):
        with ExitStack() as stack:
            for name in ("builtins.open", "pathlib.Path.open", "subprocess.run", "subprocess.Popen", "socket.socket", "os.getenv", "os.system"):
                stack.enter_context(patch(name, side_effect=AssertionError("external access")))
            self.assertEqual(verify_observation(http(), response())["verdict"], "PASS")
            self.assertEqual(verify_observation(command(), {"type": "test_result", "returncode": 0})["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
