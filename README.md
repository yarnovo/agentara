# Agentara

基于 Lark 解析器的 AI Agent DSL（领域特定语言）解析库。

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 项目概述

Agentara 是一个轻量级的 Python 库，用于解析 AI Agent 定义的 DSL。通过简单的语法，你可以定义 AI Agent 的基本配置，包括系统提示词、模型提供商、模型名称等参数。

## 特性

- 🎯 **简单语法**：专注于 AI Agent 的核心配置
- 📝 **清晰结构**：使用 Lark 解析器实现可靠的语法解析
- 🚀 **轻量级**：最小化依赖，只需要 Lark 解析器
- 🔧 **易于扩展**：基于标准的 EBNF 语法定义

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

### 基本使用

```python
from agentara import AgentParser

# 定义 Agent DSL
agent_dsl = """
agent Assistant {
    name: "AI Assistant"
    description: "General purpose AI assistant"
    system_prompt: "You are a helpful AI assistant."
    model_provider: "openai"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
}
"""

# 创建解析器并解析
parser = AgentParser()
result = parser.parse(agent_dsl)

# 访问解析结果
for agent in result["agents"]:
    print(f"Agent ID: {agent['id']}")
    print(f"Properties: {agent['properties']}")
```

### 从文件加载

```python
from agentara import AgentParser

# 创建解析器
parser = AgentParser()

# 从文件读取并解析
with open("agents.dsl", "r") as f:
    content = f.read()
    result = parser.parse(content)

# 处理结果
for agent in result["agents"]:
    props = agent["properties"]
    print(f"Agent: {agent['id']}")
    print(f"  Model: {props.get('model_provider')}/{props.get('model_name')}")
    print(f"  Temperature: {props.get('temperature')}")
```

## DSL 语法

Agentara 使用简单直观的语法定义 AI Agent：

```
agent AgentName {
    property_name: value
    ...
}
```

### 支持的属性

- `name`: Agent 的显示名称（字符串）
- `description`: Agent 的描述（字符串）
- `system_prompt`: 系统提示词（字符串）
- `model_provider`: 模型提供商，如 "openai"、"anthropic"（字符串或标识符）
- `model_name`: 模型名称，如 "gpt-4"、"claude-3-opus"（字符串或标识符）
- `temperature`: 温度参数（数字，0.0-2.0）
- `max_tokens`: 最大 token 数（整数）

### 示例

```dsl
// 客服 Agent
agent CustomerService {
    name: "Customer Service Agent"
    description: "Handles customer inquiries"
    system_prompt: "You are a helpful customer service representative."
    model_provider: "openai"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
}

// 翻译 Agent
agent Translator {
    name: "Language Translator"
    system_prompt: "You are a professional translator."
    model_provider: "anthropic"
    model_name: "claude-3-sonnet"
    temperature: 0.3
    max_tokens: 3000
}
```

## API 参考

### AgentParser

主要的解析器类。

```python
parser = AgentParser(grammar_file=None)
```

参数：
- `grammar_file` (可选): 自定义语法文件路径。如果不提供，使用内置语法。

### parser.parse(content)

解析 DSL 内容。

参数：
- `content`: DSL 字符串内容

返回：
- 字典，包含 `agents` 列表，每个 agent 包含 `id` 和 `properties`

抛出：
- `Exception`: 解析失败时抛出异常，包含错误位置信息

## 项目结构

```
agentara/
├── agentara/           # 核心库
│   ├── __init__.py    # 包导出
│   ├── parser.py      # Lark 解析器实现
│   └── grammar/       # 语法定义
│       └── agent.lark # Lark 语法文件
├── examples/          # 示例文件
├── tests/            # 测试用例
└── README.md         # 本文档
```

## 依赖

- Python 3.12+
- lark >= 1.1.0

## 许可证

MIT License