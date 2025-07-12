# textX 实现 HTML 语法解析的可行性研究

## 问题定义

探讨使用 textX (基于 BNF/EBNF) 来定义和解析 HTML 这种具有开闭标签的 XML 风格语法的可行性。

## 核心挑战

HTML/XML 语法的特点：
1. **嵌套结构**：`<div><p>text</p></div>`
2. **开闭标签匹配**：每个开标签需要对应的闭标签
3. **自闭合标签**：`<img />`, `<br />`
4. **属性语法**：`<div class="container" id="main">`
5. **混合内容**：标签和文本可以混合

## textX 实现 HTML 的可行性分析

### 答案：可以实现，但有挑战

textX **可以**解析 HTML，但需要巧妙的语法设计：

### 1. 基础 HTML 语法定义（可行但复杂）

```textx
// HTML 文档
Document:
    '<!DOCTYPE' doctype=/[^>]+/ '>'
    root=Element
;

// 元素定义 - 这是关键挑战
Element:
    SelfClosingElement | NormalElement
;

// 自闭合元素
SelfClosingElement:
    '<' name=TagName attributes*=Attribute '/>'
;

// 普通元素（开闭标签）
NormalElement:
    '<' openTag=TagName attributes*=Attribute '>'
    content*=Content
    '</' closeTag=TagName '>'
;

// 内容：文本或嵌套元素
Content:
    Text | Element
;

// 文本内容
Text:
    content=/[^<]+/
;

// 标签名
TagName:
    name=ID
;

// 属性
Attribute:
    name=ID ('=' value=AttributeValue)?
;

AttributeValue:
    STRING | ID | NUMBER
;
```

### 2. 标签匹配验证（需要语义验证）

```python
from textx import metamodel_from_str

# 注册验证器确保开闭标签匹配
def validate_element(element):
    if hasattr(element, 'openTag') and hasattr(element, 'closeTag'):
        if element.openTag.name != element.closeTag.name:
            raise TextXSemanticError(
                f"标签不匹配: <{element.openTag.name}> ... </{element.closeTag.name}>"
            )

mm = metamodel_from_str(grammar)
mm.register_obj_processors({
    'NormalElement': validate_element
})
```

### 3. 更复杂的实现（处理 HTML 特性）

```textx
// 支持更多 HTML 特性
HTMLDocument:
    doctype=DOCTYPE?
    elements+=Element
;

Element:
    VoidElement     |  // <br>, <img>, <input>
    RawTextElement  |  // <script>, <style>
    NormalElement      // 其他所有元素
;

// 空元素（HTML5 不需要闭合）
VoidElement:
    '<' name=VoidTagName attributes*=Attribute '>'
;

VoidTagName:
    'area' | 'base' | 'br' | 'col' | 'embed' | 'hr' | 
    'img' | 'input' | 'link' | 'meta' | 'source' | 
    'track' | 'wbr'
;

// 原始文本元素（内容不解析）
RawTextElement:
    ScriptElement | StyleElement
;

ScriptElement:
    '<script' attributes*=Attribute '>'
    content=/(?:(?!<\/script>).)*/ 
    '</script>'
;

// 普通元素（递归定义）
NormalElement:
    '<' tag=TagName attributes*=Attribute '>'
    children*=Content
    '</' !VoidTagName tag=[TagName] '>'  // 引用开标签
;
```

## 主要问题和限制

### 1. 开闭标签匹配
BNF 本身不能强制要求开闭标签名称相同，需要额外的语义验证。

### 2. 错误恢复
HTML 解析器通常有强大的错误恢复机制（如浏览器的容错性），textX 较难实现。

### 3. 性能问题
对于大型 HTML 文档，递归下降解析可能较慢。

### 4. HTML 的不规则性
真实的 HTML 有很多不规则情况：
- 未闭合的标签
- 错误嵌套
- 隐式闭合规则

## HTML 实际使用的解析技术

### 1. HTML5 解析算法
HTML5 规范定义了一个**状态机**解析器，而不是基于 BNF：

```
Data state → Tag open state → Tag name state → ...
```

这是因为 HTML 需要：
- 容错处理
- 错误恢复
- 向后兼容

### 2. 常见的 HTML 解析器

1. **浏览器引擎**：
   - Chrome/Edge: Blink 
   - Firefox: Gecko
   - Safari: WebKit
   都使用手写的状态机解析器

2. **库**：
   - BeautifulSoup (Python): 使用 html.parser 或 lxml
   - Cheerio (Node.js): 使用 htmlparser2
   - Jsoup (Java): 手写的解析器

### 3. XML 解析器
XML（HTML 的严格版本）通常使用：
- **SAX**: 事件驱动
- **DOM**: 构建完整树
- **StAX**: 拉取式解析

## 更适合的方案

### 1. 使用 PEG（解析表达式语法）

```peg
# PEG 更适合处理 HTML
Document <- Element*
Element <- OpenTag Content* CloseTag / SelfClosingTag
OpenTag <- '<' TagName Attribute* '>'
CloseTag <- '</' TagName '>'
Content <- Text / Element
```

PEG 的优势：
- 支持有序选择
- 更好的回溯
- 可以处理上下文相关语法

### 2. 使用 ANTLR

ANTLR 是更强大的解析器生成器：

```antlr
grammar HTML;

document : element* ;

element 
    : '<' startTag=Name attribute* '>' content* '</' endTag=Name '>'
    | '<' Name attribute* '/>'
    ;

content : TEXT | element ;

attribute : Name ('=' value)? ;
```

### 3. 使用专门的 XML 解析器

```python
# 使用 lxml
from lxml import etree

parser = etree.HTMLParser()
tree = etree.parse(StringIO(html_string), parser)
```

## 结论和建议

### textX 能否解析 HTML？
**能，但不理想**。主要问题：
1. 需要复杂的语法定义
2. 需要额外的验证逻辑
3. 缺乏 HTML 特有的容错机制
4. 性能可能不够理想

### 推荐方案

1. **如果必须用 textX**：
   - 定义 HTML 的严格子集
   - 添加自定义验证器
   - 只支持良构的 HTML

2. **如果要完整支持 HTML**：
   - 使用现有的 HTML 解析库
   - 或使用 ANTLR/PEG
   - 或实现状态机解析器

3. **如果是为了 Agentara 项目**：
   考虑定义一个更简单的标记语言，比如：
   ```
   {div class="container"}
       {p}Hello World{/p}
   {/div}
   ```
   这种语法更适合 BNF 风格的解析器。

### 最终建议

对于 Agentara 项目，如果需要富文本功能，建议：

1. **使用 Markdown**：简单，适合 textX
2. **定义简化的标记语言**：避免 HTML 的复杂性
3. **嵌入 HTML**：将 HTML 作为字符串处理，不解析
4. **使用模板语言**：如 Jinja2 风格的语法

```textx
// 更适合 textX 的模板语法
Template:
    blocks*=Block
;

Block:
    TextBlock | TagBlock | ExpressionBlock
;

TagBlock:
    '{' tag=ID attributes*=Attribute '}'
    content*=Block
    '{/' tag=ID '}'
;
```

这样既有结构化的优势，又避免了 HTML 解析的复杂性。