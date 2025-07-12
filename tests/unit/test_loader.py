"""Test cases for loader functions."""

import tempfile
from pathlib import Path

import pytest

from agentara import AgentaraError, load_agent_from_file, load_agent_from_str


class TestLoader:
    """Test cases for agent loading functions."""

    def test_load_from_string(self):
        """Test loading agent from string."""
        content = """
        agent TestAgent {
            name: "Test Agent"
            description: "A test agent"
        }
        """
        model = load_agent_from_str(content)

        assert model is not None
        assert len(model.agents) == 1
        assert model.agents[0].name == "TestAgent"

    def test_load_from_string_no_validation(self):
        """Test loading agent from string without validation."""
        content = """
        agent TestAgent {
            name: "Test Agent"
        }
        """
        model = load_agent_from_str(content, validate=False)

        assert model is not None
        assert len(model.agents) == 1

    def test_load_from_string_with_error(self):
        """Test loading invalid agent from string."""
        content = """
        agent TestAgent {
            invalid syntax here
        }
        """
        with pytest.raises(AgentaraError) as exc_info:
            load_agent_from_str(content)

        assert "Failed to load agent" in str(exc_info.value)

    def test_load_from_file(self):
        """Test loading agent from file."""
        content = """
        agent FileAgent {
            name: "File Agent"
            version: "1.0.0"
        }
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dsl", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            model = load_agent_from_file(temp_path)

            assert model is not None
            assert len(model.agents) == 1
            assert model.agents[0].name == "FileAgent"
        finally:
            # Clean up
            Path(temp_path).unlink()

    def test_load_from_nonexistent_file(self):
        """Test loading from non-existent file."""
        with pytest.raises(AgentaraError) as exc_info:
            load_agent_from_file("/path/that/does/not/exist.dsl")

        assert "File not found" in str(exc_info.value)

    def test_load_complex_agent(self):
        """Test loading complex agent definition."""
        content = """
        agent ComplexAgent {
            name: "Complex Agent"
            description: "A complex agent with all features"
            version: "2.0.0"

            capabilities [
                search_web,
                extract_content,
                summarize
            ]

            parameters {
                max_results: 10
                timeout: 30
                api_key: required
            }

            rules {
                on_error: retry(3)
                rate_limit: 10/minute
            }
        }
        """

        model = load_agent_from_str(content)

        assert model is not None
        agent = model.agents[0]
        assert agent.name == "ComplexAgent"
        assert hasattr(agent, "capabilities")
        assert hasattr(agent, "parameters")
        assert hasattr(agent, "rules")

    def test_load_multiple_agents(self):
        """Test loading multiple agents."""
        content = """
        agent FirstAgent {
            name: "First"
        }

        agent SecondAgent {
            name: "Second"
        }

        agent ThirdAgent {
            name: "Third"
        }
        """

        model = load_agent_from_str(content)

        assert len(model.agents) == 3
        assert [a.name for a in model.agents] == ["FirstAgent", "SecondAgent", "ThirdAgent"]

    def test_load_with_workflow(self):
        """Test loading agents with workflow."""
        content = """
        agent DataCollector {
            name: "Data Collector"
            capabilities [collect_data]
        }

        agent DataProcessor {
            name: "Data Processor"
            capabilities [process_data]
        }

        workflow DataPipeline {
            agents: [DataCollector, DataProcessor]

            flow {
                DataCollector -> DataProcessor
            }
        }
        """

        model = load_agent_from_str(content)

        assert len(model.agents) == 2
        assert hasattr(model, "workflows")
        assert len(model.workflows) == 1
        assert model.workflows[0].name == "DataPipeline"

    def test_load_file_with_pathlib(self):
        """Test loading file using pathlib.Path."""
        content = """
        agent PathAgent {
            name: "Path Agent"
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dsl", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            model = load_agent_from_file(temp_path)

            assert model is not None
            assert model.agents[0].name == "PathAgent"
        finally:
            temp_path.unlink()

    def test_load_with_utf8_content(self):
        """Test loading file with UTF-8 content."""
        content = """
        agent UnicodeAgent {
            name: "Unicode Agent 中文"
            description: "Agent with émojis 🚀 and special chars"
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dsl", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            model = load_agent_from_file(temp_path)

            assert model is not None
            assert model.agents[0].name == "UnicodeAgent"
        finally:
            Path(temp_path).unlink()
