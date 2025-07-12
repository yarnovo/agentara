// Workflow Example
// This example demonstrates how to define multiple agents and connect them in a workflow

// First, define individual agents
agent DataCollector {
    name: "Data Collector"
    description: "Collects data from various sources"
    version: "1.0.0"
    
    capabilities [
        fetch_api_data,
        scrape_web,
        read_files
    ]
    
    parameters {
        sources: required
        format: "json"
        batch_size: 100
    }
}

agent DataProcessor {
    name: "Data Processor"
    description: "Processes and transforms collected data"
    version: "1.0.0"
    
    capabilities [
        clean_data,
        transform_data,
        validate_data
    ]
    
    parameters {
        validation_rules: required
        output_format: "parquet"
    }
}

agent DataAnalyzer {
    name: "Data Analyzer"
    description: "Analyzes processed data and generates insights"
    version: "1.0.0"
    
    capabilities [
        statistical_analysis,
        trend_detection,
        anomaly_detection,
        report_generation
    ]
    
    parameters {
        analysis_type: "comprehensive"
        confidence_level: 0.95
        report_format: "html"
    }
}

agent ReportPublisher {
    name: "Report Publisher"
    description: "Publishes analysis reports to various channels"
    version: "1.0.0"
    
    capabilities [
        send_email,
        post_to_slack,
        save_to_cloud
    ]
    
    parameters {
        recipients: required
        channels: required
    }
}

// Define the workflow connecting the agents
workflow DataAnalysisPipeline {
    agents: [DataCollector, DataProcessor, DataAnalyzer, ReportPublisher]
    
    flow {
        DataCollector -> DataProcessor
        DataProcessor -> DataAnalyzer
        DataAnalyzer -> ReportPublisher
    }
}