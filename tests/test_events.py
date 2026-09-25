import unittest

from agentguard.events import Event


class EventContractTests(unittest.TestCase):
    def test_event_can_be_serialized_with_dependencies(self):
        event = Event("run-1", "step-2", "tool_result", "failed", "test failed", ("step-1",))
        self.assertEqual(event.to_dict()["dependency_ids"], ["step-1"])
        self.assertTrue(event.to_dict()["timestamp"])


if __name__ == "__main__":
    unittest.main()
