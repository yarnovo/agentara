"""Parser module for Agentara DSL."""

from pathlib import Path

from textx import metamodel_from_file, metamodel_from_str

from .exceptions import AgentaraParseError
from .registry import get_processors


class AgentParser:
    """Parser for Agent DSL files."""

    def __init__(self, grammar_file: Path | None = None):
        """
        Initialize the parser with grammar.

        Args:
            grammar_file: Optional path to grammar file. If not provided,
                         uses the default agent.tx grammar.
        """
        if grammar_file is None:
            # Use default grammar file
            grammar_file = Path(__file__).parent / "grammar" / "agent.tx"

        try:
            if grammar_file.exists():
                self.metamodel = metamodel_from_file(str(grammar_file))
            else:
                # Fallback to embedded grammar
                self._init_with_embedded_grammar()
        except Exception as e:
            raise AgentaraParseError(f"Failed to initialize parser: {e}") from e

        # Register processors
        self._register_processors()

    def _init_with_embedded_grammar(self):
        """Initialize with embedded grammar as fallback."""
        grammar = """
        Model:
            agents*=Agent
            workflows*=Workflow
        ;

        Agent:
            'agent' name=ID '{'
                properties*=Property
                capabilities=Capabilities?
                parameters=Parameters?
                rules=Rules?
            '}'
        ;

        Property:
            name=PropertyName ':' value=STRING
        ;

        PropertyName:
            'name' | 'description' | 'version' | 'author' | 'tags'
        ;

        Capabilities:
            'capabilities' '['
                capabilities+=Capability[',']
            ']'
        ;

        Capability:
            name=/[a-zA-Z_][a-zA-Z0-9_]*/
        ;

        Parameters:
            'parameters' '{'
                params+=ParameterDef
            '}'
        ;

        ParameterDef:
            name=/[a-zA-Z_][a-zA-Z0-9_]*/ ':' (value=Value | 'required')
        ;

        Value:
            STRING | INT | FLOAT | BOOL | ID
        ;

        Rules:
            'rules' '{'
                rules+=Rule
            '}'
        ;

        Rule:
            name=/[a-zA-Z_][a-zA-Z0-9_]*/ ':' value=RuleValue
        ;

        RuleValue:
            FunctionCall | RateLimit | STRING | INT | ID
        ;

        RateLimit:
            count=INT '/' period=Period
        ;

        Period:
            'second' | 'minute' | 'hour' | 'day'
        ;

        FunctionCall:
            name=ID '(' args+=Value[','] ')'
        ;

        Workflow:
            'workflow' name=ID '{'
                'agents' ':' '[' agents+=ID[','] ']'
            '}'
        ;

        Comment: /\\/\\/.*$/;
        """
        self.metamodel = metamodel_from_str(grammar)

    def _register_processors(self):
        """Register all processors from the registry."""
        # Register model processors
        for processor in get_processors("model"):
            self.metamodel.register_model_processor(processor)

        # Register object processors
        for obj_type in ["agent", "capability", "parameter"]:
            processors = get_processors(obj_type)
            if processors:
                self.metamodel.register_obj_processors({obj_type.capitalize(): processor for processor in processors})

    def parse(self, content: str):
        """
        Parse Agent DSL content.

        Args:
            content: DSL string to parse

        Returns:
            Parsed model object

        Raises:
            AgentaraParseError: If parsing fails
        """
        try:
            model = self.metamodel.model_from_str(content)

            # Handle empty model case - textX returns empty string for completely empty input
            if isinstance(model, str) and not model.strip():
                # Create an empty model object with required attributes
                class EmptyModel:
                    def __init__(self):
                        self.agents = []
                        self.workflows = []

                return EmptyModel()

            return model
        except Exception as e:
            raise AgentaraParseError(f"Failed to parse DSL: {e}") from e
