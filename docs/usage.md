# Agentara 使用指南

## 基本用法

### 1. 安装

```bash
pip install agentara
```

### 2. 编写 DSL 文件

创建一个 `.dsl` 文件，例如 `agents.dsl`：

```dsl
// 定义一个客服 Agent
agent CustomerSupport {
    name: "Customer Support Bot"
    description: "Handles customer inquiries"
    system_prompt: "You are a helpful customer support agent. Be polite and professional."
    model_provider: "openai"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
}

// 定义一个代码助手 Agent
agent CodeHelper {
    name: "Code Assistant"
    system_prompt: "You are an expert programmer. Help users write clean code."
    model_provider: "anthropic"
    model_name: "claude-3-opus"
    temperature: 0.5
}
```

### 3. 解析 DSL

```python
from agentara import AgentParser

# 创建解析器
parser = AgentParser()

# 从文件读取并解析
with open("agents.dsl", "r") as f:
    content = f.read()
    result = parser.parse(content)

# 使用解析结果
for agent in result["agents"]:
    print(f"Agent: {agent['id']}")
    props = agent['properties']
    
    # 获取配置信息
    model_provider = props.get('model_provider')
    model_name = props.get('model_name')
    system_prompt = props.get('system_prompt')
    
    # 可以用这些信息初始化实际的 AI Agent
    print(f"  Model: {model_provider}/{model_name}")
    print(f"  System Prompt: {system_prompt}")
```

### 4. 错误处理

```python
from agentara import AgentParser

parser = AgentParser()

try:
    # 解析可能出错的 DSL
    result = parser.parse(invalid_dsl)
except Exception as e:
    print(f"解析错误: {e}")
    # 错误信息会包含行号和列号
```

## 高级用法

### 自定义语法文件

如果需要修改语法，可以提供自定义的语法文件：

```python
from pathlib import Path
from agentara import AgentParser

# 使用自定义语法文件
custom_grammar = Path("my_grammar.lark")
parser = AgentParser(grammar_file=custom_grammar)
```

### 批量处理

```python
from pathlib import Path
from agentara import AgentParser

parser = AgentParser()
agents_dir = Path("agents")

# 解析目录下所有 .dsl 文件
all_agents = []
for dsl_file in agents_dir.glob("*.dsl"):
    with open(dsl_file, "r") as f:
        result = parser.parse(f.read())
        all_agents.extend(result["agents"])

print(f"总共解析了 {len(all_agents)} 个 Agent")
```

## 完整示例

```python
from agentara import AgentParser

# DSL 内容
dsl_content = """
agent Assistant {
    name: "AI Assistant"
    description: "General purpose assistant"
    system_prompt: "You are a helpful AI assistant."
    model_provider: "openai"
    model_name: "gpt-4"
    temperature: 0.7
    max_tokens: 2000
}
"""

# 解析
parser = AgentParser()
result = parser.parse(dsl_content)

# 获取 Agent 信息
agent = result["agents"][0]
print(f"Agent ID: {agent['id']}")
print(f"Properties:")
for key, value in agent['properties'].items():
    print(f"  {key}: {value}")
```