"""Integration tests for Agentara."""

import tempfile
from pathlib import Path

import pytest

from agentara import (
    AgentParser,
    AgentValidator,
    load_agent_from_file,
    load_agent_from_str,
    register_processor,
    register_validator,
)


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_agent_lifecycle(self):
        """Test complete agent definition, parsing, and validation."""
        # Define a complete agent
        agent_dsl = """
        agent AIAssistant {
            name: "AI Assistant"
            description: "A helpful AI assistant"
            version: "1.0.0"
            author: "Test Team"

            capabilities [
                natural_language_processing,
                code_generation(language("python")),
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
                timeout: 60
            }
        }
        """

        # Load and validate
        model = load_agent_from_str(agent_dsl)

        # Verify structure
        assert len(model.agents) == 1
        agent = model.agents[0]

        assert agent.name == "AIAssistant"
        assert len(agent.properties) >= 4
        assert hasattr(agent, "capabilities")
        assert len(agent.capabilities.capabilities) == 3
        assert hasattr(agent, "parameters")
        assert len(agent.parameters.params) == 4
        assert hasattr(agent, "rules")
        assert len(agent.rules.rules) == 3

    def test_workflow_with_multiple_agents(self):
        """Test workflow connecting multiple agents."""
        workflow_dsl = """
        agent DataFetcher {
            name: "Data Fetcher"
            capabilities [fetch_data]
        }

        agent DataCleaner {
            name: "Data Cleaner"
            capabilities [clean_data, validate_data]
        }

        agent DataAnalyzer {
            name: "Data Analyzer"
            capabilities [analyze_data, generate_report]
        }

        workflow DataProcessingPipeline {
            agents: [DataFetcher, DataCleaner, DataAnalyzer]

            flow {
                DataFetcher -> DataCleaner
                DataCleaner -> DataAnalyzer
            }
        }
        """

        model = load_agent_from_str(workflow_dsl)

        # Verify agents
        assert len(model.agents) == 3
        agent_names = {agent.name for agent in model.agents}
        assert agent_names == {"DataFetcher", "DataCleaner", "DataAnalyzer"}

        # Verify workflow
        assert len(model.workflows) == 1
        workflow = model.workflows[0]
        assert workflow.name == "DataProcessingPipeline"
        assert len(workflow.agents) == 3
        assert len(workflow.flow.connections) == 2

    def test_custom_validation_integration(self):
        """Test integration with custom validators."""

        # Register custom validators
        @register_validator("agent")
        def validate_name_format(agent):
            if not agent.name[0].isupper():
                raise ValueError(f"Agent name must start with uppercase: {agent.name}")

        @register_validator("agent")
        def validate_version_exists(agent):
            has_version = False
            if hasattr(agent, "properties"):
                for prop in agent.properties:
                    if prop.name == "version":
                        has_version = True
                        break

            if not has_version:
                raise ValueError(f"Agent {agent.name} must have a version")

        # Test with valid agent
        valid_dsl = """
        agent ValidAgent {
            name: "Valid Agent"
            version: "1.0.0"
        }
        """

        # Should not raise
        model = load_agent_from_str(valid_dsl)

        # Test with invalid agent (lowercase name)
        invalid_dsl = """
        agent invalidAgent {
            name: "Invalid Agent"
            version: "1.0.0"
        }
        """

        parser = AgentParser()
        model = parser.parse(invalid_dsl)

        validator = AgentValidator()
        validator.add_validator("agent", validate_name_format)

        with pytest.raises(Exception) as exc_info:
            validator.validate(model)

        assert "must start with uppercase" in str(exc_info.value)

    def test_file_based_workflow(self):
        """Test loading agents from files."""
        # Create main agent file
        main_content = """
        agent MainAgent {
            name: "Main Agent"
            version: "1.0.0"

            capabilities [
                orchestrate,
                coordinate
            ]
        }
        """

        # Create worker agent file
        worker_content = """
        agent WorkerAgent {
            name: "Worker Agent"
            version: "1.0.0"

            capabilities [
                execute_task,
                report_status
            ]
        }
        """

        # Save to temporary files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            main_file = tmppath / "main.dsl"
            main_file.write_text(main_content, encoding="utf-8")

            worker_file = tmppath / "worker.dsl"
            worker_file.write_text(worker_content, encoding="utf-8")

            # Load both files
            main_model = load_agent_from_file(main_file)
            worker_model = load_agent_from_file(worker_file)

            assert main_model.agents[0].name == "MainAgent"
            assert worker_model.agents[0].name == "WorkerAgent"

    def test_error_handling_chain(self):
        """Test error handling through the full chain."""
        # Test parse error
        parse_error_dsl = """
        agent BadSyntax {
            this is not valid syntax
        }
        """

        with pytest.raises(Exception) as exc_info:
            load_agent_from_str(parse_error_dsl)

        assert "Failed to load agent" in str(exc_info.value)

        # Test validation error with custom validator
        @register_validator("agent")
        def always_fail(agent):
            raise ValueError("This agent is not allowed")

        valid_syntax_dsl = """
        agent WillFailValidation {
            name: "Valid Syntax"
        }
        """

        parser = AgentParser()
        model = parser.parse(valid_syntax_dsl)

        validator = AgentValidator()
        validator.add_validator("agent", always_fail)

        with pytest.raises(Exception) as exc_info:
            validator.validate(model)

        assert "not allowed" in str(exc_info.value)

    def test_complex_capability_parameters(self):
        """Test parsing complex capability parameters."""
        complex_dsl = """
        agent AdvancedAgent {
            name: "Advanced Agent"

            capabilities [
                code_generation(
                    language("python"),
                    style("pep8"),
                    max_lines(1000)
                ),
                api_integration(
                    protocol("rest"),
                    auth("oauth2")
                ),
                data_processing
            ]
        }
        """

        model = load_agent_from_str(complex_dsl)
        agent = model.agents[0]

        # Check capabilities
        assert len(agent.capabilities.capabilities) == 3

        # First capability should have parameters
        code_gen = agent.capabilities.capabilities[0]
        assert code_gen.name == "code_generation"
        assert hasattr(code_gen, "params")
        assert len(code_gen.params) == 3

    def test_model_processor_integration(self):
        """Test model processors integration."""
        from agentara import clear_registry

        # Clear registry before test
        clear_registry()

        process_count = 0

        @register_processor("model")
        def count_agents(model, metamodel):
            nonlocal process_count
            process_count += 1
            if hasattr(model, "agents"):
                model._total_agents = len(model.agents)

        # Create parser after registering processor
        parser = AgentParser()

        dsl = """
        agent Agent1 { name: "One" }
        agent Agent2 { name: "Two" }
        agent Agent3 { name: "Three" }
        """

        # Note: Processor registration happens in parser initialization
        # The processor will be called automatically during parsing
        model = parser.parse(dsl)

        assert process_count == 1
        assert hasattr(model, "_total_agents")
        assert model._total_agents == 3

        # Clear registry after test
        clear_registry()
