# textX 模型序列化与 JSON 转换调研报告

## 调研背景

在 Agentara 项目中，我们使用 textX 框架构建了一个 Agent DSL。为了支持前端 UI 的可视化编辑需求，我们需要实现：

1. **DSL → JSON**：将 DSL 文本解析成结构化的 JSON 数据供前端渲染
2. **JSON → DSL**：将前端编辑的 JSON 数据转换回 DSL 文本格式

## textX 框架现状分析

### 1. textX 核心功能

textX 是一个用于构建领域特定语言（DSL）的 Python 框架，它提供了：

- 基于语法文件（.tx）的元模型定义
- 自动生成的解析器
- 模型实例化和验证
- 可视化导出（DOT、PlantUML）

### 2. 序列化支持现状

根据官方文档和源码分析，textX **目前不支持**：

1. 将模型对象序列化回原始 DSL 文本
2. 内置的 JSON 序列化功能

textX 主要关注从文本到模型的单向转换。虽然有 `model_export` 功能，但仅支持导出为可视化格式（DOT、PlantUML），而非数据交换格式。

### 3. 模型结构特点

textX 生成的模型是 Python 对象图，包含：

- 动态生成的 Python 类（基于语法规则）
- 特殊属性（以 `_tx` 前缀开头）
- 完整的父子关系和引用解析

## 解决方案研究

### 方案 1：使用 Python Pickle

**优点**：
- 可以完整保存模型状态
- 实现简单
- 保留所有 textX 特殊属性

**缺点**：
- 二进制格式，不可读
- Python 专用，无法与前端交互
- 安全性问题

**示例代码**：
```python
import pickle

# 序列化
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# 反序列化
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)
```

### 方案 2：使用 jsonpickle

**优点**：
- 生成 JSON 格式
- 可以处理复杂 Python 对象
- 支持循环引用

**缺点**：
- 生成的 JSON 包含 Python 特定信息
- 结构复杂，不适合前端直接使用
- 仍然是 Python 特定的解决方案

**示例代码**：
```python
import jsonpickle

# 序列化
json_str = jsonpickle.encode(model)

# 反序列化
model = jsonpickle.decode(json_str)
```

### 方案 3：自定义序列化器（推荐）

**优点**：
- 完全控制 JSON 结构
- 可以生成前端友好的格式
- 跨语言兼容
- 可以过滤不需要的属性

**缺点**：
- 需要自行实现
- 需要处理引用关系

**实现思路**：

#### 3.1 DSL → JSON 序列化器

```python
def model_to_dict(obj, visited=None):
    """递归转换 textX 模型对象为字典"""
    if visited is None:
        visited = set()
    
    # 避免循环引用
    if id(obj) in visited:
        return {"_ref": id(obj)}
    visited.add(id(obj))
    
    # 基础类型直接返回
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    
    # 列表递归处理
    if isinstance(obj, list):
        return [model_to_dict(item, visited) for item in obj]
    
    # textX 对象处理
    result = {
        "_type": obj.__class__.__name__
    }
    
    # 遍历所有属性
    for attr_name in dir(obj):
        # 跳过私有属性和 textX 特殊属性
        if attr_name.startswith('_'):
            continue
            
        try:
            value = getattr(obj, attr_name)
            # 跳过方法
            if callable(value):
                continue
                
            result[attr_name] = model_to_dict(value, visited)
        except:
            pass
    
    return result
```

#### 3.2 JSON → DSL 生成器

```python
class DSLGenerator:
    """从 JSON 生成 DSL 文本"""
    
    def generate(self, json_data):
        if isinstance(json_data, dict):
            obj_type = json_data.get('_type')
            
            # 根据类型分发到不同的生成方法
            if obj_type == 'Agent':
                return self._generate_agent(json_data)
            elif obj_type == 'Workflow':
                return self._generate_workflow(json_data)
            # ... 其他类型
            
        return ""
    
    def _generate_agent(self, data):
        lines = [f"agent {data['name']} {{"]
        
        # 属性
        for key in ['name', 'description', 'version', 'author']:
            if key in data and data[key]:
                lines.append(f'    {key}: "{data[key]}"')
        
        # 能力
        if 'capabilities' in data:
            lines.append("    capabilities [")
            for cap in data['capabilities']:
                lines.append(f"        {self._generate_capability(cap)},")
            lines.append("    ]")
        
        # 参数
        if 'parameters' in data:
            lines.append("    parameters {")
            for param in data['parameters']:
                lines.append(f"        {param['name']}: {param['value']}")
            lines.append("    }")
        
        lines.append("}")
        return "\n".join(lines)
```

### 方案 4：基于模板的方案

使用 Jinja2 模板生成 DSL：

```python
from jinja2 import Template

agent_template = Template('''
agent {{ agent.name }} {
    name: "{{ agent.properties.name }}"
    {% if agent.properties.description %}
    description: "{{ agent.properties.description }}"
    {% endif %}
    
    {% if agent.capabilities %}
    capabilities [
        {% for cap in agent.capabilities %}
        {{ cap.name }}{% if cap.parameters %}({{ cap.parameters|join(', ') }}){% endif %}{% if not loop.last %},{% endif %}
        {% endfor %}
    ]
    {% endif %}
}
''')
```

## 前端集成方案

### 1. JSON Schema 设计

为前端定义清晰的 JSON Schema：

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "definitions": {
    "Agent": {
      "type": "object",
      "properties": {
        "_type": { "const": "Agent" },
        "name": { "type": "string" },
        "properties": {
          "type": "object",
          "properties": {
            "name": { "type": "string" },
            "description": { "type": "string" },
            "version": { "type": "string" },
            "author": { "type": "string" }
          }
        },
        "capabilities": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Capability"
          }
        },
        "parameters": {
          "type": "array",
          "items": {
            "$ref": "#/definitions/Parameter"
          }
        }
      }
    }
  }
}
```

### 2. API 设计

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/dsl/parse', methods=['POST'])
def parse_dsl():
    """DSL → JSON"""
    dsl_content = request.json['content']
    
    try:
        # 解析 DSL
        model = parser.parse(dsl_content)
        
        # 转换为 JSON
        json_data = model_to_dict(model)
        
        return jsonify({
            'success': True,
            'data': json_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/dsl/generate', methods=['POST'])
def generate_dsl():
    """JSON → DSL"""
    json_data = request.json['data']
    
    try:
        # 生成 DSL
        generator = DSLGenerator()
        dsl_content = generator.generate(json_data)
        
        # 验证生成的 DSL
        model = parser.parse(dsl_content)
        
        return jsonify({
            'success': True,
            'content': dsl_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
```

## 实施建议

### 1. 短期方案（MVP）

1. 实现基础的 `model_to_dict` 函数
2. 针对核心 DSL 结构（Agent、Workflow）实现 JSON → DSL 生成
3. 提供简单的 REST API

### 2. 中期优化

1. 完善错误处理和验证
2. 支持更复杂的 DSL 特性（引用、导入等）
3. 添加增量更新支持
4. 实现双向同步机制

### 3. 长期规划

1. 考虑贡献回 textX 社区
2. 开发独立的 textX 序列化库
3. 支持多种序列化格式（YAML、TOML 等）
4. 实现模型差异比较和合并

## 技术风险与缓解

### 风险 1：模型复杂度

**问题**：随着 DSL 功能增加，序列化逻辑会变得复杂

**缓解**：
- 采用访问者模式设计
- 为每种类型定义独立的序列化器
- 编写充分的单元测试

### 风险 2：性能问题

**问题**：大型模型的序列化可能较慢

**缓解**：
- 实现缓存机制
- 支持部分序列化
- 考虑使用 C 扩展优化关键路径

### 风险 3：版本兼容性

**问题**：DSL 语法变化可能破坏现有序列化

**缓解**：
- 在 JSON 中包含版本信息
- 实现版本迁移机制
- 保持向后兼容

## 结论

虽然 textX 本身不提供序列化功能，但通过自定义实现，我们可以满足前端 UI 集成的需求。推荐采用**方案 3（自定义序列化器）**，因为它提供了最大的灵活性和控制力。

关键实施步骤：

1. 定义清晰的 JSON Schema
2. 实现双向转换器
3. 提供 REST API
4. 编写完整的测试用例
5. 准备详细的前端集成文档

这个方案不仅能满足当前需求，还为未来的扩展预留了空间。