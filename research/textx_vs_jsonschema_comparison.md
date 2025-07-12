# textX vs JSON Schema：以 Agent DSL 为例的对比分析

## 引言

在 Agentara 项目中，我们选择了 textX 而不是 JSON Schema。本文将详细对比两者的能力差异，说明为什么 textX 更适合定义复杂的 Agent DSL。

## 核心差异：声明式 vs 命令式

### JSON Schema：数据验证
```json
{
  "type": "object",
  "properties": {
    "agent": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "capabilities": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    }
  }
}
```

### textX：语言定义
```textx
Agent:
    'agent' name=ID '{'
        capabilities=Capabilities
    '}'
;

Capabilities:
    'capabilities' '[' items+=Capability[','] ']'
;
```

## textX 独有能力详解

### 1. 自定义语法结构

**textX 可以定义任意语法**：

```textx
// 自然的 DSL 语法
agent DataCollector {
    name: "数据收集器"
    version: 1.0.0
    
    capabilities [
        fetch_data(source: "api", format: "json"),
        validate_schema,
        transform_data
    ]
    
    on_error: retry(3) then notify(admin)
}
```

**JSON Schema 只能验证 JSON 结构**：
```json
{
  "agent": {
    "name": "DataCollector",
    "properties": {
      "name": "数据收集器",
      "version": "1.0.0"
    },
    "capabilities": [
      {
        "name": "fetch_data",
        "parameters": {
          "source": "api",
          "format": "json"
        }
      }
    ]
  }
}
```

### 2. 语法糖和简写

**textX 支持多种表达方式**：

```textx
// 定义能力的多种语法
Capability:
    // 简单能力
    name=ID |
    // 带参数的能力
    name=ID '(' params+=Parameter[','] ')' |
    // 带配置块的能力
    name=ID '{' config+=Config '}'
;

// 使用时可以混合使用
capabilities [
    simple_task,                          // 简单形式
    complex_task(timeout: 30),            // 函数形式
    advanced_task {                       // 块形式
        parallel: true
        workers: 5
    }
]
```

**JSON Schema 必须统一结构**：
```json
{
  "capabilities": [
    { "name": "simple_task" },
    { "name": "complex_task", "parameters": { "timeout": 30 } },
    { 
      "name": "advanced_task", 
      "config": { "parallel": true, "workers": 5 } 
    }
  ]
}
```

### 3. 引用和关系

**textX 原生支持引用**：

```textx
Workflow:
    'workflow' name=ID '{'
        'agents:' '[' agents+=[Agent][','] ']'
        'flow' '{' flows+=Flow '}'
    '}'
;

Flow:
    from=[Agent] '->' to=[Agent] 
    ('when' condition=Expression)?
;

// 使用
workflow DataPipeline {
    agents: [DataCollector, DataProcessor, DataAnalyzer]
    
    flow {
        DataCollector -> DataProcessor when "data.size > 1000"
        DataProcessor -> DataAnalyzer
    }
}
```

**JSON Schema 需要额外验证**：
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "workflow": {
      "type": "object",
      "properties": {
        "agents": {
          "type": "array",
          "items": { "type": "string" }
        },
        "flow": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "from": { "type": "string" },
              "to": { "type": "string" },
              "condition": { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

无法验证：
- `from` 和 `to` 必须是已定义的 agent
- 引用的完整性
- 循环依赖

### 4. 上下文相关语法

**textX 可以根据上下文改变解析规则**：

```textx
Agent:
    'agent' name=ID '{'
        // 根据 agent 类型使用不同的配置
        (type='collector' collector_config=CollectorConfig |
         type='processor' processor_config=ProcessorConfig |
         type='analyzer' analyzer_config=AnalyzerConfig)
    '}'
;

// 不同类型有不同的必需字段
CollectorConfig:
    'source:' source=STRING
    'interval:' interval=INT
;

ProcessorConfig:
    'input_format:' input=Format
    'output_format:' output=Format
;
```

**JSON Schema 使用 oneOf/anyOf（复杂且难读）**：
```json
{
  "oneOf": [
    {
      "properties": {
        "type": { "const": "collector" },
        "collector_config": {
          "required": ["source", "interval"]
        }
      }
    },
    {
      "properties": {
        "type": { "const": "processor" },
        "processor_config": {
          "required": ["input_format", "output_format"]
        }
      }
    }
  ]
}
```

### 5. 语义动作和验证

**textX 支持解析时执行代码**：

```python
# 自定义对象处理器
def capability_processor(capability):
    # 验证能力参数
    if capability.name == "fetch_data":
        if not hasattr(capability, 'source'):
            raise TextXSemanticError("fetch_data requires 'source' parameter")
    
    # 动态添加属性
    if capability.name == "rate_limit":
        capability.requests_per_second = parse_rate_limit(capability.value)
    
    return capability

# 注册处理器
metamodel.register_obj_processors({
    'Capability': capability_processor
})
```

**JSON Schema 只能做静态验证**。

### 6. 宏和模板

**textX 可以实现语言级别的抽象**：

```textx
// 定义宏
Macro:
    'macro' name=ID '(' params*=ID[','] ')' '=' expansion=Expansion
;

// 使用宏
agent MyAgent {
    @use_standard_error_handling(retry: 3, timeout: 30)
    @enable_monitoring(metrics: ["latency", "throughput"])
    
    capabilities [
        @crud_operations(entity: "User")  // 展开为 create, read, update, delete
    ]
}
```

**JSON Schema 无法实现这种抽象**。

### 7. 条件语法

**textX 可以实现条件解析**：

```textx
Agent:
    'agent' name=ID 
    ('extends' parent=[Agent])? '{'
        // 如果有 parent，某些字段变为可选
        (parent? | 'version:' version=STRING)
        properties*=Property
    '}'
;
```

### 8. 自定义操作符

**textX 允许定义领域特定的操作符**：

```textx
Rule:
    condition=Condition '=>' action=Action
;

Condition:
    left=Expression op=('>' | '<' | '==' | 'matches') right=Expression
;

// 使用
rules {
    cpu_usage > 80% => scale_up(instances: 2)
    error_rate > 5% => notify(team: "devops")
    log_message matches /ERROR:.*timeout/ => restart_service
}
```

### 9. 嵌入式语言

**textX 可以嵌入其他语言**：

```textx
Agent:
    'agent' name=ID '{'
        'script' language=('python' | 'javascript') ':'
        code=MULTILINE_CODE
    '}'
;

// 使用
agent DataTransformer {
    script python:
        ```
        def transform(data):
            return {
                'timestamp': datetime.now(),
                'processed': data.upper()
            }
        ```
}
```

### 10. 增量解析

**textX 可以实现部分解析和懒加载**：

```python
# 只解析需要的部分
class LazyAgentParser:
    def parse_header(self, text):
        # 只解析 agent 名称和类型，跳过内容
        partial_grammar = """
        Agent: 'agent' name=ID type=ID 'skip_body'
        """
        
    def parse_full(self, agent_name):
        # 需要时才解析完整内容
        pass
```

## 实际案例对比

### 案例：定义复杂的工作流规则

**textX 版本（直观易读）**：
```
workflow DataProcessing {
    parallel {
        branch validation {
            ValidateSchema -> CleanData when "errors == 0"
            ValidateSchema -> RejectData when "errors > 0"
        }
        
        branch enrichment {
            FetchMetadata -> MergeData
        }
    }
    
    synchronize at MergeData
    
    MergeData -> SaveToDatabase
        with retry(3)
        on_error: notify(admin) then abort
}
```

**JSON Schema 版本（冗长且难以表达）**：
```json
{
  "workflow": {
    "name": "DataProcessing",
    "structures": [
      {
        "type": "parallel",
        "branches": [
          {
            "name": "validation",
            "steps": [
              {
                "from": "ValidateSchema",
                "to": "CleanData",
                "condition": "errors == 0"
              },
              {
                "from": "ValidateSchema",
                "to": "RejectData",
                "condition": "errors > 0"
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## 性能考虑

### textX
- 解析时间：需要构建 AST
- 运行时：可以生成优化的代码
- 内存：AST 占用额外内存

### JSON Schema
- 解析时间：JSON 解析很快
- 运行时：验证可能很慢（复杂 schema）
- 内存：相对较少

## 选择建议

### 使用 textX 当你需要：
1. 设计领域特定语言（DSL）
2. 自然的语法表达
3. 复杂的引用关系
4. 编译时优化
5. 语言级别的抽象

### 使用 JSON Schema 当你需要：
1. 验证 JSON 数据
2. 跨语言的数据交换
3. 简单的配置验证
4. RESTful API 定义
5. 现有工具链集成

## 结论

对于 Agentara 项目，textX 的选择是正确的，因为：

1. **表达力**：Agent DSL 需要自然、直观的语法
2. **复杂性**：工作流、引用、条件逻辑等难以用 JSON Schema 表达
3. **扩展性**：未来可能需要添加更多语言特性
4. **用户体验**：开发者写 DSL 比写 JSON 更舒适
5. **工具支持**：可以构建更好的 IDE 支持、语法高亮等

textX 让我们能够创建一个真正的**语言**，而不仅仅是一个数据格式。这对于 Agent 定义这样的复杂领域来说是至关重要的。