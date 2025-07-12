// Simple Agent Example
// This is a basic agent definition showing minimal required syntax

agent SimpleWebSearcher {
    name: "Simple Web Searcher"
    description: "A basic agent that searches the web"
    version: "1.0.0"
    
    capabilities [
        search_web,
        extract_content
    ]
}