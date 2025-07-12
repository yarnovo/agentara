# 前端渲染格式方案对比

## 方案 A：DOT + 图形库（强烈推荐）

### 优势
1. **textX 已支持**：无需额外开发序列化功能
2. **成熟的前端库**：
   - **Viz.js**：Graphviz 的 JavaScript 版本
   - **d3-graphviz**：基于 D3.js 的 Graphviz 渲染器
   - **@hpcc-js/wasm**：WebAssembly 版本的 Graphviz

### 实现示例

```python
# 后端：直接使用 textX 的导出功能
from textx.export import model_export
from io import StringIO

def model_to_dot(model):
    """将模型导出为 DOT 字符串"""
    output = StringIO()
    model_export(model, output)
    return output.getvalue()
```

```javascript
// 前端：使用 d3-graphviz 渲染
import { graphviz } from 'd3-graphviz';

function renderModel(dotString) {
    graphviz('#graph')
        .renderDot(dotString)
        .on('end', function () {
            // 添加交互功能
            addInteractivity();
        });
}

// 支持交互编辑
function addInteractivity() {
    d3.selectAll('.node')
        .on('click', function(d) {
            // 编辑节点
            editNode(d);
        })
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
}
```

## 方案 B：图形数据结构格式

### 1. **Cytoscape.js JSON**
专门为网络图设计的 JSON 格式：

```json
{
  "elements": {
    "nodes": [
      { "data": { "id": "a1", "name": "Agent 1", "type": "DataCollector" }},
      { "data": { "id": "a2", "name": "Agent 2", "type": "DataProcessor" }}
    ],
    "edges": [
      { "data": { "source": "a1", "target": "a2", "label": "data flow" }}
    ]
  },
  "style": [ /* 样式定义 */ ],
  "layout": { "name": "dagre" }
}
```

### 2. **vis.js/vis-network 格式**
```javascript
const nodes = [
    {id: 1, label: 'Agent 1', group: 'collector'},
    {id: 2, label: 'Agent 2', group: 'processor'}
];

const edges = [
    {from: 1, to: 2, arrows: 'to', label: 'data'}
];
```

### 3. **mxGraph/draw.io XML**
更复杂但功能强大，支持完整的图形编辑：

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="Agent 1" style="rounded=1;" vertex="1" parent="1">
      <mxGeometry x="120" y="120" width="120" height="60" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

## 方案 C：DSL 直接渲染（创新方案）

### Monaco Editor + 实时预览

```javascript
// 使用 Monaco Editor 直接编辑 DSL
const editor = monaco.editor.create(document.getElementById('editor'), {
    value: dslContent,
    language: 'agentara-dsl', // 自定义语言
    theme: 'vs-dark'
});

// 实时解析并预览
editor.onDidChangeModelContent(() => {
    const content = editor.getValue();
    // 发送到后端解析并获取可视化数据
    updatePreview(content);
});
```

## 方案 D：混合方案（最佳实践）

### 1. 多格式支持的 API

```python
@app.route('/api/model/export', methods=['POST'])
def export_model():
    format = request.json.get('format', 'json')
    
    if format == 'dot':
        return {'dot': model_to_dot(model)}
    elif format == 'cytoscape':
        return {'elements': model_to_cytoscape(model)}
    elif format == 'vis':
        return {'nodes': nodes, 'edges': edges}
```

### 2. 前端适配层

```javascript
class ModelRenderer {
    constructor(format) {
        this.format = format;
        this.renderers = {
            'dot': new DotRenderer(),
            'cytoscape': new CytoscapeRenderer(),
            'vis': new VisRenderer()
        };
    }
    
    render(data, container) {
        return this.renderers[this.format].render(data, container);
    }
}
```

## 推荐实施路径

### 第一阶段：DOT + d3-graphviz
- 利用 textX 现有功能
- 快速实现可视化
- 支持基础交互

### 第二阶段：Cytoscape.js
- 更丰富的交互功能
- 支持拖拽编辑
- 自定义节点样式

### 第三阶段：完整编辑器
- Monaco Editor + 图形预览
- 双向同步编辑
- 版本控制集成

## 技术栈建议

### 前端
- **图形库**：Cytoscape.js（功能最全）
- **编辑器**：Monaco Editor
- **框架**：React/Vue + 状态管理
- **样式**：Tailwind CSS

### 后端
- **序列化**：textX export + 自定义转换器
- **API**：FastAPI/Flask
- **WebSocket**：实时协作编辑

## 示例：Cytoscape.js 集成

```javascript
// React 组件示例
import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

export function AgentGraph({ modelData }) {
    const cyRef = useRef(null);
    
    useEffect(() => {
        const cy = cytoscape({
            container: cyRef.current,
            elements: modelData.elements,
            style: [
                {
                    selector: 'node[type="agent"]',
                    style: {
                        'background-color': '#666',
                        'label': 'data(name)',
                        'shape': 'roundrectangle'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'curve-style': 'bezier',
                        'target-arrow-shape': 'triangle',
                        'label': 'data(label)'
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB'
            }
        });
        
        // 添加编辑功能
        cy.on('tap', 'node', function(evt){
            const node = evt.target;
            openNodeEditor(node.data());
        });
        
        return () => cy.destroy();
    }, [modelData]);
    
    return <div ref={cyRef} style={{ width: '100%', height: '600px' }} />;
}
```

## 结论

对于前端渲染需求，**DOT + 图形库**是最快速的解决方案，因为：

1. textX 已经支持 DOT 导出
2. 前端有成熟的渲染库
3. DOT 格式简单但表达力强
4. 可以逐步迁移到更复杂的方案

建议先用 DOT 快速实现 MVP，然后根据用户反馈逐步增强到 Cytoscape.js 或自定义方案。