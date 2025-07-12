# Agentara 架构设计文档

## 项目概述

Agentara 是一个基于 textX DSL（Domain Specific Language）的 AI Agent 生成框架。该框架允许用户通过声明式的 DSL 语法定义 AI Agent 的结构、能力和工作流程。

## 技术栈

- **编程语言**: Python 3.12+
- **DSL 解析器**: textX 3.0+
- **CLI 框架**: Click 8.1+
- **UI 组件**: Rich 13.0+
- **测试框架**: Pytest 7.0+
- **代码质量**: Ruff, Pyright, Pre-commit

## 项目结构

```
agentara/
├── agentara/                    # 核心库代码
│   ├── __init__.py             # 包初始化文件
│   ├── exceptions.py           # 自定义异常定义
│   ├── grammar/                # DSL 语法定义
│   │   ├── __init__.py
│   │   └── agent.tx            # textX 语法文件
│   ├── loader.py               # DSL 文件加载器
│   ├── parser.py               # DSL 解析器
│   ├── registry.py             # Agent 注册管理
│   ├── validator.py            # 模型验证器
│   └── py.typed                # PEP 561 类型标记
├── docs/                       # 文档目录
│   └── agent_dsl_prompt_for_ai.md  # DSL 使用指南
├── examples/                   # 示例文件
│   ├── simple_agent.dsl        # 简单 Agent 示例
│   ├── advanced_agent.dsl      # 高级 Agent 示例
│   ├── multi_agent_system.dsl  # 多 Agent 系统示例
│   └── workflow_example.dsl    # 工作流示例
├── tests/                      # 测试目录
│   ├── unit/                   # 单元测试
│   │   ├── test_parser.py      # 解析器测试
│   │   ├── test_validator.py   # 验证器测试
│   │   ├── test_loader.py      # 加载器测试
│   │   ├── test_registry.py    # 注册器测试
│   │   └── test_integration.py # 集成测试
│   └── e2e/                    # 端到端测试
│       ├── io/                 # 测试数据
│       └── test_runner.py      # E2E 测试运行器
├── research/                   # 研究文档
│   └── textX_research_report.md # textX 调研报告
├── pyproject.toml              # 项目配置文件
├── Makefile                    # 构建自动化
├── pytest.ini                  # Pytest 配置
└── uv.lock                     # 依赖锁文件
```

## 核心组件说明

### 1. DSL 语法层 (`grammar/`)

- **agent.tx**: 定义了 Agentara DSL 的语法规则
  - 支持 Agent 定义：名称、描述、版本、作者、标签
  - 支持 Capabilities（能力）定义：功能声明和参数配置
  - 支持 Parameters（参数）定义：输入参数类型和约束
  - 支持 Rules（规则）定义：行为规则和限流规则
  - 支持 Workflow（工作流）定义：多 Agent 协作流程

### 2. 解析层 (`parser.py`)

- **Parser 类**: 负责将 DSL 文件解析为 Python 对象模型
  - 使用 textX 进行语法解析
  - 提供解析结果的缓存机制
  - 支持错误位置追踪和友好的错误提示

### 3. 验证层 (`validator.py`)

- **Validator 类**: 负责验证解析后的模型
  - 语义验证：确保 Agent 定义的完整性
  - 引用验证：检查工作流中的 Agent 引用有效性
  - 规则验证：验证限流规则和行为规则的合法性

### 4. 加载层 (`loader.py`)

- **Loader 类**: 负责从文件系统加载 DSL 文件
  - 支持单文件和目录批量加载
  - 文件编码自动检测
  - 路径规范化处理

### 5. 注册层 (`registry.py`)

- **Registry 类**: 管理已解析的 Agent 实例
  - Agent 实例的注册和查询
  - 支持按名称、标签等条件检索
  - 提供 Agent 生命周期管理

### 6. 异常处理 (`exceptions.py`)

- 定义框架特定的异常类型
  - `ParseError`: 解析错误
  - `ValidationError`: 验证错误
  - `LoadError`: 加载错误
  - `RegistryError`: 注册错误

## 数据流

```
DSL 文件 (.dsl)
    ↓
[Loader] 加载文件内容
    ↓
[Parser] 解析 DSL 语法
    ↓
[Validator] 验证模型合法性
    ↓
[Registry] 注册 Agent 实例
    ↓
Agent 实例（可用于代码生成或运行时）
```

## 扩展性设计

### 1. 语法扩展

- 通过修改 `agent.tx` 文件可以扩展 DSL 语法
- textX 支持语法继承和模块化

### 2. 验证规则扩展

- Validator 采用规则链模式，易于添加新的验证规则
- 支持自定义验证器插件

### 3. 后端生成器扩展

- 预留了代码生成器接口
- 可以为不同的目标平台生成 Agent 实现代码

## 测试架构

### 单元测试

- 覆盖所有核心组件的功能测试
- 使用 pytest 和 pytest-cov 进行测试覆盖率分析

### 端到端测试

- 基于真实的 DSL 文件进行完整流程测试
- 包含正面和负面测试用例
- 使用 JSON 格式定义测试场景和期望结果

## 部署考虑

- 作为 Python 库发布到 PyPI
- 支持 pip 安装和依赖管理
- 提供 CLI 工具用于 DSL 文件验证和转换

## 未来规划

1. **代码生成器**: 实现将 DSL 定义转换为可执行的 Agent 代码
2. **运行时引擎**: 直接解释执行 DSL 定义的 Agent
3. **可视化编辑器**: 提供图形化的 DSL 编辑界面
4. **更多 Agent 模板**: 预定义常用的 Agent 模式和能力