"""Exception classes for Agentara."""


class AgentaraError(Exception):
    """Base exception for all Agentara errors."""

    pass


class AgentaraValidationError(AgentaraError):
    """Raised when Agent validation fails."""

    pass


class AgentaraParseError(AgentaraError):
    """Raised when DSL parsing fails."""

    pass
