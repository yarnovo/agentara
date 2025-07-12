"""Registry for validators and processors."""

from collections.abc import Callable

# Global registries
_validators: dict[str, list[Callable]] = {}
_processors: dict[str, list[Callable]] = {}


def register_validator(obj_type: str):
    """
    Decorator to register a validator function.

    Usage:
        @register_validator("agent")
        def validate_agent_name(agent):
            if not agent.name.isalnum():
                raise ValueError("Invalid agent name")
    """

    def decorator(func: Callable) -> Callable:
        if obj_type not in _validators:
            _validators[obj_type] = []
        _validators[obj_type].append(func)
        return func

    return decorator


def register_processor(obj_type: str):
    """
    Decorator to register a processor function.

    Usage:
        @register_processor("model")
        def process_model(model, metamodel):
            # Process model after parsing
            pass
    """

    def decorator(func: Callable) -> Callable:
        if obj_type not in _processors:
            _processors[obj_type] = []
        _processors[obj_type].append(func)
        return func

    return decorator


def get_validators(obj_type: str) -> list[Callable]:
    """Get all validators for a specific object type."""
    return _validators.get(obj_type, [])


def get_processors(obj_type: str) -> list[Callable]:
    """Get all processors for a specific object type."""
    return _processors.get(obj_type, [])


def clear_registry():
    """Clear all registered validators and processors. Useful for testing."""
    _validators.clear()
    _processors.clear()
