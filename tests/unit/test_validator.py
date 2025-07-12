"""Test cases for AgentValidator."""

import typing

import pytest

from agentara import AgentaraParseError, AgentaraValidationError, AgentParser, AgentValidator


class TestAgentValidator:
    """Test cases for the Agent validator."""

    def test_validate_empty_model(self):
        """Test validating an empty model."""
        parser = AgentParser()
        validator = AgentValidator()

        model = parser.parse("")
        # Should not raise any exception
        validator.validate(model)

    def test_validate_agent_without_name(self):
        """Test validating agent without name raises error."""
        validator = AgentValidator()

        # Create a mock agent without name
        class MockAgent:
            pass

        class MockModel:
            agents: typing.ClassVar = [MockAgent()]

        with pytest.raises(AgentaraValidationError) as exc_info:
            validator.validate(MockModel())

        assert "must have a name" in str(exc_info.value)

    def test_validate_valid_agent(self):
        """Test validating a valid agent."""
        parser = AgentParser()
        validator = AgentValidator()

        content = """
        agent ValidAgent {
            name: "Valid Agent"
            description: "A valid test agent"
        }
        """
        model = parser.parse(content)
        # Should not raise any exception
        validator.validate(model)

    def test_custom_validator_registration(self):
        """Test registering and using custom validators."""
        parser = AgentParser()
        validator = AgentValidator()

        # Define a custom validator
        def validate_agent_name_length(agent):
            if len(agent.name) < 3:
                raise ValueError("Agent name must be at least 3 characters")

        # Register the validator
        validator.add_validator("agent", validate_agent_name_length)

        # Test with short name
        content = """
        agent Ab {
            name: "Ab"
        }
        """
        model = parser.parse(content)

        with pytest.raises(AgentaraValidationError) as exc_info:
            validator.validate(model)

        assert "at least 3 characters" in str(exc_info.value)

    def test_validate_agent_version_format(self):
        """Test validating agent version format."""
        parser = AgentParser()
        validator = AgentValidator()

        # Add version validator
        def validate_version_format(agent):
            if hasattr(agent, "properties"):
                for prop in agent.properties:
                    if prop.name == "version":
                        version = prop.value.strip('"')
                        # Simple semantic version check
                        parts = version.split(".")
                        if len(parts) != 3 or not all(p.isdigit() for p in parts):
                            raise ValueError(f"Invalid version format: {version}")

        validator.add_validator("agent", validate_version_format)

        # Test with invalid version
        content = """
        agent BadVersion {
            name: "Bad Version Agent"
            version: "1.0"
        }
        """
        model = parser.parse(content)

        with pytest.raises(AgentaraValidationError) as exc_info:
            validator.validate(model)

        assert "Invalid version format" in str(exc_info.value)

    def test_validate_required_parameters(self):
        """Test validating required parameters."""
        parser = AgentParser()
        validator = AgentValidator()

        # Add parameter validator
        def validate_required_params(agent):
            if hasattr(agent, "parameters") and agent.parameters:
                required_params = []
                for param in agent.parameters.params:
                    if hasattr(param, "value") and param.value == "required":
                        required_params.append(param.name)

                # Store for later validation when agent is instantiated
                agent._required_params = required_params

        validator.add_validator("agent", validate_required_params)

        content = """
        agent RequiredParamsAgent {
            name: "Agent with required params"

            parameters {
                api_key: required
                optional_param: "default_value"
            }
        }
        """
        model = parser.parse(content)
        validator.validate(model)

        # Check that required params were identified
        agent = model.agents[0]
        assert hasattr(agent, "_required_params")
        assert "api_key" in agent._required_params

    def test_validate_capability_names(self):
        """Test validating capability names."""
        parser = AgentParser()
        validator = AgentValidator()

        # Define allowed capabilities
        allowed_capabilities = {
            "search_web",
            "extract_content",
            "summarize",
            "natural_language_processing",
            "code_generation",
            "data_analysis",
        }

        def validate_capabilities(agent):
            if hasattr(agent, "capabilities"):
                for cap in agent.capabilities.capabilities:
                    if cap.name not in allowed_capabilities:
                        raise ValueError(f"Unknown capability: {cap.name}")

        validator.add_validator("agent", validate_capabilities)

        # Test with unknown capability
        content = """
        agent UnknownCapability {
            name: "Agent with unknown capability"

            capabilities [
                search_web,
                unknown_capability
            ]
        }
        """
        model = parser.parse(content)

        with pytest.raises(AgentaraValidationError) as exc_info:
            validator.validate(model)

        assert "Unknown capability" in str(exc_info.value)

    def test_validate_rate_limit_format(self):
        """Test validating rate limit format."""
        parser = AgentParser()
        validator = AgentValidator()

        def validate_rate_limits(agent):
            if hasattr(agent, "rules"):
                for rule in agent.rules.rules:
                    if hasattr(rule.value, "count") and hasattr(rule.value, "period"):
                        # Validate rate limit
                        if rule.value.count <= 0:
                            raise ValueError("Rate limit count must be positive")

                        valid_periods = ["second", "minute", "hour", "day"]
                        if rule.value.period not in valid_periods:
                            raise ValueError(f"Invalid rate limit period: {rule.value.period}")

        validator.add_validator("agent", validate_rate_limits)

        # This should pass
        content = """
        agent RateLimitedAgent {
            name: "Rate limited agent"

            rules {
                rate_limit: 10/minute
            }
        }
        """
        model = parser.parse(content)
        validator.validate(model)  # Should not raise

    def test_validate_workflow_agent_references(self):
        """Test validating workflow agent references."""
        parser = AgentParser()
        AgentValidator()

        # Add workflow validator as a model processor
        def validate_workflow_references(model, metamodel=None):
            if hasattr(model, "workflows"):
                agent_names = {agent.name for agent in model.agents}

                for workflow in model.workflows:
                    # Check that all referenced agents exist
                    for agent_ref in workflow.agents:
                        if agent_ref.name not in agent_names:
                            raise ValueError(f"Workflow references unknown agent: {agent_ref.name}")

        # For model-level validation, we need to validate after parsing
        content = """
        agent ExistingAgent {
            name: "Existing Agent"
        }

        workflow TestWorkflow {
            agents: [ExistingAgent, NonExistentAgent]
        }
        """

        # textX will automatically validate references during parsing
        with pytest.raises(AgentaraParseError) as exc_info:
            parser.parse(content)

        assert "Unknown object" in str(exc_info.value)
        assert "NonExistentAgent" in str(exc_info.value)

    def test_multiple_validators_on_same_object(self):
        """Test multiple validators on the same object type."""
        parser = AgentParser()
        validator = AgentValidator()

        # Add multiple validators
        validator.add_validator("agent", lambda a: None)  # Pass-through
        validator.add_validator("agent", lambda a: None)  # Pass-through

        def failing_validator(agent):
            raise ValueError("This validator always fails")

        validator.add_validator("agent", failing_validator)

        content = """
        agent TestAgent {
            name: "Test Agent"
        }
        """
        model = parser.parse(content)

        with pytest.raises(AgentaraValidationError) as exc_info:
            validator.validate(model)

        assert "always fails" in str(exc_info.value)
