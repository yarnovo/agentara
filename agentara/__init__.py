"""Agentara - AI Agent generation framework based on textX DSL."""

# Re-export textX exceptions for convenience
from textx import TextXSemanticError, TextXSyntaxError

from .exceptions import AgentaraError, AgentaraParseError, AgentaraValidationError
from .loader import load_agent_from_file, load_agent_from_str
from .parser import AgentParser
from .registry import clear_registry, register_processor, register_validator
from .validator import AgentValidator

__version__ = "0.0.0"

__all__ = [
    "AgentParser",
    "AgentValidator",
    "AgentaraError",
    "AgentaraParseError",
    "AgentaraValidationError",
    "TextXSemanticError",
    "TextXSyntaxError",
    "clear_registry",
    "load_agent_from_file",
    "load_agent_from_str",
    "register_processor",
    "register_validator",
]
