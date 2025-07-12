# DSL 到 UI 表单的转换方案

## 需求理解

将 DSL 语法转换成用户友好的 UI 表单界面，而不是图形化的节点关系展示。用户通过表单编辑，系统自动生成对应的 DSL 代码。

## 推荐方案：Schema-Driven UI

### 核心思路

1. **定义 UI Schema**：描述每个字段如何在 UI 中展示
2. **自动表单生成**：根据 Schema 生成表单
3. **双向绑定**：表单修改自动更新 DSL

### 方案 1：JSON Schema + UI Schema（推荐）

使用 JSON Schema 定义数据结构，UI Schema 定义展示方式。

#### 数据 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "title": "Agent 名称",
          "description": "Agent 的唯一标识符"
        },
        "properties": {
          "type": "object",
          "properties": {
            "name": {
              "type": "string",
              "title": "显示名称"
            },
            "description": {
              "type": "string",
              "title": "描述"
            },
            "version": {
              "type": "string",
              "title": "版本号",
              "pattern": "^\\d+\\.\\d+\\.\\d+$"
            },
            "author": {
              "type": "string",
              "title": "作者"
            }
          }
        },
        "capabilities": {
          "type": "array",
          "title": "能力列表",
          "items": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "enum": ["natural_language_processing", "code_generation", "data_analysis", "search_web"]
              },
              "parameters": {
                "type": "array",
                "items": {
                  "type": "object"
                }
              }
            }
          }
        },
        "parameters": {
          "type": "object",
          "title": "配置参数",
          "properties": {
            "model": {
              "type": "string",
              "title": "模型",
              "enum": ["gpt-4", "gpt-3.5-turbo", "claude"]
            },
            "temperature": {
              "type": "number",
              "title": "温度",
              "minimum": 0,
              "maximum": 2
            },
            "max_tokens": {
              "type": "integer",
              "title": "最大令牌数"
            }
          }
        }
      }
    }
  }
}
```

#### UI Schema
```json
{
  "agent": {
    "ui:order": ["name", "properties", "capabilities", "parameters"],
    "name": {
      "ui:autofocus": true,
      "ui:placeholder": "输入 Agent ID"
    },
    "properties": {
      "description": {
        "ui:widget": "textarea",
        "ui:options": {
          "rows": 3
        }
      },
      "version": {
        "ui:placeholder": "1.0.0"
      }
    },
    "capabilities": {
      "ui:widget": "checkboxes",
      "ui:options": {
        "inline": true
      }
    },
    "parameters": {
      "temperature": {
        "ui:widget": "range"
      },
      "model": {
        "ui:widget": "select"
      }
    }
  }
}
```

#### 前端实现（React + react-jsonschema-form）

```jsx
import Form from "@rjsf/core";
import validator from "@rjsf/validator-ajv8";

function AgentEditor({ initialData, onSave }) {
  const [formData, setFormData] = useState(initialData);
  
  const handleSubmit = ({ formData }) => {
    // 将表单数据转换为 DSL
    const dsl = generateDSL(formData);
    onSave(dsl);
  };
  
  return (
    <div className="agent-editor">
      <div className="form-panel">
        <Form
          schema={schema}
          uiSchema={uiSchema}
          formData={formData}
          onChange={({formData}) => setFormData(formData)}
          onSubmit={handleSubmit}
          validator={validator}
        />
      </div>
      <div className="preview-panel">
        <h3>DSL 预览</h3>
        <pre>{generateDSL(formData)}</pre>
      </div>
    </div>
  );
}
```

### 方案 2：Formily（阿里开源）

更强大的表单解决方案，支持复杂联动。

```jsx
import { createForm } from '@formily/core'
import { FormProvider, Field } from '@formily/react'
import { Input, Select, ArrayCards } from '@formily/antd'

const form = createForm()

const AgentForm = () => {
  return (
    <FormProvider form={form}>
      <Field
        name="name"
        title="Agent 名称"
        required
        component={Input}
      />
      <Field
        name="properties.description"
        title="描述"
        component={Input.TextArea}
      />
      <Field
        name="capabilities"
        title="能力配置"
        component={ArrayCards}
      >
        <Field name="name" component={Select} />
        <Field name="parameters" component={ParameterEditor} />
      </Field>
    </FormProvider>
  )
}
```

### 方案 3：自定义 Form Builder

基于 DSL 语法结构定制的表单构建器。

```typescript
interface FormField {
  type: 'text' | 'select' | 'array' | 'object' | 'code';
  label: string;
  name: string;
  options?: any;
  children?: FormField[];
}

const agentFormStructure: FormField[] = [
  {
    type: 'text',
    name: 'name',
    label: 'Agent ID',
    options: {
      placeholder: '输入唯一标识符',
      pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/
    }
  },
  {
    type: 'object',
    name: 'properties',
    label: '基本属性',
    children: [
      {
        type: 'text',
        name: 'name',
        label: '显示名称'
      },
      // ...
    ]
  },
  {
    type: 'array',
    name: 'capabilities',
    label: '能力列表',
    options: {
      addLabel: '添加能力',
      itemComponent: CapabilityEditor
    }
  }
];
```

## DSL 生成器实现

```typescript
class DSLGenerator {
  generateAgent(data: AgentData): string {
    const lines: string[] = [];
    
    // Agent 声明
    lines.push(`agent ${data.name} {`);
    
    // 属性
    if (data.properties) {
      for (const [key, value] of Object.entries(data.properties)) {
        if (value) {
          lines.push(`    ${key}: "${value}"`);
        }
      }
    }
    
    // 能力
    if (data.capabilities?.length > 0) {
      lines.push('    capabilities [');
      data.capabilities.forEach((cap, index) => {
        let line = `        ${cap.name}`;
        if (cap.parameters?.length > 0) {
          const params = cap.parameters.map(p => `${p.key}("${p.value}")`).join(', ');
          line += `(${params})`;
        }
        if (index < data.capabilities.length - 1) line += ',';
        lines.push(line);
      });
      lines.push('    ]');
    }
    
    // 参数
    if (data.parameters && Object.keys(data.parameters).length > 0) {
      lines.push('    parameters {');
      for (const [key, value] of Object.entries(data.parameters)) {
        lines.push(`        ${key}: ${this.formatValue(value)}`);
      }
      lines.push('    }');
    }
    
    lines.push('}');
    return lines.join('\n');
  }
  
  private formatValue(value: any): string {
    if (typeof value === 'string') return `"${value}"`;
    if (typeof value === 'boolean') return value ? 'true' : 'false';
    return String(value);
  }
}
```

## 高级特性

### 1. 实时预览
```jsx
function LivePreview({ formData }) {
  const [dsl, setDsl] = useState('');
  const [isValid, setIsValid] = useState(true);
  
  useEffect(() => {
    try {
      const generated = new DSLGenerator().generateAgent(formData);
      setDsl(generated);
      // 可选：发送到后端验证
      validateDSL(generated).then(setIsValid);
    } catch (error) {
      setIsValid(false);
    }
  }, [formData]);
  
  return (
    <div className={`preview ${isValid ? 'valid' : 'invalid'}`}>
      <SyntaxHighlighter language="agentara">
        {dsl}
      </SyntaxHighlighter>
    </div>
  );
}
```

### 2. 模板系统
```typescript
const templates = {
  dataCollector: {
    name: 'DataCollector',
    properties: {
      name: '数据采集器',
      description: '从多个数据源采集数据'
    },
    capabilities: ['fetch_api_data', 'scrape_web'],
    parameters: {
      timeout: 30,
      retry: 3
    }
  },
  aiAssistant: {
    // ...
  }
};
```

### 3. 字段联动
```jsx
// 根据选择的能力动态显示相关参数
const CapabilityForm = () => {
  const [selectedCapability, setSelectedCapability] = useState('');
  
  const parameterFields = {
    'code_generation': ['language', 'style', 'framework'],
    'data_analysis': ['format', 'visualization'],
    'search_web': ['max_results', 'sources']
  };
  
  return (
    <>
      <Select 
        value={selectedCapability}
        onChange={setSelectedCapability}
        options={capabilityOptions}
      />
      {parameterFields[selectedCapability]?.map(param => (
        <Field key={param} name={param} />
      ))}
    </>
  );
};
```

## 完整架构

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   UI Schema     │────▶│   Form Builder  │────▶│   Form UI       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   DSL Text      │◀────│  DSL Generator  │◀────│   Form Data     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                                                ▲
         │                                                │
         └──────────────── Parse & Validate ──────────────┘
```

## 工具推荐

### 表单库
- **react-jsonschema-form**：基于 JSON Schema，简单易用
- **Formily**：阿里出品，功能强大
- **react-hook-form**：轻量级，性能好
- **Formik**：社区活跃

### UI 组件库
- **Ant Design**：企业级，组件丰富
- **Material-UI**：Google 风格
- **Arco Design**：字节跳动
- **Semi Design**：抖音

### 代码编辑器
- **Monaco Editor**：VSCode 同款
- **CodeMirror**：轻量级
- **Ace Editor**：功能丰富

## 实施建议

1. **MVP 阶段**：使用 react-jsonschema-form 快速搭建
2. **优化阶段**：根据用户反馈定制组件
3. **高级阶段**：实现可视化拖拽构建器

这样用户就能通过友好的表单界面编辑 Agent，而不需要手写 DSL 语法了！