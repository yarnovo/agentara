# Agentara

基于 textX DSL 的 AI Agent 生成框架，通过标准化的领域特定语言定义和验证 AI Agent。

## 项目概述

Agentara 是一个创新的框架，旨在解决 AI 生成 Agent 时的标准化和规范性问题。通过使用 [textX](https://github.com/textX/textX) 库定义清晰的 DSL（领域特定语言），确保 AI 生成的 Agent 符合预定义的标准格式。

## 核心特性

- 🎯 **标准化 DSL**：使用 textX 定义 Agent 的标准语法
- ✅ **自动验证**：解析即验证，确保生成内容符合规范
- 🚀 **AI 友好**：清晰的错误提示，帮助 AI 快速修正
- 🔧 **灵活扩展**：支持自定义验证规则和业务逻辑
- 📝 **完整工具链**：提供解析器、验证器和代码生成器

## 技术背景

### 为什么选择 textX？

textX 是一个成熟的 Python DSL 框架，具有以下优势：

- **语法清晰**：基于 PEG 语法，定义直观易懂
- **错误提示精确**：提供准确的错误位置和期望内容
- **解析即验证**：解析过程自动完成基础验证
- **易于扩展**：支持自定义处理器和验证规则

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/agentara.git
cd agentara

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -e .
```

### 基本使用

```python
from agentara import AgentParser

# 创建解析器
parser = AgentParser()

# 定义 Agent
agent_definition = """
agent WebSearcher {
    name: "Web Search Agent"
    description: "Searches the web for information"
    
    capabilities {
        - search_web
        - extract_content
        - summarize
    }
    
    parameters {
        max_results: 10
        timeout: 30
    }
}
"""

# 解析和验证
try:
    agent = parser.parse(agent_definition)
    print(f"成功解析 Agent: {agent.name}")
except Exception as e:
    print(f"解析错误: {e}")
```

## 项目结构

```
agentara/
├── agentara/              # 核心库
│   ├── __init__.py
│   ├── grammar/          # DSL 语法定义
│   │   └── agent.tx      # Agent DSL 语法
│   ├── parser.py         # 解析器实现
│   ├── validators/       # 验证器
│   └── generators/       # 代码生成器
├── examples/             # 示例 Agent 定义
├── tests/               # 测试用例
├── research/            # 技术调研文档
└── docs/               # 项目文档
```

## DSL 语法示例

Agent DSL 支持以下特性：

```
// 基本 Agent 定义
agent BasicAgent {
    name: "Simple Agent"
    version: "1.0.0"
}

// 带有能力和参数的 Agent
agent AdvancedAgent {
    name: "Advanced AI Agent"
    description: "Multi-capability agent"
    
    capabilities {
        - natural_language_processing
        - code_generation
        - data_analysis
    }
    
    parameters {
        model: "gpt-4"
        temperature: 0.7
        max_tokens: 2000
    }
    
    rules {
        // 定义行为规则
        on_error: retry(3)
        timeout: 60
    }
}

// Agent 组合
workflow DataPipeline {
    agents: [DataCollector, DataProcessor, DataAnalyzer]
    
    flow {
        DataCollector -> DataProcessor -> DataAnalyzer
    }
}
```

## 验证机制

Agentara 提供多层次的验证：

1. **语法验证**：自动检查 DSL 语法正确性
2. **语义验证**：验证业务规则和约束
3. **引用验证**：确保所有引用的资源存在
4. **自定义验证**：支持添加特定的验证规则

```python
# 添加自定义验证
from agentara.validators import register_validator

@register_validator("agent")
def validate_agent_name(agent):
    if not agent.name.isalnum():
        raise ValueError(f"Agent 名称只能包含字母和数字: {agent.name}")
```

## 工具链

### 命令行工具

```bash
# 验证 Agent 定义
agentara validate agent.dsl

# 生成代码
agentara generate agent.dsl --output agent.py

# 交互式 Agent 设计器
agentara designer
```

### API 集成

```python
from agentara import AgentRegistry

# 注册 Agent
registry = AgentRegistry()
registry.register_from_file("agents/web_searcher.dsl")

# 获取并使用 Agent
agent = registry.get("WebSearcher")
result = agent.execute(task="Search for Python tutorials")

```

## 开发路线图

- [ ] 完成基础 DSL 语法定义
- [ ] 实现核心解析器和验证器
- [ ] 开发代码生成器
- [ ] 创建 CLI 工具
- [ ] 编写完整文档
- [ ] 发布第一个版本

## 贡献指南

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 相关文档

- [项目需求](REQUIREMENTS.md) - 详细的项目需求说明
- [textX 调研报告](research/textX_research_report.md) - textX 库的技术调研
- [架构设计](ARCHITECTURE.md) - 系统架构设计文档
- [API 文档](docs/api.md) - 完整的 API 参考

## 许可证

MIT License