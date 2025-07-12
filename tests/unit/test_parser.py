"""Test cases for AgentParser."""

import pytest

from agentara import AgentaraParseError, AgentParser


class TestAgentParser:
    """Test cases for the Agent DSL parser."""

    def test_parse_empty_model(self):
        """Test parsing an empty model."""
        parser = AgentParser()
        content = ""
        model = parser.parse(content)
        assert model is not None
        assert hasattr(model, "agents")
        assert len(model.agents) == 0

    def test_parse_simple_agent(self):
        """Test parsing a simple agent definition."""
        parser = AgentParser()
        content = """
        agent SimpleAgent {
            name: "Simple Agent"
            description: "A simple test agent"
        }
        """
        model = parser.parse(content)
        assert len(model.agents) == 1

        agent = model.agents[0]
        assert agent.name == "SimpleAgent"

    def test_parse_multiple_agents(self):
        """Test parsing multiple agent definitions."""
        parser = AgentParser()
        content = """
        agent FirstAgent {
            name: "First Agent"
        }

        agent SecondAgent {
            name: "Second Agent"
        }
        """
        model = parser.parse(content)
        assert len(model.agents) == 2
        assert model.agents[0].name == "FirstAgent"
        assert model.agents[1].name == "SecondAgent"

    def test_parse_agent_with_capabilities(self):
        """Test parsing agent with capabilities."""
        parser = AgentParser()
        content = """
        agent WebSearcher {
            name: "Web Search Agent"
            version: "1.0.0"

            capabilities [
                search_web,
                extract_content,
                summarize
            ]
        }
        """
        model = parser.parse(content)
        agent = model.agents[0]
        assert agent.name == "WebSearcher"
        assert hasattr(agent, "capabilities")
        assert len(agent.capabilities.capabilities) == 3

    def test_parse_agent_with_parameters(self):
        """Test parsing agent with parameters."""
        parser = AgentParser()
        content = """
        agent ConfigurableAgent {
            name: "Configurable Agent"

            parameters {
                max_results: 10
                timeout: 30
                api_key: required
            }
        }
        """
        model = parser.parse(content)
        agent = model.agents[0]
        assert hasattr(agent, "parameters")
        assert len(agent.parameters.params) == 3

    def test_parse_agent_with_rules(self):
        """Test parsing agent with rules."""
        parser = AgentParser()
        content = """
        agent RuleBasedAgent {
            name: "Rule Based Agent"

            rules {
                on_error: retry(3)
                ratelimit: 10/minute
                timeout: 60
            }
        }
        """
        model = parser.parse(content)
        agent = model.agents[0]
        assert hasattr(agent, "rules")
        assert len(agent.rules.rules) == 3

    def test_parse_complex_agent(self):
        """Test parsing a complex agent with all features."""
        parser = AgentParser()
        content = """
        agent ComplexAgent {
            name: "Complex AI Agent"
            description: "A fully featured agent"
            version: "2.0.0"
            author: "Test Author"

            capabilities [
                natural_language_processing,
                code_generation(language("python"), style("pep8")),
                data_analysis
            ]

            parameters {
                model: "gpt-4"
                temperature: 0.7
                max_tokens: 2000
                api_key: required
            }

            rules {
                on_error: retry(3)
                rate_limit: 100/hour
                timeout: 120
                max_concurrent: 5
            }
        }
        """
        model = parser.parse(content)
        agent = model.agents[0]

        assert agent.name == "ComplexAgent"
        assert len(agent.properties) >= 4
        assert hasattr(agent, "capabilities")
        assert hasattr(agent, "parameters")
        assert hasattr(agent, "rules")

    def test_parse_workflow(self):
        """Test parsing workflow definition."""
        parser = AgentParser()
        content = """
        agent DataCollector {
            name: "Data Collector"
        }

        agent DataProcessor {
            name: "Data Processor"
        }

        agent DataAnalyzer {
            name: "Data Analyzer"
        }

        workflow DataPipeline {
            agents: [DataCollector, DataProcessor, DataAnalyzer]

            flow {
                DataCollector -> DataProcessor
                DataProcessor -> DataAnalyzer
            }
        }
        """
        model = parser.parse(content)

        assert len(model.agents) == 3
        assert hasattr(model, "workflows")
        assert len(model.workflows) == 1

        workflow = model.workflows[0]
        assert workflow.name == "DataPipeline"
        assert len(workflow.agents) == 3

    def test_parse_with_comments(self):
        """Test parsing DSL with comments."""
        parser = AgentParser()
        content = """
        // This is a comment
        agent CommentedAgent {
            name: "Agent with comments"
            // Another comment
            description: "Testing comment support"
        }
        """
        model = parser.parse(content)
        assert len(model.agents) == 1
        assert model.agents[0].name == "CommentedAgent"

    def test_parse_invalid_syntax(self):
        """Test parsing invalid syntax raises error."""
        parser = AgentParser()
        content = """
        agent InvalidAgent {
            name:
        }
        """
        with pytest.raises(AgentaraParseError):
            parser.parse(content)

    def test_parse_missing_closing_brace(self):
        """Test parsing with missing closing brace."""
        parser = AgentParser()
        content = """
        agent UnclosedAgent {
            name: "Unclosed"
        """
        with pytest.raises(AgentaraParseError):
            parser.parse(content)

    def test_parse_invalid_capability_syntax(self):
        """Test parsing invalid capability syntax."""
        parser = AgentParser()
        content = """
        agent BadCapabilities {
            capabilities [
                search_web
                extract_content
            ]
        }
        """
        # Missing comma between capabilities
        with pytest.raises(AgentaraParseError):
            parser.parse(content)

    def test_parse_empty_agent(self):
        """Test parsing empty agent definition."""
        parser = AgentParser()
        content = """
        agent EmptyAgent {
        }
        """
        model = parser.parse(content)
        assert len(model.agents) == 1
        assert model.agents[0].name == "EmptyAgent"
        assert len(model.agents[0].properties) == 0
