"""Validator module for Agentara DSL."""

from collections.abc import Callable
from typing import Any

from .exceptions import AgentaraValidationError


class AgentValidator:
    """Validator for Agent models."""

    def __init__(self):
        """Initialize the validator."""
        self._validators: dict[str, list[Callable]] = {}

    def validate(self, model: Any) -> None:
        """
        Validate an Agent model.

        Args:
            model: The parsed model to validate

        Raises:
            AgentaraValidationError: If validation fails
        """
        # Validate all agents in the model
        if hasattr(model, "agents"):
            for agent in model.agents:
                self._validate_agent(agent)

    def _validate_agent(self, agent: Any) -> None:
        """Validate a single agent."""
        # Basic validation
        if not hasattr(agent, "name") or not agent.name:
            raise AgentaraValidationError("Agent must have a name")

        # Run registered validators
        agent_validators = self._validators.get("agent", [])
        for validator in agent_validators:
            try:
                validator(agent)
            except Exception as e:
                raise AgentaraValidationError(f"Validation failed for agent '{agent.name}': {e}") from e

    def add_validator(self, obj_type: str, validator: Callable) -> None:
        """Add a validator for a specific object type."""
        if obj_type not in self._validators:
            self._validators[obj_type] = []
        self._validators[obj_type].append(validator)
