"""Test cases for registry functions."""

import typing

import pytest

from agentara import clear_registry, register_processor, register_validator
from agentara.registry import get_processors, get_validators


class TestRegistry:
    """Test cases for validator and processor registry."""

    def setup_method(self):
        """Clear registry before each test."""
        clear_registry()

    def teardown_method(self):
        """Clear registry after each test."""
        clear_registry()

    def test_register_validator(self):
        """Test registering a validator."""

        @register_validator("agent")
        def test_validator(agent):
            pass

        validators = get_validators("agent")
        assert len(validators) == 1
        assert validators[0].__name__ == "test_validator"

    def test_register_multiple_validators(self):
        """Test registering multiple validators for same type."""

        @register_validator("agent")
        def validator1(agent):
            pass

        @register_validator("agent")
        def validator2(agent):
            pass

        validators = get_validators("agent")
        assert len(validators) == 2

    def test_register_validators_different_types(self):
        """Test registering validators for different types."""

        @register_validator("agent")
        def agent_validator(agent):
            pass

        @register_validator("capability")
        def capability_validator(capability):
            pass

        assert len(get_validators("agent")) == 1
        assert len(get_validators("capability")) == 1
        assert len(get_validators("unknown")) == 0

    def test_register_processor(self):
        """Test registering a processor."""

        @register_processor("model")
        def test_processor(model, metamodel):
            pass

        processors = get_processors("model")
        assert len(processors) == 1
        assert processors[0].__name__ == "test_processor"

    def test_validator_function_preserved(self):
        """Test that validator function is preserved after decoration."""
        call_count = 0

        @register_validator("agent")
        def counting_validator(agent):
            nonlocal call_count
            call_count += 1
            return call_count

        # Function should still work
        result = counting_validator(None)
        assert result == 1
        assert call_count == 1

    def test_processor_function_preserved(self):
        """Test that processor function is preserved after decoration."""

        @register_processor("model")
        def returning_processor(model, metamodel):
            return "processed"

        # Function should still work
        result = returning_processor(None, None)
        assert result == "processed"

    def test_empty_registry(self):
        """Test getting validators/processors from empty registry."""
        assert get_validators("agent") == []
        assert get_processors("model") == []

    def test_validator_with_complex_logic(self):
        """Test validator with complex validation logic."""

        @register_validator("agent")
        def complex_validator(agent):
            if not hasattr(agent, "name"):
                raise ValueError("Agent must have name")
            if len(agent.name) < 3:
                raise ValueError("Agent name too short")
            if not agent.name[0].isupper():
                raise ValueError("Agent name must start with uppercase")

        validators = get_validators("agent")
        assert len(validators) == 1

        # Test the validator logic
        class MockAgent:
            name = "TestAgent"

        # Should not raise
        validators[0](MockAgent())

        # Test various failure cases
        MockAgent.name = "Te"
        with pytest.raises(ValueError, match="too short"):
            validators[0](MockAgent())

        MockAgent.name = "testAgent"
        with pytest.raises(ValueError, match="uppercase"):
            validators[0](MockAgent())

    def test_processor_with_model_modification(self):
        """Test processor that modifies the model."""

        @register_processor("model")
        def modifying_processor(model, metamodel):
            # Add a processed flag
            model._processed = True
            # Count agents
            if hasattr(model, "agents"):
                model._agent_count = len(model.agents)

        processors = get_processors("model")

        # Test the processor
        class MockModel:
            agents: typing.ClassVar = [1, 2, 3]

        model_instance = MockModel()
        processors[0](model_instance, None)

        assert hasattr(model_instance, "_processed")
        assert model_instance._processed is True
        assert model_instance._agent_count == 3

    def test_multiple_decorators_same_function(self):
        """Test applying decorator multiple times to same function."""

        @register_validator("agent")
        @register_validator("capability")
        def universal_validator(obj):
            return "validated"

        # Should be registered for both types
        assert len(get_validators("agent")) == 1
        assert len(get_validators("capability")) == 1

        # Both should be the same function
        assert get_validators("agent")[0] == get_validators("capability")[0]

        # Function should still work
        assert universal_validator(None) == "validated"
