// Simple Agent Example

agent CustomerService {
    name: "Customer Service Agent"
    description: "Handles customer inquiries and support"
    system_prompt: "You are a helpful customer service representative. Be polite, professional, and solve customer issues efficiently."
    model_provider: "openai"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
}

agent CodeAssistant {
    name: "Code Assistant"
    description: "Helps with programming tasks"
    system_prompt: "You are an expert programmer. Help users write clean, efficient code and debug issues."
    model_provider: "anthropic"
    model_name: "claude-3-opus"
    temperature: 0.5
    max_tokens: 4000
}