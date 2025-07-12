// Multi-Agent System Example
// This example shows a complex system with multiple specialized agents

// Orchestrator agent that coordinates other agents
agent Orchestrator {
    name: "System Orchestrator"
    description: "Manages and coordinates all other agents"
    version: "1.0.0"
    
    capabilities [
        task_distribution,
        agent_monitoring,
        result_aggregation,
        error_handling
    ]
    
    rules {
        on_error: retry(3)
        timeout: 300
        max_concurrent: 10
    }
}

// Specialized agents for different tasks
agent NLPAgent {
    name: "Natural Language Processor"
    description: "Handles all NLP-related tasks"
    version: "1.5.0"
    
    capabilities [
        text_classification,
        named_entity_recognition,
        sentiment_analysis,
        language_translation(languages("en", "es", "fr", "de", "zh"))
    ]
    
    parameters {
        model: "bert-large"
        max_sequence_length: 512
        batch_size: 32
    }
}

agent CodeGenerationAgent {
    name: "Code Generator"
    description: "Generates code in multiple programming languages"
    version: "2.0.0"
    
    capabilities [
        generate_python,
        generate_javascript,
        generate_typescript,
        code_review,
        refactor_code
    ]
    
    parameters {
        model: "codex"
        temperature: 0.3
        max_tokens: 4000
        style_guide: required
    }
    
    rules {
        rate_limit: 50/hour
        on_error: fallback("simpler_model")
    }
}

agent DataScienceAgent {
    name: "Data Science Assistant"
    description: "Performs data analysis and machine learning tasks"
    version: "1.2.0"
    
    capabilities [
        exploratory_data_analysis,
        feature_engineering,
        model_training(algorithms("random_forest", "xgboost", "neural_network")),
        model_evaluation,
        hyperparameter_tuning
    ]
    
    parameters {
        framework: "scikit-learn"
        gpu_enabled: true
        memory_limit: "16GB"
    }
}

agent SecurityAgent {
    name: "Security Monitor"
    description: "Monitors and ensures security compliance"
    version: "1.0.0"
    
    capabilities [
        vulnerability_scanning,
        access_control,
        audit_logging,
        threat_detection
    ]
    
    parameters {
        scan_frequency: "continuous"
        alert_threshold: "medium"
        compliance_standards: required
    }
    
    rules {
        priority: "critical"
        on_threat: notify("security_team")
    }
}

// Workflow for code development tasks
workflow CodeDevelopmentFlow {
    agents: [Orchestrator, NLPAgent, CodeGenerationAgent, SecurityAgent]
    
    flow {
        Orchestrator -> NLPAgent
        NLPAgent -> CodeGenerationAgent
        CodeGenerationAgent -> SecurityAgent
        SecurityAgent -> Orchestrator
    }
}

// Workflow for data analysis tasks
workflow DataAnalysisFlow {
    agents: [Orchestrator, DataScienceAgent, NLPAgent]
    
    flow {
        Orchestrator -> DataScienceAgent
        DataScienceAgent -> NLPAgent
        NLPAgent -> Orchestrator
    }
}