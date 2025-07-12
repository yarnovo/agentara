// Advanced Agent Example
// This example shows all available features of the Agent DSL

agent AdvancedAIAssistant {
    name: "Advanced AI Assistant"
    description: "A fully-featured AI assistant with multiple capabilities"
    version: "2.0.0"
    author: "Agentara Team"
    tags: "ai, assistant, nlp, code-generation"
    
    // Define agent capabilities with parameters
    capabilities [
        natural_language_processing,
        code_generation(language("python"), style("pep8")),
        data_analysis(format("pandas"), visualization("matplotlib")),
        search_web,
        extract_content,
        summarize(max_length(500))
    ]
    
    // Configuration parameters
    parameters {
        model: "gpt-4"
        temperature: 0.7
        max_tokens: 2000
        api_key: required
        timeout: 30
        retry_attempts: 3
    }
    
    // Behavioral rules
    rules {
        on_error: retry(3)
        rate_limit: 100/hour
        timeout: 60
        max_concurrent: 5
        priority: "high"
    }
}