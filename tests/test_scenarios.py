import unittest
from copy import deepcopy

from agentguard.scenarios import unsupported_scenario, validate_scenario


def http():
    return {"name": "Read report", "source": "explicit", "reason": "Requested report access",
            "action": {"type": "http_request", "method": "GET", "path": "/reports/1"},
            "assertions": [{"type": "status", "equals": 200}]}


def command():
    return {"name": "Existing tests", "source": "inferred", "reason": "Regression coverage",
            "action": {"type": "test_command",
                       "command": ["python3", "-m", "unittest", "tests.test_example"]}}


class ScenarioTests(unittest.TestCase):
    def reject(self, scenario):
        with self.assertRaises(ValueError):
            validate_scenario(scenario)

    def test_valid_http_status(self):
        for method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            for status in (100, 200, 599):
                s = http()
                s["action"]["method"] = method
                s["assertions"][0]["equals"] = status
                self.assertIsNone(validate_scenario(s))

    def test_valid_json_scalars(self):
        for value in ("ready", "", 0, -2, 1.5, True, False, None):
            s = http()
            s["assertions"].append({"type": "json_field", "path": "report.state", "equals": value})
            self.assertIsNone(validate_scenario(s))

    def test_placeholders_and_opaque_variables_without_mutation(self):
        s = http()
        s["action"]["path"] = "/reports/{report_id}"
        s["variables"] = {"report_id": None, "later": {"symbol": "id"}}
        before = deepcopy(s)
        validate_scenario(s)
        self.assertEqual(s, before)

    def test_valid_http_payload_and_headers(self):
        s = http()
        s["action"].update(json={"title": "Report"}, headers={"Accept": "application/json"})
        validate_scenario(s)

    def test_valid_command(self):
        self.assertIsNone(validate_scenario(command()))

    def test_valid_unsupported(self):
        s = unsupported_scenario(name="Visual layout", source="inferred",
                                 reason="Layout matters", explanation="Browser actions are unsupported")
        self.assertEqual(s, {"name": "Visual layout", "source": "inferred", "reason": "Layout matters",
                             "action": {"type": "unsupported", "explanation": "Browser actions are unsupported"}})
        validate_scenario(s)

    def test_invalid_source(self):
        for value in (None, "", "ambiguous", "EXPLICIT", [], 1):
            s = http()
            s["source"] = value
            self.reject(s)

    def test_unknown_action(self):
        for value in ("browser", "shell", None, [], {}):
            s = http()
            s["action"]["type"] = value
            self.reject(s)

    def test_invalid_method_and_path(self):
        for key, values in (("method", ["get", "HEAD", "", None, []]),
                            ("path", ["", " ", "reports/1", "https://example.org", None, 2])):
            for value in values:
                s = http()
                s["action"][key] = value
                self.reject(s)

    def test_http_requires_assertions(self):
        s = http()
        del s["assertions"]
        self.reject(s)
        for value in ([], None, {}, "status"):
            s["assertions"] = value
            self.reject(s)

    def test_invalid_status(self):
        for value in (99, 600, True, False, 200.0, "200", None):
            s = http()
            s["assertions"][0]["equals"] = value
            self.reject(s)

    def test_unknown_assertion(self):
        for value in ("regex", "python", None, []):
            s = http()
            s["assertions"][0]["type"] = value
            self.reject(s)

    def test_invalid_commands(self):
        for value in ("python3 -m unittest", [], (), None, [1], [""], ["  "], ["python3", None]):
            s = command()
            s["action"]["command"] = value
            self.reject(s)

    def test_command_forbids_even_empty_assertions(self):
        for value in ([], None, [{"type": "status", "equals": 200}]):
            s = command()
            s["assertions"] = value
            self.reject(s)

    def test_malformed_variables(self):
        for value in (None, [], "id", {"": 1}, {" ": 1}, {1: "id"}):
            s = http()
            s["variables"] = value
            self.reject(s)

    def test_extra_fields(self):
        for target in ("scenario", "action", "assertion"):
            s = http()
            obj = s if target == "scenario" else s["action"] if target == "action" else s["assertions"][0]
            obj["unexpected"] = "value"
            self.reject(s)
        s = command()
        s["action"]["shell"] = True
        self.reject(s)

    def test_missing_required_fields(self):
        for base in (http(), command()):
            for key in base:
                s = deepcopy(base)
                del s[key]
                self.reject(s)
            for key in base["action"]:
                s = deepcopy(base)
                del s["action"][key]
                self.reject(s)
        for key in ("type", "equals"):
            s = http()
            del s["assertions"][0][key]
            self.reject(s)

    def test_malformed_structures_and_common_text(self):
        for value in (None, [], "scenario"):
            self.reject(value)
            s = http()
            s["action"] = value
            self.reject(s)
            s = http()
            s["assertions"] = [value]
            self.reject(s)
        for field in ("name", "reason"):
            for value in (None, "", " ", 2):
                s = http()
                s[field] = value
                self.reject(s)

    def test_invalid_json_field_values_and_paths(self):
        assertion = {"type": "json_field", "path": "report.state", "equals": None}
        for field, values in (("equals", [{}, [], object(), float("nan"), float("inf"), -float("inf")]),
                              ("path", ["", " ", ".state", "state.", "a..b", "a. .b", None])):
            for value in values:
                s = http()
                s["assertions"] = [{**assertion, field: value}]
                self.reject(s)
        for key in assertion:
            a = dict(assertion)
            del a[key]
            s = http()
            s["assertions"] = [a]
            self.reject(s)
        s["assertions"] = [{**assertion, "callback": "code"}]
        self.reject(s)

    def test_invalid_payload_and_headers(self):
        for field, values in (("json", [None, [], "{}"]),
                              ("headers", [None, [], {1: "x"}, {"x": 1}])):
            for value in values:
                s = http()
                s["action"][field] = value
                self.reject(s)

    def test_invalid_unsupported_records(self):
        for explanation in ("", " ", None, 1):
            with self.assertRaises(ValueError):
                unsupported_scenario(name="Layout", source="explicit", reason="Requested", explanation=explanation)
        s = unsupported_scenario(name="Layout", source="explicit", reason="Requested", explanation="No browser")
        for mutation in ({"assertions": []}, {"verdict": "UNVERIFIED"}):
            self.reject({**s, **mutation})
        for action in ({"type": "unsupported"}, {**s["action"], "command": ["anything"]}):
            self.reject({**s, "action": action})


if __name__ == "__main__":
    unittest.main()
