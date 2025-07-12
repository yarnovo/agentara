"""Test cases for AgentParser."""

import pytest

from agentara import AgentParser


class TestAgentParser:
    """Test cases for the Agent DSL parser."""

    def test_parse_empty_model(self):
        """Test parsing an empty model."""
        parser = AgentParser()
        content = ""
        result = parser.parse(content)
        assert result is not None
        assert "agents" in result
        assert len(result["agents"]) == 0

    def test_parse_simple_agent(self):
        """Test parsing a simple agent definition."""
        parser = AgentParser()
        content = """
        agent SimpleAgent {
            name: "Simple Agent"
            description: "A simple test agent"
        }
        """
        result = parser.parse(content)
        assert len(result["agents"]) == 1

        agent = result["agents"][0]
        assert agent["id"] == "SimpleAgent"
        assert agent["properties"]["name"] == "Simple Agent"
        assert agent["properties"]["description"] == "A simple test agent"

    def test_parse_multiple_agents(self):
        """Test parsing multiple agent definitions."""
        parser = AgentParser()
        content = """
        agent FirstAgent {
            name: "First Agent"
            model_provider: "openai"
        }

        agent SecondAgent {
            name: "Second Agent"
            model_provider: "anthropic"
        }
        """
        result = parser.parse(content)
        assert len(result["agents"]) == 2
        assert result["agents"][0]["id"] == "FirstAgent"
        assert result["agents"][1]["id"] == "SecondAgent"

    def test_parse_agent_with_all_properties(self):
        """Test parsing agent with all supported properties."""
        parser = AgentParser()
        content = """
        agent CompleteAgent {
            name: "Complete Agent"
            description: "An agent with all properties"
            system_prompt: "You are a helpful assistant."
            model_provider: "openai"
            model_name: "gpt-4"
            temperature: 0.7
            max_tokens: 2000
        }
        """
        result = parser.parse(content)
        agent = result["agents"][0]
        props = agent["properties"]

        assert props["name"] == "Complete Agent"
        assert props["description"] == "An agent with all properties"
        assert props["system_prompt"] == "You are a helpful assistant."
        assert props["model_provider"] == "openai"
        assert props["model_name"] == "gpt-4"
        assert props["temperature"] == 0.7
        assert props["max_tokens"] == 2000

    def test_parse_with_numbers(self):
        """Test parsing numeric values."""
        parser = AgentParser()
        content = """
        agent NumericAgent {
            temperature: 0.5
            max_tokens: 1000
        }
        """
        result = parser.parse(content)
        agent = result["agents"][0]

        assert agent["properties"]["temperature"] == 0.5
        assert isinstance(agent["properties"]["temperature"], float)
        assert agent["properties"]["max_tokens"] == 1000
        assert isinstance(agent["properties"]["max_tokens"], int)

    def test_parse_with_comments(self):
        """Test parsing with comments."""
        parser = AgentParser()
        content = """
        // This is a comment
        agent CommentedAgent {
            name: "Agent with comments"
            // Another comment
            description: "Test agent"
        }
        // Final comment
        """
        result = parser.parse(content)
        assert len(result["agents"]) == 1
        assert result["agents"][0]["properties"]["name"] == "Agent with comments"

    def test_parse_invalid_syntax(self):
        """Test parsing with invalid syntax."""
        parser = AgentParser()
        content = """
        agent InvalidAgent {
            name "Missing colon"
        }
        """
        with pytest.raises(Exception) as exc_info:
            parser.parse(content)
        assert "Syntax error" in str(exc_info.value)

    def test_parse_missing_closing_brace(self):
        """Test parsing with missing closing brace."""
        parser = AgentParser()
        content = """
        agent Unclosed {
            name: "Unclosed agent"
        """
        with pytest.raises(Exception) as exc_info:
            parser.parse(content)
        assert "error" in str(exc_info.value).lower()

    def test_parse_empty_agent(self):
        """Test parsing an agent with no properties."""
        parser = AgentParser()
        content = """
        agent EmptyAgent {
        }
        """
        result = parser.parse(content)
        assert len(result["agents"]) == 1
        assert result["agents"][0]["id"] == "EmptyAgent"
        assert result["agents"][0]["properties"] == {}

    def test_parse_with_string_identifiers(self):
        """Test parsing with string values vs identifiers."""
        parser = AgentParser()
        content = """
        agent TestAgent {
            model_provider: openai
            model_name: "gpt-4"
        }
        """
        result = parser.parse(content)
        agent = result["agents"][0]

        # Both should work - identifier and string
        assert agent["properties"]["model_provider"] == "openai"
        assert agent["properties"]["model_name"] == "gpt-4"
