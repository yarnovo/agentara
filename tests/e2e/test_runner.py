"""End-to-end test runner for Agentara.

This runner loads test cases from JSON files in the io/ directory and executes them.
Each test case contains:
- input: The DSL input from AI
- expected_output: Expected parsing result
- expected_errors: Expected validation errors (if any)
"""

import json
from pathlib import Path
from typing import Any

import pytest

from agentara import load_agent_from_str


class E2ETestRunner:
    """Runner for end-to-end tests based on JSON test cases."""

    def __init__(self, test_dir: Path):
        """Initialize the test runner with test directory."""
        self.test_dir = test_dir
        self.io_dir = test_dir / "io"

    def load_test_case(self, json_file: Path) -> dict[str, Any]:
        """Load a test case from JSON file."""
        with open(json_file, encoding="utf-8") as f:
            return json.load(f)

    def get_all_test_cases(self) -> list[Path]:
        """Get all JSON test case files."""
        return sorted(self.io_dir.glob("*.json"))

    def run_test_case(self, test_case: dict[str, Any]) -> None:
        """Run a single test case."""
        input_dsl = test_case.get("input", "")
        expected_output = test_case.get("expected_output", {})
        expected_errors = test_case.get("expected_errors", [])

        if expected_errors:
            # Test should fail with specific errors
            with pytest.raises(Exception) as exc_info:
                load_agent_from_str(input_dsl)

            error_msg = str(exc_info.value)
            for expected_error in expected_errors:
                assert expected_error in error_msg, f"Expected error '{expected_error}' not found in '{error_msg}'"
        else:
            # Test should succeed
            model = load_agent_from_str(input_dsl)

            # Verify expected output
            if "agents" in expected_output:
                assert len(model.agents) == len(expected_output["agents"])

                for i, expected_agent in enumerate(expected_output["agents"]):
                    actual_agent = model.agents[i]

                    # Check agent properties
                    assert actual_agent.name == expected_agent["name"]

                    # Check capabilities if specified
                    if "capabilities" in expected_agent:
                        assert hasattr(actual_agent, "capabilities")
                        actual_caps = [cap.name for cap in actual_agent.capabilities.capabilities]
                        assert actual_caps == expected_agent["capabilities"]

                    # Check parameters if specified
                    if "parameters" in expected_agent:
                        assert hasattr(actual_agent, "parameters")
                        # Additional parameter checks can be added here

            # Verify workflows if specified
            if "workflows" in expected_output:
                assert hasattr(model, "workflows")
                assert len(model.workflows) == len(expected_output["workflows"])


# Test generation using pytest
def pytest_generate_tests(metafunc):
    """Generate test cases from JSON files."""
    if "test_case_file" in metafunc.fixturenames:
        runner = E2ETestRunner(Path(__file__).parent)
        test_files = runner.get_all_test_cases()

        # Generate test IDs from filenames
        test_ids = [f.stem for f in test_files]

        metafunc.parametrize("test_case_file", test_files, ids=test_ids)


class TestE2E:
    """End-to-end test class."""

    def test_from_json(self, test_case_file: Path):
        """Run end-to-end test from JSON file."""
        runner = E2ETestRunner(Path(__file__).parent)
        test_case = runner.load_test_case(test_case_file)

        # Extract test metadata
        test_name = test_case.get("name", test_case_file.stem)
        test_description = test_case.get("description", "")

        print(f"\nRunning E2E test: {test_name}")
        if test_description:
            print(f"Description: {test_description}")

        # Run the test
        runner.run_test_case(test_case)
