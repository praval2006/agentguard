"""Fake-provider contract checks, not evidence of real grounding intelligence."""

from copy import deepcopy
from contextlib import ExitStack
import unittest
from unittest.mock import Mock, patch

from agentguard.grounding import (
    MAX_PLANNER_LIST_ITEMS, MAX_PLANNER_TEXT_CHARS, MAX_TEXT_CHARS, ground_scenarios,
)
from agentguard.scenarios import validate_scenario


def plan(count=1):
    return {"explicit_requirements": ["Deleted reports cannot be retrieved."],
            "inferred_behaviors": [], "ambiguities": [], "scenarios": [
                {"name": f"Retrieval {i}", "behavior": "Deleted report should no longer be retrievable",
                 "reason": "Deletion removes retrieval access", "source": "inferred"}
                for i in range(count)]}


def unsupported(p):
    return [{**{k: s[k] for k in ("name", "source", "reason")},
             "action": {"type": "unsupported", "explanation": "No supported retrieval mechanism is evidenced"}}
            for s in p["scenarios"]]


class GroundingTests(unittest.TestCase):
    def invoke(self, p, result, context=""):
        return ground_scenarios(p, context, grounding_provider=Mock(return_value=result))

    def test_evidenced_http(self):
        p = plan()
        result = unsupported(p)
        result[0].update(action={"type": "http_request", "method": "GET", "path": "/reports/{id}"},
                         variables={"id": "deleted_report_id"}, assertions=[{"type": "status", "equals": 404}])
        context = "GET /reports/{id}: missing reports return 404. Fixture deleted_report_id identifies a deleted report."
        self.assertEqual(self.invoke(p, result, context), result)

    def test_missing_execution_mechanism_is_unsupported(self):
        p = plan()
        context = "Reports have an owner and title. Deletion removes a report."
        result = self.invoke(p, unsupported(p), context)
        self.assertEqual(result[0]["action"]["type"], "unsupported")
        self.assertIn("No supported retrieval mechanism", result[0]["action"]["explanation"])

    def test_evidenced_test_command(self):
        p = plan()
        result = unsupported(p)
        result[0]["action"] = {"type": "test_command", "command": ["python3", "-m", "unittest", "tests.test_reports"]}
        self.assertEqual(self.invoke(p, result, "Existing retrieval regression command: python3 -m unittest tests.test_reports"), result)

    def test_request_contains_only_supplied_evidence_and_instructions(self):
        p = plan()
        p["ambiguities"] = ["Retention period is unspecified."]
        provider = Mock(return_value=unsupported(p))
        ground_scenarios(p, "Supplied context", grounding_provider=provider)
        provider.assert_called_once()
        request = provider.call_args.args[0]
        self.assertEqual(set(request), {"instructions", "planner_output", "repository_context"})
        self.assertEqual(request["planner_output"], p)
        self.assertEqual(request["repository_context"], "Supplied context")
        for phrase in ("WHAT", "Never invent", "ambiguities", "Unsupported is preferable",
                       "never upgrade", "Do not execute", "command safety", "direct relevance",
                       "a test", "No extra schema fields"):
            self.assertIn(phrase, request["instructions"])

    def test_provider_error_propagates_once(self):
        provider = Mock(side_effect=RuntimeError("offline"))
        with self.assertRaisesRegex(RuntimeError, "offline"):
            ground_scenarios(plan(), "", grounding_provider=provider)
        provider.assert_called_once()

    def test_missing_result(self):
        with self.assertRaises(ValueError): self.invoke(plan(), [])

    def test_added_result(self):
        with self.assertRaises(ValueError): self.invoke(plan(), unsupported(plan(2)))

    def test_reordered_results(self):
        p = plan(2)
        with self.assertRaises(ValueError): self.invoke(p, unsupported(p)[::-1])

    def test_changed_name(self):
        self.check_identity_change("name", "Different name")

    def test_changed_source(self):
        self.check_identity_change("source", "explicit")

    def test_changed_reason(self):
        self.check_identity_change("reason", "Different reason")

    def check_identity_change(self, field, value):
        p = plan()
        result = unsupported(p)
        result[0][field] = value
        with self.assertRaisesRegex(ValueError, "preserve"):
            self.invoke(p, result)

    def test_malformed_planner_output(self):
        bad = [None, [], {}, {**plan(), "extra": []}]
        for key in plan():
            p = plan()
            del p[key]
            bad.append(p)
        for key in plan()["scenarios"][0]:
            p = plan()
            del p["scenarios"][0][key]
            bad.append(p)
            p = plan()
            p["scenarios"][0][key] = " "
            bad.append(p)
        for entry in (None, "text", {**plan()["scenarios"][0], "extra": 1}):
            p = plan()
            p["scenarios"] = [entry]
            bad.append(p)
        for p in bad:
            provider = Mock()
            with self.subTest(p=p), self.assertRaises(ValueError):
                ground_scenarios(p, "", grounding_provider=provider)
            provider.assert_not_called()

    def test_malformed_ambiguities_and_requirement_lists(self):
        for field in ("ambiguities", "explicit_requirements", "inferred_behaviors"):
            for value in (None, "text", {}, [None], [""], [" "]):
                p = plan()
                p[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.invoke(p, unsupported(plan()))

    def test_malformed_context(self):
        for value in (None, {}, [], 1):
            with self.assertRaises(ValueError): self.invoke(plan(), [], value)

    def test_noncallable_provider(self):
        with self.assertRaises(ValueError):
            ground_scenarios(plan(), "", grounding_provider=None)

    def test_malformed_provider_result(self):
        for value in (None, {}, "[]", (), [None]):
            with self.assertRaises(ValueError): self.invoke(plan(), value)

    def test_each_result_passes_through_schema_validator(self):
        p = plan(2)
        result = unsupported(p)
        with patch("agentguard.grounding.validate_scenario", wraps=validate_scenario) as validate:
            self.invoke(p, result)
            self.assertEqual(validate.call_count, 2)
        result[1]["action"] = {"type": "http_request", "method": "GET", "path": "/"}
        with self.assertRaisesRegex(ValueError, "assertions"):
            self.invoke(p, result)

    def test_scenario_count_boundary(self):
        p = plan(5)
        self.assertEqual(len(self.invoke(p, unsupported(p))), 5)
        provider = Mock()
        with self.assertRaises(ValueError):
            ground_scenarios(plan(6), "", grounding_provider=provider)
        provider.assert_not_called()

    def test_empty_scenarios(self):
        provider = Mock(return_value=[])
        self.assertEqual(ground_scenarios(plan(0), "", grounding_provider=provider), [])
        provider.assert_called_once()
        with self.assertRaises(ValueError): self.invoke(plan(0), unsupported(plan()))

    def test_no_execution_or_external_reads(self):
        p = plan()
        result = unsupported(p)
        result[0]["action"] = {"type": "test_command", "command": ["not-a-real-command"]}
        with ExitStack() as stack:
            mocks = [stack.enter_context(patch(target, side_effect=AssertionError("External access")))
                     for target in ("builtins.open", "pathlib.Path.open", "subprocess.run",
                                    "subprocess.Popen", "socket.socket", "os.getenv", "os.system")]
            self.invoke(p, result, "Existing command: not-a-real-command")
            result[0].update(action={"type": "http_request", "method": "GET", "path": "/health"},
                             assertions=[{"type": "status", "equals": 200}])
            self.invoke(p, result, "GET /health returns 200")
            for mock in mocks: mock.assert_not_called()

    def test_input_size_and_list_bounds(self):
        p = plan(0)
        p["explicit_requirements"] = ["x" * MAX_PLANNER_TEXT_CHARS]
        self.assertEqual(self.invoke(p, [], "x" * MAX_TEXT_CHARS), [])
        for context, extra in (("x" * (MAX_TEXT_CHARS + 1), ""), ("", "x")):
            q = deepcopy(p)
            q["explicit_requirements"][0] += extra
            with self.assertRaises(ValueError): self.invoke(q, [], context)
        for field in ("ambiguities", "explicit_requirements", "inferred_behaviors"):
            q = plan(0)
            q[field] = ["x"] * MAX_PLANNER_LIST_ITEMS
            self.invoke(q, [])
            q[field].append("x")
            with self.assertRaises(ValueError): self.invoke(q, [])

    def test_provider_cannot_mutate_preservation_baseline(self):
        p = plan()
        before = deepcopy(p)
        def provider(request):
            request["planner_output"]["scenarios"][0]["source"] = "explicit"
            return unsupported(request["planner_output"])
        with self.assertRaisesRegex(ValueError, "preserve source"):
            ground_scenarios(p, "", grounding_provider=provider)
        self.assertEqual(p, before)


if __name__ == "__main__":
    unittest.main()
