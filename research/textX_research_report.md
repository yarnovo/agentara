# textX 库调研报告

## 1. textX 简介

textX 是一个用于在 Python 中构建领域特定语言（DSL）的元语言框架。它受到 Xtext 的启发，能够从单一的语法描述自动生成解析器和元模型（Python 类形式）。

### 核心特性
- **自动化生成**：从语法定义自动生成解析器和 Python 类
- **无歧义语法**：基于 Arpeggio PEG 解析器，支持无限前瞻
- **灵活可扩展**：支持自定义类、处理器和验证规则
- **错误提示友好**：提供清晰的错误位置和期望信息

## 2. 解析和验证机制

### 2.1 工作流程

textX 的解析和验证是一体化的过程：

1. **语法定义** → 2. **创建元模型** → 3. **解析输入** → 4. **验证处理**

```python
from textx import metamodel_from_str

# 1. 定义语法
grammar = """
Model: commands*=DrawCommand;
DrawCommand: MoveCommand | ShapeCommand;
MoveTo: 'move' 'to' position=Point;
Point: x=INT ',' y=INT;
"""

# 2. 创建元模型
mm = metamodel_from_str(grammar)

# 3. 解析模型（解析失败会抛出异常）
model_str = "move to 5, 10"
model = mm.model_from_str(model_str)  # 解析和基础验证同时进行
```

### 2.2 验证机制

textX 提供两个层次的验证：

#### 基础验证（解析时自动执行）
- 语法结构验证
- 类型匹配验证
- 引用解析验证

#### 高级验证（通过处理器实现）
- **模型处理器**：在整个模型解析完成后执行
- **对象处理器**：在特定对象实例化时执行

```python
from textx import TextXSemanticError

# 模型处理器示例
def validate_model(model, metamodel):
    # 检查整个模型的语义规则
    if some_condition_not_met:
        raise TextXSemanticError("验证失败的描述")

# 对象处理器示例
def validate_point(point):
    # 检查单个对象的规则
    if point.x < 0 or point.y < 0:
        raise TextXSemanticError("坐标不能为负数", **point._tx_fqn)

# 注册处理器
mm.register_model_processor(validate_model)
mm.register_obj_processors({
    'Point': validate_point
})
```

## 3. 错误处理机制

### 3.1 解析错误

当输入不符合语法时，textX 会抛出 `NoMatch` 异常：

```python
from textx import NoMatch

try:
    model = mm.model_from_str("invalid syntax")
except NoMatch as e:
    print(f"解析错误位置：行 {e.line}, 列 {e.col}")
    print(f"期望的内容：{e.expected}")
```

### 3.2 语义错误

通过处理器抛出的 `TextXSemanticError` 会保留源文件位置信息：

```python
from textx import TextXSemanticError

def check_semantics(obj):
    if not valid:
        # 错误会包含对象在源文件中的位置
        raise TextXSemanticError("具体的错误描述", **obj._tx_fqn)
```

## 4. 实际应用示例

### 4.1 完整的 DSL 实现

```python
from textx import metamodel_from_str, TextXSemanticError

# 定义一个简单的配置 DSL
grammar = """
Config: sections*=Section;
Section: '[' name=ID ']' params*=Param;
Param: name=ID '=' value=Value;
Value: STRING | INT | BOOL;
"""

# 创建元模型
mm = metamodel_from_str(grammar)

# 添加验证规则
def validate_section(section):
    # 检查 section 名称唯一性
    model = section._tx_model
    sections = [s for s in model.sections if s.name == section.name]
    if len(sections) > 1:
        raise TextXSemanticError(
            f"Section '{section.name}' 重复定义",
            **section._tx_fqn
        )

mm.register_obj_processors({
    'Section': validate_section
})

# 使用 DSL
config_text = """
[database]
host = "localhost"
port = 3306

[cache]
enabled = true
size = 1024
"""

try:
    config = mm.model_from_str(config_text)
    print("配置解析成功")
except Exception as e:
    print(f"错误：{e}")
```

### 4.2 项目结构建议

对于 Agentara 项目，建议采用以下结构：

```
agentara/
├── agentara/
│   ├── __init__.py
│   ├── grammar/           # DSL 语法定义
│   │   ├── __init__.py
│   │   └── agent.tx       # Agent DSL 语法文件
│   ├── metamodel.py       # 元模型构建
│   ├── validators/        # 验证器
│   │   ├── __init__.py
│   │   └── agent_validator.py
│   ├── parser.py          # 解析器封装
│   └── cli.py            # 命令行接口
├── tests/
│   ├── models/           # 测试用例
│   │   ├── valid/
│   │   └── invalid/
│   └── test_parser.py
└── examples/             # 示例 Agent 定义
```

## 5. 关键发现和建议

### 5.1 解析即验证

- textX 的解析过程本身就包含了基础验证
- 解析成功意味着输入符合语法规则
- 额外的语义验证通过处理器机制实现

### 5.2 错误提示优势

- 自动追踪错误位置（行、列）
- 提供期望内容的详细信息
- 支持自定义错误消息

### 5.3 为 AI 友好的设计

- 清晰的语法定义格式
- 明确的错误提示
- 支持增量开发和测试

## 6. 实施建议

1. **语法设计**：保持 Agent DSL 语法简洁明了
2. **验证分层**：基础语法验证 + 业务逻辑验证
3. **错误处理**：提供详细的错误信息帮助 AI 修正
4. **测试驱动**：建立完善的测试用例库
5. **文档完善**：为 AI 提供清晰的 DSL 规范文档

## 7. 结论

textX 非常适合 Agentara 项目的需求：
- 解析和验证一体化，简化了实现
- 错误提示清晰，对 AI 友好
- 灵活的验证机制支持复杂的业务规则
- 成熟稳定，社区活跃

建议项目采用 textX 作为 Agent DSL 的实现基础。