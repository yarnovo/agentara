# HTML/XML 解析器原理与自定义标记语言设计指南

## 引言

HTML 和 XML 看起来简单，但解析它们却充满挑战。本文将深入探讨标记语言的解析原理，并教你如何设计自己的标记语言。

## 第一部分：HTML/XML 解析器原理

### 1. 为什么 HTML 解析这么复杂？

考虑这个"简单"的 HTML：
```html
<p>Hello <b>World</p></b>
```

这是错误的 HTML（标签交叉了），但浏览器必须能处理它！这就是 HTML 解析的核心挑战：**容错性**。

### 2. HTML5 解析器的工作原理

HTML5 定义了一个**确定性的状态机解析算法**，主要包含：

#### 2.1 分词器（Tokenizer）

分词器有多种状态：
```
Data state (初始状态)
    ↓ 遇到 '<'
Tag open state
    ↓ 遇到 '/'
End tag open state
    ↓ 遇到字母
Tag name state
    ... 等等
```

**状态机示例**：
```python
class HTMLTokenizer:
    def __init__(self):
        self.state = "DATA"
        self.current_token = None
        
    def consume(self, char):
        if self.state == "DATA":
            if char == "<":
                self.state = "TAG_OPEN"
            else:
                self.emit_character(char)
                
        elif self.state == "TAG_OPEN":
            if char == "/":
                self.state = "END_TAG_OPEN"
            elif char.isalpha():
                self.current_token = {"type": "start_tag", "name": char}
                self.state = "TAG_NAME"
            # ... 更多状态处理
```

#### 2.2 树构建器（Tree Constructor）

树构建器维护一个**开放元素栈**：

```python
class TreeBuilder:
    def __init__(self):
        self.open_elements = []  # 栈
        self.document = Document()
        
    def process_token(self, token):
        if token["type"] == "start_tag":
            element = Element(token["name"])
            self.current_node.append_child(element)
            self.open_elements.append(element)
            
        elif token["type"] == "end_tag":
            # 查找匹配的开始标签
            self.close_element(token["name"])
```

#### 2.3 错误恢复机制

HTML5 定义了精确的错误恢复规则：

```python
def handle_mismatched_tag(self, tag_name):
    # 情况：</p> 但栈顶是 <b>
    # 解决：隐式关闭 <b>，然后关闭 <p>
    
    while self.open_elements:
        current = self.open_elements[-1]
        if current.name == tag_name:
            self.open_elements.pop()
            break
        else:
            # 隐式关闭
            self.open_elements.pop()
            if self.is_special_element(current):
                break
```

### 3. XML 解析器原理

XML 解析器比 HTML 简单，因为它**不容错**：

#### 3.1 SAX（Simple API for XML）

事件驱动的解析方式：

```python
class MySAXHandler:
    def startElement(self, name, attrs):
        print(f"开始标签: {name}")
        
    def endElement(self, name):
        print(f"结束标签: {name}")
        
    def characters(self, content):
        print(f"文本内容: {content}")

# 使用
parser = xml.sax.make_parser()
parser.setContentHandler(MySAXHandler())
parser.parse("document.xml")
```

#### 3.2 DOM（Document Object Model）

构建完整的文档树：

```python
import xml.dom.minidom

# 解析 XML
dom = xml.dom.minidom.parse("document.xml")

# 遍历
for node in dom.getElementsByTagName("item"):
    print(node.getAttribute("id"))
```

#### 3.3 StAX（Streaming API for XML）

拉取式解析（主要在 Java 中）：

```java
XMLStreamReader reader = XMLInputFactory.newInstance()
    .createXMLStreamReader(new FileInputStream("doc.xml"));
    
while (reader.hasNext()) {
    int event = reader.next();
    switch (event) {
        case XMLStreamConstants.START_ELEMENT:
            System.out.println("Start: " + reader.getLocalName());
            break;
        // ...
    }
}
```

### 4. 实际的 HTML 解析器实现

让我们看看真实的解析器是如何工作的：

#### 4.1 BeautifulSoup（Python）

```python
from bs4 import BeautifulSoup

# BeautifulSoup 使用不同的后端解析器
html = "<p>Hello <b>World</p></b>"

# 使用 Python 内置解析器
soup1 = BeautifulSoup(html, 'html.parser')
# 结果: <p>Hello <b>World</b></p>

# 使用 lxml（更严格）
soup2 = BeautifulSoup(html, 'lxml')
# 结果: <html><body><p>Hello <b>World</b></p></body></html>
```

#### 4.2 浏览器解析器的特殊规则

```javascript
// 浏览器的解析有特殊规则
document.write('<table><tr><div>content</div></tr></table>');
// div 会被移出 table，因为 table 内不能直接放 div

document.write('<p>段落1<p>段落2');
// 自动补全为：<p>段落1</p><p>段落2</p>
```

## 第二部分：设计自定义标记语言

### 1. 设计原则

#### 1.1 明确目标

问自己：
- 为什么需要新的标记语言？
- 目标用户是谁？
- 需要什么特性？

#### 1.2 简洁性 vs 表达力

```
太简单：[b]粗体[/b]           # BBCode 风格
平衡：**粗体**                # Markdown 风格  
太复杂：<b class="bold">粗体</b>  # HTML 风格
```

### 2. 实战：设计一个文档标记语言

让我们设计一个介于 Markdown 和 HTML 之间的标记语言。

#### 2.1 语法设计

```
@ 这是我们的文档标记语言 (DML - Document Markup Language)

@document "我的文档" {
    @meta {
        author: "张三"
        date: 2024-01-15
        tags: [教程, 标记语言]
    }
    
    @section "介绍" {
        这是普通段落。支持 *斜体* 和 **粗体**。
        
        @note {
            这是一个注释块。
        }
        
        @code python {
            def hello():
                print("Hello, World!")
        }
    }
    
    @section "列表示例" {
        @list {
            - 项目 1
            - 项目 2
              - 子项目 2.1
              - 子项目 2.2
        }
    }
}
```

#### 2.2 使用 Lark 实现解析器

```python
from lark import Lark, Transformer, v_args

# 定义语法
dml_grammar = r"""
start: document

document: "@document" string "{" meta? section* "}"

meta: "@meta" "{" meta_item* "}"
meta_item: WORD ":" (string | number | array)

section: "@section" string "{" content* "}"

content: paragraph 
       | note 
       | code_block 
       | list_block

paragraph: text+

note: "@note" "{" text+ "}"

code_block: "@code" WORD "{" code_content "}"
code_content: /[^}]+/

list_block: "@list" "{" list_item+ "}"
list_item: "-" text+

text: WORD 
    | formatted_text 
    | string 
    | number

formatted_text: "*" WORD "*"           -> italic
              | "**" WORD "**"         -> bold

array: "[" [WORD ("," WORD)*] "]"

string: ESCAPED_STRING
number: NUMBER

%import common.WORD
%import common.NUMBER
%import common.ESCAPED_STRING
%import common.WS
%ignore WS
"""

# 创建解析器
dml_parser = Lark(dml_grammar, start='start')

# 转换器：将解析树转换为 HTML
@v_args(inline=True)
class DMLToHTML(Transformer):
    def document(self, title, *contents):
        meta = ""
        sections = []
        for item in contents:
            if isinstance(item, dict) and "meta" in item:
                meta = item["meta"]
            else:
                sections.append(item)
                
        return f"""
        <article>
            <h1>{title}</h1>
            {meta}
            {''.join(sections)}
        </article>
        """
    
    def section(self, title, *contents):
        return f"""
        <section>
            <h2>{title}</h2>
            {''.join(contents)}
        </section>
        """
    
    def paragraph(self, *texts):
        return f"<p>{''.join(texts)}</p>"
    
    def italic(self, text):
        return f"<em>{text}</em>"
    
    def bold(self, text):
        return f"<strong>{text}</strong>"
    
    def code_block(self, language, code):
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    def note(self, *texts):
        return f'<div class="note">{''.join(texts)}</div>'
    
    def list_block(self, *items):
        return f"<ul>{''.join(items)}</ul>"
    
    def list_item(self, *texts):
        return f"<li>{''.join(texts)}</li>"
    
    def string(self, s):
        return s[1:-1]  # 去掉引号
    
    def number(self, n):
        return str(n)
    
    def WORD(self, w):
        return str(w)
```

#### 2.3 使用示例

```python
# 解析 DML
dml_text = '''
@document "使用指南" {
    @meta {
        author: "张三"
        date: 2024-01-15
    }
    
    @section "简介" {
        DML 是一种新的标记语言。
        支持 *斜体* 和 **粗体** 文本。
        
        @note {
            这是一个提示信息。
        }
    }
}
'''

# 解析并转换
tree = dml_parser.parse(dml_text)
html = DMLToHTML().transform(tree)
print(html)
```

### 3. 高级设计：混合语言

#### 3.1 嵌入其他语言

```
@document {
    @section "代码示例" {
        这里是说明文字。
        
        @embed markdown {
            # Markdown 标题
            
            - 列表项1
            - 列表项2
            
            [链接](http://example.com)
        }
        
        @embed html {
            <table>
                <tr><td>直接嵌入的 HTML</td></tr>
            </table>
        }
    }
}
```

#### 3.2 实现嵌入式解析

```python
class EmbeddedLanguageProcessor:
    def __init__(self):
        self.processors = {
            'markdown': self.process_markdown,
            'html': self.process_html,
            'latex': self.process_latex
        }
    
    def process_embed(self, language, content):
        processor = self.processors.get(language)
        if processor:
            return processor(content)
        return f"<pre>{content}</pre>"  # 默认处理
    
    def process_markdown(self, content):
        import markdown
        return markdown.markdown(content)
    
    def process_html(self, content):
        # 清理和验证 HTML
        from bleach import clean
        return clean(content, tags=['table', 'tr', 'td', 'th'])
```

### 4. 设计自定义标记语言的最佳实践

#### 4.1 保持一致性

```
坏例子：
@title: 我的标题      # 用冒号
@author = 张三        # 用等号
@date "2024-01-15"   # 直接跟值

好例子：
@title: "我的标题"
@author: "张三"
@date: "2024-01-15"
```

#### 4.2 提供清晰的错误信息

```python
def parse_with_error_handling(text):
    try:
        return parser.parse(text)
    except Exception as e:
        line_no = e.line
        column = e.column
        
        # 提供上下文
        lines = text.split('\n')
        error_line = lines[line_no - 1]
        
        print(f"解析错误在第 {line_no} 行，第 {column} 列：")
        print(error_line)
        print(" " * (column - 1) + "^")
        print(f"错误：{e}")
```

#### 4.3 考虑扩展性

```python
# 插件系统
class DMLExtension:
    def __init__(self, name, pattern, handler):
        self.name = name
        self.pattern = pattern
        self.handler = handler

# 注册自定义标签
extensions = []

def register_extension(name, pattern, handler):
    extensions.append(DMLExtension(name, pattern, handler))

# 使用
register_extension(
    "youtube",
    r"@youtube\s+(\S+)",
    lambda match: f'<iframe src="https://youtube.com/embed/{match.group(1)}"></iframe>'
)
```

### 5. 性能优化

#### 5.1 缓存解析结果

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def parse_and_cache(text_hash):
    return parser.parse(text)

def parse_dml(text):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    return parse_and_cache(text_hash)
```

#### 5.2 流式解析

```python
class StreamingDMLParser:
    def __init__(self):
        self.buffer = ""
        self.in_block = False
        
    def feed(self, chunk):
        self.buffer += chunk
        
        # 查找完整的块
        while True:
            if not self.in_block:
                start = self.buffer.find('@')
                if start == -1:
                    break
                self.in_block = True
                
            # 查找块结束
            end = self.find_block_end(self.buffer)
            if end == -1:
                break
                
            # 处理完整块
            block = self.buffer[:end]
            self.process_block(block)
            self.buffer = self.buffer[end:]
            self.in_block = False
```

## 总结

1. **HTML/XML 解析器**使用状态机和栈来处理嵌套结构
2. **HTML 解析**的核心是容错和错误恢复
3. **设计标记语言**需要平衡简洁性和功能性
4. **实现解析器**可以使用现有工具（Lark、ANTLR）
5. **最佳实践**包括一致性、错误处理和扩展性

记住：最好的标记语言是用户爱用的语言！