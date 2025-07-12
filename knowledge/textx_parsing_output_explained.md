# textX 解析产物详解

## 概述

textX 解析 DSL 文本后，生成的是一个 **Python 对象图**，其中每个对象都是动态生成的 Python 类的实例。

## 1. 解析产物的本质

### 1.1 动态生成的 Python 类

当你定义语法规则时，textX 会自动生成对应的 Python 类：

```textx
// textX 语法
Agent:
    'agent' name=ID '{'
        version=STRING
        capabilities+=Capability
    '}'
;

Capability:
    name=ID ('(' params+=Param[','] ')')?
;
```

textX 会生成类似这样的 Python 类（概念性展示）：

```python
# textX 内部动态生成的类（简化示意）
class Agent:
    def __init__(self, parent, name, version, capabilities):
        self.parent = parent
        self.name = name
        self.version = version
        self.capabilities = capabilities
        
        # textX 特殊属性
        self._tx_position = ...       # 在源文件中的位置
        self._tx_position_end = ...   # 结束位置
        self._tx_fqn = 'Agent'       # 完全限定名

class Capability:
    def __init__(self, parent, name, params):
        self.parent = parent
        self.name = name
        self.params = params if params else []
        
        # textX 特殊属性
        self._tx_position = ...
        self._tx_position_end = ...
        self._tx_fqn = 'Capability'
```

### 1.2 实际的解析产物

```python
from textx import metamodel_from_str

# 定义语法
grammar = '''
Agent:
    'agent' name=ID '{'
        'version:' version=STRING
        capabilities=Capabilities?
    '}'
;

Capabilities:
    'capabilities' '[' items+=Capability[','] ']'
;

Capability:
    name=ID
;
'''

# 创建元模型
mm = metamodel_from_str(grammar)

# 解析 DSL
dsl_text = '''
agent DataCollector {
    version: "1.0.0"
    capabilities [
        fetch_data,
        validate_schema,
        transform_data
    ]
}
'''

# 解析生成模型
model = mm.model_from_str(dsl_text)

# 探索生成的对象
print(type(model))                    # <class 'textx.lang.Agent'>
print(model.name)                     # 'DataCollector'
print(model.version)                  # '1.0.0'
print(type(model.capabilities))       # <class 'textx.lang.Capabilities'>
print(len(model.capabilities.items))  # 3

# 访问嵌套对象
for cap in model.capabilities.items:
    print(f"Capability: {cap.name}")
    print(f"  Type: {type(cap)}")     # <class 'textx.lang.Capability'>
    print(f"  Position: {cap._tx_position}")
```

## 2. textX 特殊属性

每个解析生成的对象都包含特殊属性（以 `_tx` 开头）：

```python
# 示例对象
agent = model  # 假设是解析出的 Agent 对象

# 1. 位置信息
print(agent._tx_position)      # 在源文件中的起始位置（字符偏移）
print(agent._tx_position_end)  # 结束位置

# 2. 元信息
print(agent._tx_fqn)          # 'Agent' - 规则的完全限定名
print(agent._tx_metamodel)     # 元模型引用（仅根对象有）
print(agent._tx_model)         # 模型根引用

# 3. 解析器信息
print(model._tx_parser)        # 解析器实例
print(model._tx_filename)      # 源文件名（如果从文件解析）

# 4. 获取行列位置
line, col = model._tx_parser.pos_to_linecol(agent._tx_position)
print(f"Agent defined at line {line}, column {col}")
```

## 3. 对象图的结构

### 3.1 树形结构

```python
# 可视化对象图结构
def print_model_tree(obj, indent=0):
    """递归打印模型树"""
    prefix = "  " * indent
    obj_type = obj.__class__.__name__
    
    # 打印当前对象
    print(f"{prefix}{obj_type}")
    
    # 遍历所有属性
    for attr_name in dir(obj):
        if attr_name.startswith('_'):
            continue
            
        attr_value = getattr(obj, attr_name)
        
        # 跳过方法
        if callable(attr_value):
            continue
            
        # 处理列表
        if isinstance(attr_value, list):
            print(f"{prefix}  {attr_name}: [")
            for item in attr_value:
                if hasattr(item, '_tx_fqn'):
                    print_model_tree(item, indent + 2)
                else:
                    print(f"{prefix}    {item}")
            print(f"{prefix}  ]")
        
        # 处理对象
        elif hasattr(attr_value, '_tx_fqn'):
            print(f"{prefix}  {attr_name}:")
            print_model_tree(attr_value, indent + 2)
        
        # 处理简单值
        else:
            print(f"{prefix}  {attr_name}: {attr_value}")

# 使用
print_model_tree(model)
```

输出示例：
```
Agent
  name: DataCollector
  version: 1.0.0
  capabilities:
    Capabilities
      items: [
        Capability
          name: fetch_data
        Capability
          name: validate_schema
        Capability
          name: transform_data
      ]
```

### 3.2 引用解析

textX 自动解析引用关系：

```textx
Workflow:
    'workflow' name=ID '{'
        'agents:' agents+=[Agent][',']
        flows+=Flow
    '}'
;

Flow:
    from=[Agent] '->' to=[Agent]
;
```

```python
# DSL
workflow_dsl = '''
agent Collector {
    version: "1.0"
}

agent Processor {
    version: "1.0"
}

workflow Pipeline {
    agents: Collector, Processor
    Collector -> Processor
}
'''

# 解析后，引用自动解析为对象
model = mm.model_from_str(workflow_dsl)
workflow = model.workflows[0]
flow = workflow.flows[0]

# from 和 to 不是字符串，而是实际的 Agent 对象！
print(flow.from.name)      # 'Collector'
print(flow.to.name)        # 'Processor'
print(flow.from is model.agents[0])  # True - 同一个对象
```

## 4. 自定义类

你可以提供自己的 Python 类来代替动态生成的类：

```python
class Agent:
    """自定义 Agent 类"""
    def __init__(self, parent, name, version, capabilities):
        self.parent = parent
        self.name = name
        self.version = version
        self.capabilities = capabilities or []
        
    def get_capability_names(self):
        """自定义方法"""
        if self.capabilities:
            return [cap.name for cap in self.capabilities.items]
        return []
    
    def __str__(self):
        return f"Agent({self.name} v{self.version})"

# 注册自定义类
mm = metamodel_from_str(grammar, classes=[Agent])

# 解析后得到自定义类的实例
model = mm.model_from_str(dsl_text)
print(type(model))                          # <class '__main__.Agent'>
print(model.get_capability_names())         # ['fetch_data', 'validate_schema', ...]
print(str(model))                           # Agent(DataCollector v1.0.0)
```

## 5. 模型处理和转换

### 5.1 遍历模型

```python
from textx import get_children_of_type, get_model

# 获取所有特定类型的对象
all_capabilities = get_children_of_type("Capability", model)
for cap in all_capabilities:
    print(f"Found capability: {cap.name}")

# 获取模型根
root = get_model(some_nested_object)
```

### 5.2 模型验证

```python
def validate_agent(agent):
    """自定义验证"""
    if agent.version == "0.0.0":
        raise TextXSemanticError("Version cannot be 0.0.0", model=agent)
    
    if not agent.capabilities:
        raise TextXSemanticError("Agent must have at least one capability", model=agent)

# 注册验证器
mm.register_obj_processors({
    'Agent': validate_agent
})
```

### 5.3 模型转换

```python
def agent_to_dict(agent):
    """将 textX 模型转换为字典"""
    return {
        'name': agent.name,
        'version': agent.version,
        'capabilities': [
            cap.name for cap in agent.capabilities.items
        ] if agent.capabilities else [],
        'position': {
            'start': agent._tx_position,
            'end': agent._tx_position_end
        }
    }

# 转换
agent_dict = agent_to_dict(model)
print(json.dumps(agent_dict, indent=2))
```

## 6. 内存中的表示

```python
# 查看对象的所有属性
def inspect_object(obj):
    print(f"Object: {obj.__class__.__name__}")
    print("Attributes:")
    for attr in sorted(dir(obj)):
        if not attr.startswith('__'):
            value = getattr(obj, attr)
            if not callable(value):
                value_repr = repr(value)[:50] + '...' if len(repr(value)) > 50 else repr(value)
                print(f"  {attr}: {value_repr}")

inspect_object(model)
```

输出：
```
Object: Agent
Attributes:
  _tx_filename: None
  _tx_fqn: Agent
  _tx_metamodel: <textx.metamodel.Metamodel object at 0x...>
  _tx_model: <textx.lang.Agent object at 0x...>
  _tx_position: 0
  _tx_position_end: 140
  capabilities: <textx.lang.Capabilities object at 0x...>
  name: DataCollector
  parent: None
  version: 1.0.0
```

## 7. 实际应用示例

### 7.1 代码生成

```python
def generate_python_code(agent):
    """从模型生成 Python 代码"""
    code = f'''
class {agent.name}:
    VERSION = "{agent.version}"
    
    def __init__(self):
        self.capabilities = {[cap.name for cap in agent.capabilities.items]}
    
    def execute(self):
        for capability in self.capabilities:
            print(f"Executing {{capability}}")
'''
    return code

# 生成代码
python_code = generate_python_code(model)
print(python_code)
```

### 7.2 序列化为其他格式

```python
def to_yaml(agent):
    """转换为 YAML"""
    import yaml
    data = {
        'agent': {
            'name': agent.name,
            'version': agent.version,
            'capabilities': [cap.name for cap in agent.capabilities.items]
        }
    }
    return yaml.dump(data)

def to_json(agent):
    """转换为 JSON"""
    # 使用前面定义的 agent_to_dict
    return json.dumps(agent_to_dict(agent), indent=2)
```

## 总结

textX 解析的产物是：

1. **Python 对象图**：由相互连接的 Python 对象组成
2. **动态类实例**：每个语法规则对应一个动态生成的类
3. **保留源信息**：通过 `_tx_*` 属性保留位置等元信息
4. **自动解析引用**：引用自动转换为实际对象
5. **可自定义**：可以使用自定义类替代动态类
6. **易于处理**：标准 Python 对象，易于遍历和转换

这种设计让 textX 模型非常容易处理 - 你可以像操作普通 Python 对象一样操作它们！