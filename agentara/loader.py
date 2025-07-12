"""Loader functions for Agentara."""

from pathlib import Path
from typing import Any

from .exceptions import AgentaraError
from .parser import AgentParser
from .validator import AgentValidator


def load_agent_from_str(content: str, validate: bool = True) -> Any:
    """
    Load and parse Agent from DSL string.

    Args:
        content: DSL string content
        validate: Whether to validate after parsing

    Returns:
        Parsed model object

    Raises:
        AgentaraError: If parsing or validation fails
    """
    parser = AgentParser()

    try:
        model = parser.parse(content)

        if validate:
            validator = AgentValidator()
            validator.validate(model)

        return model
    except Exception as e:
        raise AgentaraError(f"Failed to load agent: {e}") from e


def load_agent_from_file(file_path: str | Path, validate: bool = True) -> Any:
    """
    Load and parse Agent from DSL file.

    Args:
        file_path: Path to DSL file
        validate: Whether to validate after parsing

    Returns:
        Parsed model object

    Raises:
        AgentaraError: If file reading, parsing or validation fails
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise AgentaraError(f"File not found: {file_path}")

    try:
        content = file_path.read_text(encoding="utf-8")
        return load_agent_from_str(content, validate)
    except Exception as e:
        raise AgentaraError(f"Failed to load agent from file: {e}") from e
