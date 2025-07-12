"""End-to-end test runner for Agentara."""

import json
from pathlib import Path

import pytest

from agentara import AgentParser


class TestE2E:
    """End-to-end tests using JSON test cases."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance."""
        return AgentParser()

    @pytest.fixture
    def test_cases(self):
        """Load all test cases from the io directory."""
        test_dir = Path(__file__).parent / "io"
        test_cases = []

        for json_file in test_dir.glob("*.json"):
            with open(json_file) as f:
                test_case = json.load(f)
                test_case["name"] = json_file.stem
                test_cases.append(test_case)

        return test_cases

    def test_all_cases(self, parser, test_cases):
        """Run all test cases."""
        for test_case in test_cases:
            name = test_case["name"]
            description = test_case["description"]
            input_dsl = test_case["input"]
            expected = test_case["expected"]

            print(f"\nRunning test: {name} - {description}")

            if expected["success"]:
                # Test should succeed
                result = parser.parse(input_dsl)

                # Check agents count
                if "agents_count" in expected:
                    assert len(result["agents"]) == expected["agents_count"], (
                        f"Expected {expected['agents_count']} agents, got {len(result['agents'])}"
                    )

                # Check agent IDs
                if "agent_ids" in expected:
                    actual_ids = [agent["id"] for agent in result["agents"]]
                    assert actual_ids == expected["agent_ids"], (
                        f"Expected IDs {expected['agent_ids']}, got {actual_ids}"
                    )

                # Check first agent ID
                if "first_agent_id" in expected and result["agents"]:
                    assert result["agents"][0]["id"] == expected["first_agent_id"]

                # Check first agent properties
                if "first_agent_properties" in expected and result["agents"]:
                    actual_props = result["agents"][0]["properties"]
                    expected_props = expected["first_agent_properties"]

                    for key, value in expected_props.items():
                        assert key in actual_props, f"Missing property: {key}"
                        assert actual_props[key] == value, f"Property {key}: expected {value}, got {actual_props[key]}"

            else:
                # Test should fail
                with pytest.raises(Exception) as exc_info:
                    parser.parse(input_dsl)

                if "error_contains" in expected:
                    assert expected["error_contains"] in str(exc_info.value), (
                        f"Expected error to contain '{expected['error_contains']}', got: {exc_info.value}"
                    )
