# Agentara Agent DSL 语法规范（AI 专用提示词）

您需要生成符合 Agentara DSL 语法规范的 Agent 定义。请严格遵循以下语法规则。

## 基本语法结构

### 1. Agent 定义

```
agent <AgentName> {
    <properties>
    <capabilities>
    <parameters>
    <rules>
}
```

**重要规则**：
- Agent 名称必须以大写字母开头，使用驼峰命名法
- Agent 名称只能包含字母和数字，不能有空格或特殊字符
- 每个 agent 块必须用花括号 `{}` 包围
- 属性、能力、参数和规则部分都是可选的

### 2. 属性定义（Properties）

基本属性使用 `key: "value"` 格式：

```
name: "显示名称"
description: "Agent 的描述"
version: "1.0.0"
author: "作者名"
tags: "tag1, tag2, tag3"
```

**规则**：
- 字符串值必须用双引号包围
- 版本号建议使用语义化版本格式（主版本.次版本.修订版本）

### 3. 能力定义（Capabilities）

```
capabilities [
    capability_name,
    capability_with_params(param1("value1"), param2("value2")),
    another_capability
]
```

**规则**：
- 能力列表用方括号 `[]` 包围
- 能力之间用逗号分隔
- 能力名称使用小写字母和下划线
- 带参数的能力使用圆括号，参数格式为 `paramName("value")`

### 4. 参数定义（Parameters）

```
parameters {
    param_name: value
    string_param: "string value"
    number_param: 123
    float_param: 0.7
    required_param: required
}
```

**规则**：
- 参数块用花括号 `{}` 包围
- 每个参数占一行
- 字符串值需要双引号
- 数字直接写
- 必需参数使用 `required` 关键字

### 5. 规则定义（Rules）

```
rules {
    on_error: retry(3)
    rate_limit: 100/hour
    timeout: 60
    priority: "high"
}
```

**规则**：
- 规则块用花括号 `{}` 包围
- 函数调用格式：`functionName(argument)`
- 速率限制格式：`number/period`，period 可以是 second、minute、hour、day
- 字符串值需要双引号

## 完整示例

### 简单 Agent

```
agent SimpleBot {
    name: "Simple Bot"
    description: "A basic bot"
    version: "1.0.0"
}
```

### 中等复杂度 Agent

```
agent DataProcessor {
    name: "Data Processing Agent"
    description: "Processes various data formats"
    version: "2.0.0"
    
    capabilities [
        read_csv,
        read_json,
        transform_data,
        write_output
    ]
    
    parameters {
        input_format: "csv"
        output_format: "json"
        batch_size: 1000
    }
}
```

### 完整功能 Agent

```
agent AdvancedAIAssistant {
    name: "Advanced AI Assistant"
    description: "Full-featured AI assistant with multiple capabilities"
    version: "3.0.0"
    author: "AI Team"
    tags: "ai, nlp, automation"
    
    capabilities [
        natural_language_processing,
        code_generation(language("python"), style("pep8")),
        data_analysis(framework("pandas")),
        web_search,
        summarization(max_length(500))
    ]
    
    parameters {
        model: "gpt-4"
        temperature: 0.7
        max_tokens: 2000
        api_key: required
        retry_attempts: 3
        timeout: 30
    }
    
    rules {
        on_error: retry(3)
        rate_limit: 100/hour
        timeout: 60
        max_concurrent: 5
        priority: "high"
    }
}
```

## Workflow 定义（多 Agent 协作）

```
workflow WorkflowName {
    agents: [Agent1, Agent2, Agent3]
    
    flow {
        Agent1 -> Agent2
        Agent2 -> Agent3
    }
}
```

**规则**：
- workflow 名称规则同 agent 名称
- agents 列表引用已定义的 agent 名称
- flow 中使用 `->` 表示数据流向

## 常见错误示例

### ❌ 错误示例 1：缺少引号
```
agent Wrong {
    name: Unquoted Name  // 错误：字符串必须有引号
}
```

### ❌ 错误示例 2：错误的能力列表语法
```
agent Wrong {
    capabilities [
        cap1
        cap2  // 错误：缺少逗号
    ]
}
```

### ❌ 错误示例 3：agent 名称不规范
```
agent wrong_name {  // 错误：必须以大写字母开头
}

agent Wrong-Name {  // 错误：不能包含连字符
}
```

### ❌ 错误示例 4：缺少花括号
```
agent Incomplete
    name: "Test"  // 错误：缺少花括号
```

## 生成检查清单

在生成 Agent DSL 时，请确保：

1. ✅ Agent 名称以大写字母开头，使用驼峰命名
2. ✅ 所有字符串值都用双引号包围
3. ✅ 每个块都有正确的开闭括号/花括号
4. ✅ 列表项之间有逗号分隔
5. ✅ 参数名称使用小写字母和下划线
6. ✅ 版本号符合语义化版本格式
7. ✅ 速率限制使用正确的格式（数字/时间单位）
8. ✅ 必需参数使用 `required` 关键字标记

## 注释

DSL 支持单行注释：
```
// 这是一个注释
agent MyAgent {
    // 另一个注释
    name: "My Agent"
}
```

请根据用户需求生成符合上述规范的 Agent DSL 代码。