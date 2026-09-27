"""Contract tests using fake reasoning; these do not evaluate model quality."""

import ast
from copy import deepcopy
from pathlib import Path
import unittest
from unittest.mock import Mock

from agentguard.planner import MAX_TEXT_CHARS, plan_acceptance


def example_plan():
    return {
        "explicit_requirements": ["Export records as CSV."],
        "inferred_behaviors": ["Quote commas in field values."],
        "ambiguities": ["Which text encoding should be used?"],
        "scenarios": [
            {"name": "CSV export", "behavior": "Export records as CSV.",
             "reason": "The task requests CSV export.", "source": "explicit"},
            {"name": "Comma escaping", "behavior": "Quote commas in values.",
             "reason": "CSV must preserve field boundaries.", "source": "inferred"},
        ],
    }


class PlannerTests(unittest.TestCase):
    def test_generic_request_preserves_inputs_priority_and_grounding_categories(self):
        expected = example_plan()
        provider = Mock(return_value=deepcopy(expected))
        result = plan_acceptance("Export records as CSV.", "Records contain text.",
                                 reasoning_provider=provider)
        self.assertEqual(result, expected)
        provider.assert_called_once()
        request = provider.call_args.args[0]
        self.assertEqual(request["task_text"], "Export records as CSV.")
        self.assertEqual(request["repository_context"], "Records contain text.")
        self.assertIn("directly", request["instructions"])
        self.assertIn("ambiguities", request["instructions"])
        self.assertIn("highest-priority-first", request["instructions"])

    def test_subscription_smoke_contract_with_fake_reasoning(self):
        root = Path(__file__).resolve().parents[1]
        task = (root / "tasks/subscription_cancellation.md").read_text()
        # Include implementation code without fixture-answer documentation.
        tree = ast.parse((root / "sample_app/subscription.py").read_text())
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
        function.body = function.body[1:]  # Omit the fixture's explanatory docstring.
        context = ast.unparse(function)
        requirements = [
            "the subscription should become cancelled",
            "the user should no longer have access to premium features",
            "repeated cancellation should not crash the application",
        ]
        expected = {"explicit_requirements": requirements,
                    "inferred_behaviors": [], "ambiguities": [], "scenarios": [
                        {"name": name, "behavior": requirement,
                         "reason": "Directly stated in Original Task.", "source": "explicit"}
                        for name, requirement in zip(
                            ["Cancelled state", "Premium access removed", "Safe repeat"], requirements)
                    ]}
        provider = Mock(return_value=expected)
        result = plan_acceptance(task, context, reasoning_provider=provider)
        self.assertEqual(result, expected)
        for requirement in requirements:
            self.assertIn(requirement, task)
        self.assertEqual(provider.call_args.args[0]["repository_context"], context)
        self.assertIn('subscription[\'status\']', context)
        self.assertNotIn("intentionally", context)

    def test_empty_plan_and_empty_context_allowed(self):
        empty = {key: [] for key in example_plan()}
        self.assertEqual(plan_acceptance("Describe export.", "",
                         reasoning_provider=lambda request: empty), empty)

    def test_five_scenarios_allowed_six_rejected(self):
        plan = example_plan()
        plan["scenarios"] = [deepcopy(plan["scenarios"][0]) for _ in range(5)]
        self.assertEqual(len(plan_acceptance("Task", "", reasoning_provider=lambda r: plan)["scenarios"]), 5)
        plan["scenarios"].append(deepcopy(plan["scenarios"][0]))
        with self.assertRaisesRegex(ValueError, "at most 5"):
            plan_acceptance("Task", "", reasoning_provider=lambda r: plan)

    def test_missing_extra_and_non_dictionary_output_rejected(self):
        bad_outputs = [None, [], "{}", {**example_plan(), "verdict": "PASS"}]
        for key in example_plan():
            plan = example_plan()
            del plan[key]
            bad_outputs.append(plan)
        for output in bad_outputs:
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "dictionary"):
                plan_acceptance("Task", "", reasoning_provider=lambda r: output)

    def test_top_level_field_types_and_text_entries_rejected(self):
        for field in example_plan():
            for value in (None, {}, "text", [None] if field != "scenarios" else "bad"):
                plan = example_plan()
                plan[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    plan_acceptance("Task", "", reasoning_provider=lambda r: plan)
        for field in ("explicit_requirements", "inferred_behaviors", "ambiguities"):
            plan = example_plan()
            plan[field] = [" "]
            with self.subTest(field=field), self.assertRaises(ValueError):
                plan_acceptance("Task", "", reasoning_provider=lambda r: plan)

    def test_malformed_scenarios_rejected(self):
        scenario = example_plan()["scenarios"][0]
        bad = [None, "text", {**scenario, "verdict": "FAIL"}]
        for key in scenario:
            missing = dict(scenario)
            del missing[key]
            bad.append(missing)
            bad.extend({**scenario, key: value} for value in (None, 1, " "))
        bad.extend({**scenario, "source": value} for value in ("ambiguous", "EXPLICIT"))
        for item in bad:
            plan = example_plan()
            plan["scenarios"] = [item]
            with self.subTest(item=item), self.assertRaisesRegex(ValueError, "scenarios"):
                plan_acceptance("Task", "", reasoning_provider=lambda r: plan)

    def test_invalid_inputs_rejected_before_provider_call(self):
        provider = Mock()
        for task, context in ((None, ""), ("Task", []), (" ", ""),
                              ("x" * (MAX_TEXT_CHARS + 1), ""),
                              ("Task", "x" * (MAX_TEXT_CHARS + 1))):
            with self.subTest(task=type(task), context=type(context)):
                with self.assertRaises((TypeError, ValueError)):
                    plan_acceptance(task, context, reasoning_provider=provider)
        provider.assert_not_called()
        with self.assertRaisesRegex(TypeError, "callable"):
            plan_acceptance("Task", "", reasoning_provider=None)

    def test_text_limit_boundary_is_not_truncated(self):
        provider = Mock(return_value=example_plan())
        text = "x" * MAX_TEXT_CHARS
        plan_acceptance(text, text, reasoning_provider=provider)
        self.assertEqual(provider.call_args.args[0]["task_text"], text)
        self.assertEqual(provider.call_args.args[0]["repository_context"], text)

    def test_provider_failure_propagates_without_retry(self):
        provider = Mock(side_effect=RuntimeError("provider unavailable"))
        with self.assertRaisesRegex(RuntimeError, "provider unavailable"):
            plan_acceptance("Task", "", reasoning_provider=provider)
        provider.assert_called_once()


if __name__ == "__main__":
    unittest.main()
