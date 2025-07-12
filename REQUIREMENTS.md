# Agentara 项目需求文档

## 项目概述

Agentara 是一个轻量级的 AI Agent DSL（领域特定语言）解析库，使用 Lark 解析器实现。

## 核心需求

### 1. DSL 语法定义
- 提供简单清晰的语法来定义 AI Agent
- 支持基本的 Agent 属性配置
- 使用 Lark 的 EBNF 语法定义

### 2. 解析功能
- 将 DSL 文本解析为结构化数据
- 提供清晰的错误信息和位置定位
- 支持注释和空白符处理

### 3. 最小化设计
- 保持代码简单，只提供核心解析功能
- 最小化依赖，只依赖 Lark 解析器
- 不包含验证器、加载器等额外功能

## 支持的 Agent 属性

- `name`: Agent 显示名称
- `description`: Agent 描述
- `system_prompt`: 系统提示词
- `model_provider`: 模型提供商（如 openai、anthropic）
- `model_name`: 模型名称（如 gpt-4、claude-3）
- `temperature`: 温度参数
- `max_tokens`: 最大 token 数

## 技术选型

- **语言**: Python 3.12+
- **解析器**: Lark（取代 textX）
- **选择 Lark 的理由**:
  - 设计理念与项目需求相符
  - 社区活跃，使用广泛
  - 文档完善，易于维护
  - 性能优秀，支持多种解析算法

## 项目结构

```
agentara/
├── agentara/
│   ├── __init__.py      # 包导出
│   ├── parser.py        # 解析器实现
│   └── grammar/
│       └── agent.lark   # 语法定义
├── examples/            # 示例 DSL 文件
└── README.md           # 项目文档
```

## 使用方式

```python
from agentara import AgentParser

parser = AgentParser()
result = parser.parse(dsl_content)
# result 包含解析后的 agents 列表
```

## 项目目标

1. 提供简单可靠的 DSL 解析功能
2. 保持代码最小化和易维护性
3. 为 AI Agent 定义提供标准化格式