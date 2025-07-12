# React (JSX) 语言解析技术详解

## 概述

React 本身是用 **JavaScript** 写的，但 JSX 语法需要特殊的解析和转换。让我们深入了解整个技术栈。

## 1. JSX 是什么？

JSX 是 JavaScript 的语法扩展，允许在 JS 代码中写类似 HTML 的标签：

```jsx
// JSX 代码
const element = <h1 className="greeting">Hello, {name}!</h1>;

// 转换后的 JavaScript
const element = React.createElement(
  'h1',
  {className: 'greeting'},
  'Hello, ',
  name,
  '!'
);
```

## 2. JSX 的解析和转换工具链

### 2.1 Babel - 主要的 JSX 转换器

Babel 是最常用的 JSX 转换工具，它的解析器使用了 **Acorn** 的修改版本。

**Babel 的架构**：
```
源代码 → Parser → AST → Transform → Generator → 输出代码
         (解析)   (抽象语法树) (转换)    (生成)
```

**Babel Parser（@babel/parser）的实现**：
- 基于 **Acorn**（JavaScript 解析器）
- 用 **JavaScript** 编写
- 支持 JSX 作为插件

```javascript
// Babel 解析 JSX 的简化示例
const parser = require('@babel/parser');

const code = `<div className="app">{message}</div>`;

const ast = parser.parse(code, {
  sourceType: 'module',
  plugins: ['jsx']  // 启用 JSX 插件
});
```

### 2.2 JSX 解析的核心实现

Babel 的 JSX 解析器扩展了 JavaScript 语法，主要添加了：

```javascript
// 在 @babel/parser 源码中的 JSX 解析逻辑（简化）
class JSXParser extends JavaScriptParser {
  // 解析 JSX 元素
  parseJSXElement() {
    const node = this.startNode();
    this.next(); // 消费 '<'
    
    if (this.match(tt.jsxTagEnd)) {
      // 解析闭合标签 </
      return this.parseJSXClosingElement();
    }
    
    // 解析开始标签
    const opening = this.parseJSXOpeningElement();
    let children = [];
    let closing = null;
    
    if (!opening.selfClosing) {
      // 解析子元素
      while (!this.match(tt.jsxTagStart) || !this.isJSXClosingElement()) {
        children.push(this.parseJSXChild());
      }
      closing = this.parseJSXClosingElement();
      
      // 验证标签匹配
      if (opening.name.name !== closing.name.name) {
        this.raise("Opening and closing tags must match");
      }
    }
    
    node.openingElement = opening;
    node.closingElement = closing;
    node.children = children;
    
    return this.finishNode(node, "JSXElement");
  }
  
  // 解析 JSX 属性
  parseJSXAttribute() {
    const node = this.startNode();
    
    if (this.match(tt.braceL)) {
      // 展开属性 {...props}
      node.argument = this.parseExpression();
      return this.finishNode(node, "JSXSpreadAttribute");
    }
    
    node.name = this.parseJSXIdentifier();
    node.value = this.eat(tt.eq) ? this.parseJSXAttributeValue() : null;
    
    return this.finishNode(node, "JSXAttribute");
  }
}
```

### 2.3 TypeScript 的 JSX 支持

TypeScript 有自己的 JSX 实现，用 **TypeScript** 编写：

```typescript
// TypeScript 编译器中的 JSX 解析（简化）
namespace ts {
  function parseJsxElement(): JsxElement {
    const pos = getNodePos();
    parseExpected(SyntaxKind.LessThanToken);
    
    const openingElement = parseJsxOpeningElement();
    
    let children: JsxChild[] | undefined;
    let closingElement: JsxClosingElement | undefined;
    
    if (!openingElement.selfClosing) {
      children = parseJsxChildren();
      closingElement = parseJsxClosingElement();
    }
    
    return finishNode(factory.createJsxElement(
      openingElement,
      children,
      closingElement
    ), pos);
  }
}
```

## 3. 其他 JSX 解析实现

### 3.1 ESBuild（Go 语言）

ESBuild 用 **Go** 语言实现了高性能的 JSX 解析：

```go
// ESBuild 的 JSX 解析器（简化）
func (p *parser) parseJSXElement(loc logger.Loc) js_ast.Expr {
    // 解析开始标签
    startTagOrSelfClosing := p.parseJSXTag()
    
    if startTagOrSelfClosing.selfClosing {
        return js_ast.Expr{Loc: loc, Data: &js_ast.EJSXElement{
            Tag:         startTagOrSelfClosing.tag,
            Properties:  startTagOrSelfClosing.properties,
            Children:    nil,
        }}
    }
    
    // 解析子元素
    children := []js_ast.Expr{}
    for {
        if p.lexer.Token == js_lexer.TLessThan {
            if p.lexer.IsJSXEndTag() {
                break
            }
            children = append(children, p.parseJSXElement())
        } else {
            children = append(children, p.parseJSXText())
        }
    }
    
    // 解析结束标签
    p.parseJSXClosingTag(startTagOrSelfClosing.tag)
    
    return js_ast.Expr{Loc: loc, Data: &js_ast.EJSXElement{
        Tag:        startTagOrSelfClosing.tag,
        Properties: startTagOrSelfClosing.properties,
        Children:   children,
    }}
}
```

### 3.2 SWC（Rust 语言）

SWC 是用 **Rust** 编写的超快速 JavaScript/TypeScript 编译器：

```rust
// SWC 的 JSX 解析实现（简化）
impl<I: Tokens> Parser<I> {
    fn parse_jsx_element(&mut self) -> PResult<Box<Expr>> {
        let start = cur_pos!(self);
        
        assert_and_bump!(self, "<");
        
        // 解析开始标签
        let opening = self.parse_jsx_opening_element()?;
        
        let mut children = vec![];
        let closing;
        
        if opening.self_closing {
            closing = None;
        } else {
            // 解析子元素
            'children: loop {
                match cur!(self) {
                    tok!("<") => {
                        if peeked_is!(self, "/") {
                            break 'children;
                        }
                        children.push(self.parse_jsx_element_child()?);
                    }
                    _ => {
                        children.push(self.parse_jsx_element_child()?);
                    }
                }
            }
            
            closing = Some(self.parse_jsx_closing_element()?);
        }
        
        Ok(Box::new(Expr::JSXElement(JSXElement {
            span: span!(self, start),
            opening,
            closing,
            children,
        })))
    }
}
```

## 4. JSX 转换的具体流程

### 4.1 解析阶段

```javascript
// 输入的 JSX
const App = () => {
  return (
    <div className="app">
      <h1>Welcome {user.name}</h1>
      <Button onClick={handleClick}>Click me</Button>
    </div>
  );
};
```

### 4.2 生成的 AST（简化）

```json
{
  "type": "JSXElement",
  "openingElement": {
    "type": "JSXOpeningElement",
    "name": { "type": "JSXIdentifier", "name": "div" },
    "attributes": [{
      "type": "JSXAttribute",
      "name": { "type": "JSXIdentifier", "name": "className" },
      "value": { "type": "StringLiteral", "value": "app" }
    }]
  },
  "children": [
    {
      "type": "JSXElement",
      "openingElement": {
        "name": { "type": "JSXIdentifier", "name": "h1" }
      },
      "children": [
        { "type": "JSXText", "value": "Welcome " },
        {
          "type": "JSXExpressionContainer",
          "expression": {
            "type": "MemberExpression",
            "object": { "type": "Identifier", "name": "user" },
            "property": { "type": "Identifier", "name": "name" }
          }
        }
      ]
    }
  ]
}
```

### 4.3 转换阶段

Babel 使用插件进行转换：

```javascript
// @babel/plugin-transform-react-jsx 的核心逻辑
module.exports = function ({ types: t }) {
  return {
    visitor: {
      JSXElement(path) {
        const openingElement = path.node.openingElement;
        const tagName = openingElement.name.name;
        
        // 收集属性
        const props = openingElement.attributes.map(attr => {
          if (t.isJSXAttribute(attr)) {
            return t.objectProperty(
              t.identifier(attr.name.name),
              attr.value
            );
          }
          // 处理展开属性等
        });
        
        // 收集子元素
        const children = path.node.children.map(child => {
          if (t.isJSXText(child)) {
            return t.stringLiteral(child.value);
          }
          if (t.isJSXExpressionContainer(child)) {
            return child.expression;
          }
          // 递归处理嵌套元素
        });
        
        // 替换为 React.createElement
        path.replaceWith(
          t.callExpression(
            t.memberExpression(
              t.identifier('React'),
              t.identifier('createElement')
            ),
            [
              t.stringLiteral(tagName),
              props.length ? t.objectExpression(props) : t.nullLiteral(),
              ...children
            ]
          )
        );
      }
    }
  };
};
```

## 5. 新的 JSX Transform（React 17+）

React 17 引入了新的 JSX 转换，不再需要导入 React：

```jsx
// 新的转换方式
// 输入
function App() {
  return <h1>Hello World</h1>;
}

// 输出（自动注入导入）
import { jsx as _jsx } from 'react/jsx-runtime';

function App() {
  return _jsx('h1', { children: 'Hello World' });
}
```

配置新转换：

```json
// babel.config.json
{
  "presets": [
    ["@babel/preset-react", {
      "runtime": "automatic"  // 使用新的转换
    }]
  ]
}
```

## 6. JSX 的语法定义（类 BNF）

```bnf
JSXElement ::= JSXSelfClosingElement | JSXOpeningElement JSXChildren? JSXClosingElement

JSXSelfClosingElement ::= '<' JSXElementName JSXAttributes? '/>'

JSXOpeningElement ::= '<' JSXElementName JSXAttributes? '>'

JSXClosingElement ::= '</' JSXElementName '>'

JSXElementName ::= JSXIdentifier | JSXNamespacedName | JSXMemberExpression

JSXAttributes ::= JSXAttribute JSXAttributes? | JSXSpreadAttribute JSXAttributes?

JSXAttribute ::= JSXAttributeName '=' JSXAttributeValue

JSXAttributeValue ::= StringLiteral | JSXExpressionContainer

JSXExpressionContainer ::= '{' Expression '}'

JSXChildren ::= JSXChild JSXChildren?

JSXChild ::= JSXText | JSXElement | JSXExpressionContainer
```

## 7. 性能对比

| 工具 | 语言 | 解析速度 | 特点 |
|------|------|----------|------|
| Babel | JavaScript | ★★★ | 功能最全，插件生态丰富 |
| TypeScript | TypeScript | ★★★ | 类型支持最好 |
| ESBuild | Go | ★★★★★ | 极快，但功能有限 |
| SWC | Rust | ★★★★★ | 快速，兼容性好 |
| Sucrase | JavaScript | ★★★★ | 专注开发环境 |

## 8. 自己实现简单的 JSX 解析器

```javascript
// 一个极简的 JSX 解析器示例
class SimpleJSXParser {
  constructor(input) {
    this.input = input;
    this.index = 0;
  }
  
  parse() {
    return this.parseElement();
  }
  
  parseElement() {
    this.consume('<');
    const tagName = this.parseIdentifier();
    const attributes = this.parseAttributes();
    
    if (this.peek() === '/') {
      this.consume('/');
      this.consume('>');
      return { type: 'element', tagName, attributes, children: [] };
    }
    
    this.consume('>');
    const children = this.parseChildren(tagName);
    this.consume('</');
    const closingTag = this.parseIdentifier();
    this.consume('>');
    
    if (tagName !== closingTag) {
      throw new Error(`Mismatched tags: ${tagName} and ${closingTag}`);
    }
    
    return { type: 'element', tagName, attributes, children };
  }
  
  parseAttributes() {
    const attrs = [];
    while (this.peek() !== '>' && this.peek() !== '/') {
      const name = this.parseIdentifier();
      this.consume('=');
      const value = this.parseAttributeValue();
      attrs.push({ name, value });
    }
    return attrs;
  }
  
  // ... 更多解析方法
}
```

## 总结

1. **React 本身**用 JavaScript 编写
2. **JSX 解析**主要通过 Babel（JavaScript）、TypeScript、ESBuild（Go）、SWC（Rust）等工具
3. **核心技术**是扩展 JavaScript 解析器以支持 XML-like 语法
4. **转换过程**：JSX → AST → JavaScript（React.createElement）
5. **性能优化**：使用 Go/Rust 重写的工具可以获得显著的性能提升

JSX 的成功展示了如何优雅地扩展现有语言语法，这种方法值得在设计 DSL 时借鉴。