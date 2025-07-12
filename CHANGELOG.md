# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 初始项目结构搭建
- 基于 textX 的 DSL 语法定义 (`agentara/grammar/agent.tx`)
- 核心解析器实现 (`agentara/parser.py`)
- 语义验证器框架 (`agentara/validator.py`)
- 验证器和处理器注册机制 (`agentara/registry.py`)
- 文件和字符串加载器 (`agentara/loader.py`)
- 自定义异常类 (`agentara/exceptions.py`)
- 完整的单元测试套件（60个测试用例）
- 端到端测试框架
- 项目文档（README.md, REQUIREMENTS.md）
- textX 技术调研报告
- AI 友好的 DSL 语法指南

### Fixed
- 修复 DSL 语法中对下划线的支持
- 修复浮点数参数解析问题（Value 类型顺序）
- 修复 CapabilityParam 语法以支持多种值类型
- 修复测试中的注册表隔离问题
- 修复验证器的函数引用问题
- 修复必需参数的识别逻辑
- 修复工作流中的 Agent 引用验证

### Changed
- 优化了 Value 类型的解析顺序（FLOAT 优先于 STRING）
- 改进了装饰器实现，直接返回原函数而非包装器
- 更新了测试以正确处理实例属性
- 移除了不必要的 CLI 依赖（click, rich）

### Removed
- 删除了 click 依赖（命令行界面库）
- 删除了 rich 依赖（终端美化库）
- 删除了相关的间接依赖（markdown-it-py, mdurl）

## [0.0.0] - 2024-01-XX

### Added
- 项目初始版本
- 基础 DSL 语法支持
- 核心解析和验证功能
- Python 库 API

### 技术细节

#### DSL 语法特性
- **Agent 定义**：支持名称、描述、版本等属性
- **Capability**：支持参数化能力定义
- **Parameter**：支持必需参数标记（`required`）
- **Rule**：支持函数调用和速率限制（如 `10/minute`）
- **Workflow**：支持多 Agent 协作定义
- **注释**：支持单行注释（`//`）

#### 错误处理
- 精确的语法错误定位（行、列）
- 清晰的语义错误描述
- 自动的引用验证
- 友好的 AI 错误提示

#### API 设计
- 简洁的解析器接口
- 灵活的验证器注册
- 可扩展的处理器机制
- 统一的异常体系

### 已知问题
- 暂未实现代码生成器
- 工作流执行逻辑待实现
- 需要更多的内置验证规则

### 下一版本计划
- 实现代码生成器
- 添加更多示例和文档
- 改进错误消息的本地化
- 性能优化