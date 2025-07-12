"""Parser module for Agentara DSL using Lark."""

from pathlib import Path

from lark import Lark, Transformer, v_args
from lark.exceptions import UnexpectedEOF, UnexpectedInput, UnexpectedToken


class AgentTransformer(Transformer):
    """Transform Lark parse tree into Python objects."""

    @v_args(inline=True)
    def model(self, *agents):
        """Transform model node."""
        return {"agents": list(agents)}

    @v_args(inline=True)
    def agent(self, agent_id, *properties):
        """Transform agent node."""
        props = {}
        for prop in properties:
            if isinstance(prop, dict):
                props.update(prop)
        return {"id": str(agent_id), "properties": props}

    @v_args(inline=True)
    def property(self, prop_name, prop_value):
        """Transform property node."""
        return {str(prop_name): prop_value}

    @v_args(inline=True)
    def name(self):
        return "name"

    @v_args(inline=True)
    def system_prompt(self):
        return "system_prompt"

    @v_args(inline=True)
    def model_provider(self):
        return "model_provider"

    @v_args(inline=True)
    def model_name(self):
        return "model_name"

    @v_args(inline=True)
    def temperature(self):
        return "temperature"

    @v_args(inline=True)
    def max_tokens(self):
        return "max_tokens"

    @v_args(inline=True)
    def description(self):
        return "description"

    @v_args(inline=True)
    def property_value(self, value):
        """Transform property value."""
        return value

    def STRING(self, token):
        """Transform string token."""
        return str(token).strip('"')

    def NUMBER(self, token):
        """Transform number token."""
        value = str(token)
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            return value

    def ID(self, token):
        """Transform ID token."""
        return str(token)


class AgentParser:
    """Parser for Agent DSL files using Lark."""

    def __init__(self, grammar_file: Path | None = None):
        """
        Initialize the parser with grammar.

        Args:
            grammar_file: Optional path to grammar file. If not provided,
                         uses the default agent.lark grammar.
        """
        if grammar_file is None:
            grammar_file = Path(__file__).parent / "grammar" / "agent.lark"

        try:
            if grammar_file.exists():
                with open(grammar_file) as f:
                    grammar_content = f.read()
            else:
                # Fallback to embedded grammar
                grammar_content = self._get_embedded_grammar()

            # Create Lark parser
            self.parser = Lark(grammar_content, parser="lalr", start="start")
            self.transformer = AgentTransformer()

        except Exception as e:
            raise Exception(f"Failed to initialize parser: {e}") from e

    def _get_embedded_grammar(self):
        """Get embedded grammar as fallback."""
        return """
// Agentara DSL Grammar Definition for Lark
// Simplified grammar for AI Agent definitions

?start: model

model: agent*

agent: "agent" ID "{" property* "}"

property: property_name ":" property_value

property_name: "name" -> name
            | "system_prompt" -> system_prompt
            | "model_provider" -> model_provider
            | "model_name" -> model_name
            | "temperature" -> temperature
            | "max_tokens" -> max_tokens
            | "description" -> description

property_value: STRING | NUMBER | ID

// Terminals
ID: /[a-zA-Z_][a-zA-Z0-9_]*/
STRING: /\"[^\"]*\"/
NUMBER: /\\d+(\\.\\d+)?/

// Comments and whitespace
COMMENT: /\\/\\/[^\\n]*/
%ignore COMMENT
%ignore /\\s+/
"""

    def parse(self, content: str) -> dict[str, list]:
        """
        Parse Agent DSL content.

        Args:
            content: DSL string to parse

        Returns:
            Dictionary with list of agents

        Raises:
            Exception: If parsing fails
        """
        try:
            # Handle empty content
            if not content.strip():
                return {"agents": []}

            # Parse with Lark
            tree = self.parser.parse(content)

            # Transform to model objects
            result = self.transformer.transform(tree)

            return result

        except UnexpectedToken as e:
            # Convert Lark error to our custom error
            line = e.line
            column = e.column
            expected = e.expected
            message = f"Syntax error at line {line}, column {column}: expected {expected}"
            raise Exception(message) from e
        except UnexpectedEOF as e:
            raise Exception("Unexpected end of file") from e
        except UnexpectedInput as e:
            raise Exception(f"Unexpected input: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to parse DSL: {e}") from e
