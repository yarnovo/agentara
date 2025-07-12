# Agentara

基于 textX DSL 的 AI Agent 定义和验证 Python 库。

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 项目概述

Agentara 是一个 Python 库，提供了基于 DSL（领域特定语言）的 AI Agent 定义和验证功能。通过使用 [textX](https://github.com/textX/textX) 作为底层解析引擎，Agentara 让开发者能够：

- 使用清晰的 DSL 语法定义 AI Agent
- 自动验证 Agent 定义的正确性
- 在 Python 程序中集成和使用 Agent
- 为 AI 系统提供标准化的 Agent 规范

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

## 安装

```bash
pip install agentara
```

### 开发安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/agentara.git
cd agentara

# 安装开发依赖
pip install -e ".[dev]"
```

## 快速开始

### 作为库使用

```python
from agentara import AgentParser, AgentValidator, AgentaraParseError

# 创建解析器和验证器
parser = AgentParser()
validator = AgentValidator()

# 定义 Agent
agent_dsl = """
agent WebSearcher {
    name: "Web Search Agent"
    description: "Searches the web for information"
    version: "1.0.0"
    
    capabilities [
        search_web,
        extract_content,
        summarize
    ]
    
    parameters {
        max_results: 10
        timeout: 30
        api_key: required
    }
    
    rules {
        on_error: retry(3)
        rate_limit: 10/minute
    }
}
"""

# 解析和验证
try:
    # 解析 DSL
    model = parser.parse(agent_dsl)
    
    # 验证语义规则
    validator.validate(model)
    
    # 获取 Agent 对象
    agents = model.agents
    for agent in agents:
        print(f"Agent: {agent.name}")
        if hasattr(agent, 'properties'):
            for prop in agent.properties:
                if prop.name == 'version':
                    print(f"Version: {prop.value}")
        if hasattr(agent, 'capabilities') and agent.capabilities:
            print(f"Capabilities: {[cap.name for cap in agent.capabilities.capabilities]}")
        
except AgentaraParseError as e:
    print(f"解析错误: {e}")
except Exception as e:
    print(f"验证错误: {e}")
```

### 从文件加载

```python
from agentara import load_agent_from_file

# 从文件加载并验证
try:
    agent_model = load_agent_from_file("path/to/agent.dsl")
    print(f"成功加载 {len(agent_model.agents)} 个 Agent")
except Exception as e:
    print(f"加载失败: {e}")
```

### 自定义验证规则

```python
from agentara import register_validator

# 注册自定义验证器
@register_validator("agent")
def validate_agent_name(agent):
    """验证 Agent 名称规范"""
    if not agent.name.replace("_", "").isalnum():
        raise ValueError(
            f"Agent 名称只能包含字母、数字和下划线: {agent.name}"
        )

@register_validator("capability")
def validate_capability(capability):
    """验证能力定义"""
    allowed_capabilities = [
        "search_web", "extract_content", "summarize",
        "code_generation", "data_analysis"
    ]
    if capability.name not in allowed_capabilities:
        raise ValueError(
            f"未知的能力类型: {capability.name}"
        )
```

## 项目结构

```
agentara/
├── agentara/              # 核心库
│   ├── __init__.py       # 包导出定义
│   ├── exceptions.py     # 自定义异常类
│   ├── grammar/          # DSL 语法定义
│   │   └── agent.tx      # Agent DSL 语法
│   ├── loader.py         # 文件加载器
│   ├── parser.py         # 解析器实现
│   ├── registry.py       # 验证器和处理器注册
│   └── validator.py      # 验证器实现
├── examples/             # 示例 Agent 定义
├── tests/               # 测试用例
│   ├── unit/            # 单元测试
│   └── e2e/             # 端到端测试
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
    
    capabilities [
        natural_language_processing,
        code_generation(
            language("python"),
            max_lines(1000)
        ),
        data_analysis
    ]
    
    parameters {
        model: "gpt-4"
        temperature: 0.7
        max_tokens: 2000
        api_key: required
    }
    
    rules {
        on_error: retry(3)
        rate_limit: 60/hour
        timeout: 30
    }
}

// 工作流定义
workflow DataPipeline {
    agents: [DataCollector, DataProcessor, DataAnalyzer]
    
    flow {
        DataCollector -> DataProcessor
        DataProcessor -> DataAnalyzer
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

## API 参考

### 核心类

- `AgentParser`: DSL 解析器
- `AgentValidator`: 语义验证器
- `AgentaraError`: 基础异常类
- `AgentaraParseError`: 解析错误异常
- `AgentaraValidationError`: 验证错误异常

### 工具函数

- `load_agent_from_file()`: 从文件加载 Agent
- `load_agent_from_str()`: 从字符串加载 Agent
- `register_validator()`: 注册自定义验证器
- `register_processor()`: 注册模型处理器
- `clear_registry()`: 清空注册的验证器和处理器（用于测试）

## 开发路线图

- [x] 完成基础 DSL 语法定义
- [x] 实现核心解析器和验证器
- [x] 支持自定义验证规则
- [x] 实现模型处理器
- [x] 完整的测试覆盖
- [ ] 开发代码生成器
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