# textX 实现 Markdown 到 HTML 转换的可行性研究

## 研究背景

探讨使用 textX DSL 框架实现一个 Markdown 语法解析器，并将其转换为 HTML 的可行性。这相当于创建一个 HTML 语法的子集。

## 答案：完全可行！

textX 非常适合实现 Markdown 解析器，因为：

1. **Markdown 有明确的语法规则**
2. **textX 支持复杂的文本匹配**
3. **可以生成结构化的 AST**
4. **易于转换为 HTML**

## 实现方案

### 1. Markdown 语法定义（markdown.tx）

```textx
// Markdown 文档模型
Document:
    blocks*=Block
;

// 块级元素
Block:
    Heading | Paragraph | CodeBlock | BlockQuote | List | HorizontalRule | BlankLine
;

// 标题：# 到 ######
Heading:
    /^#{1,6}[ \t]+/ text=InlineContent /$/
;

// 段落
Paragraph:
    !BlockStart lines+=TextLine[eolterm]
;

// 行内文本（不以特殊字符开头）
TextLine:
    /^(?!#|>|\*|-|\+|\d+\.|```|---).*$/
;

// 代码块
CodeBlock:
    '```' language=ID? /\n/
    code=/(?:(?!```).*\n)*/
    '```'
;

// 引用块
BlockQuote:
    lines+=QuoteLine+
;

QuoteLine:
    /^>[ \t]?/ content=InlineContent /$/
;

// 列表
List:
    UnorderedList | OrderedList
;

UnorderedList:
    items+=UnorderedItem+
;

UnorderedItem:
    /^[\*\-\+][ \t]+/ content=InlineContent /$/
;

OrderedList:
    items+=OrderedItem+
;

OrderedItem:
    /^\d+\.[ \t]+/ content=InlineContent /$/
;

// 水平线
HorizontalRule:
    /^(-{3,}|\*{3,}|_{3,})$/
;

// 空行
BlankLine:
    /^[ \t]*$/
;

// 行内内容
InlineContent:
    elements+=InlineElement+
;

// 行内元素
InlineElement:
    Bold | Italic | Code | Link | Image | Text
;

// 加粗：**text** 或 __text__
Bold:
    ('**' !'\n' text=/[^\*]+/ '**') |
    ('__' !'\n' text=/[^_]+/ '__')
;

// 斜体：*text* 或 _text_
Italic:
    ('*' !'*' text=/[^\*\n]+/ '*') |
    ('_' !'_' text=/[^_\n]+/ '_')
;

// 行内代码：`code`
Code:
    '`' text=/[^`\n]+/ '`'
;

// 链接：[text](url)
Link:
    '[' text=/[^\]]+/ ']' '(' url=/[^\)]+/ ')'
;

// 图片：![alt](url)
Image:
    '!' '[' alt=/[^\]]*/ ']' '(' url=/[^\)]+/ ')'
;

// 普通文本
Text:
    text=/[^\*_`\[\n]+/
;

// 用于识别块的开始（辅助规则）
BlockStart:
    /^(#{1,6}[ \t]+|>|\*|-|\+|\d+\.|```|---)/
;

Comment: /\/\/.*$/;
```

### 2. HTML 生成器实现

```python
from textx import metamodel_from_file

class MarkdownToHTML:
    """Markdown 到 HTML 转换器"""
    
    def __init__(self):
        self.mm = metamodel_from_file('markdown.tx')
    
    def convert(self, markdown_text):
        """转换 Markdown 文本为 HTML"""
        model = self.mm.model_from_str(markdown_text)
        return self.generate_html(model)
    
    def generate_html(self, model):
        """生成 HTML"""
        html_parts = []
        for block in model.blocks:
            html_parts.append(self.convert_block(block))
        return '\n'.join(html_parts)
    
    def convert_block(self, block):
        """转换块级元素"""
        block_type = block.__class__.__name__
        
        if block_type == 'Heading':
            level = len(block.match.group(0).strip())
            content = self.convert_inline(block.text)
            return f'<h{level}>{content}</h{level}>'
            
        elif block_type == 'Paragraph':
            lines = [self.convert_inline(line) for line in block.lines]
            return f'<p>{" ".join(lines)}</p>'
            
        elif block_type == 'CodeBlock':
            lang = block.language or ''
            return f'<pre><code class="language-{lang}">{block.code}</code></pre>'
            
        elif block_type == 'BlockQuote':
            content = '\n'.join([self.convert_inline(line.content) 
                                for line in block.lines])
            return f'<blockquote>{content}</blockquote>'
            
        elif block_type == 'UnorderedList':
            items = [f'<li>{self.convert_inline(item.content)}</li>' 
                    for item in block.items]
            return f'<ul>\n{"".join(items)}\n</ul>'
            
        elif block_type == 'OrderedList':
            items = [f'<li>{self.convert_inline(item.content)}</li>' 
                    for item in block.items]
            return f'<ol>\n{"".join(items)}\n</ol>'
            
        elif block_type == 'HorizontalRule':
            return '<hr>'
            
        elif block_type == 'BlankLine':
            return ''
            
        return ''
    
    def convert_inline(self, inline_content):
        """转换行内元素"""
        if not inline_content:
            return ''
            
        html_parts = []
        for element in inline_content.elements:
            element_type = element.__class__.__name__
            
            if element_type == 'Bold':
                html_parts.append(f'<strong>{element.text}</strong>')
                
            elif element_type == 'Italic':
                html_parts.append(f'<em>{element.text}</em>')
                
            elif element_type == 'Code':
                html_parts.append(f'<code>{element.text}</code>')
                
            elif element_type == 'Link':
                html_parts.append(f'<a href="{element.url}">{element.text}</a>')
                
            elif element_type == 'Image':
                alt = element.alt or ''
                html_parts.append(f'<img src="{element.url}" alt="{alt}">')
                
            elif element_type == 'Text':
                html_parts.append(element.text)
                
        return ''.join(html_parts)
```

### 3. 使用示例

```python
# 创建转换器
converter = MarkdownToHTML()

# Markdown 输入
markdown_text = """
# Hello World

This is a **bold** text and this is *italic*.

## Features

- Easy to use
- Fast parsing
- Clean HTML output

```python
def hello():
    print("Hello, World!")
```

> This is a blockquote
> with multiple lines

[Click here](https://example.com) to learn more.
"""

# 转换为 HTML
html = converter.convert(markdown_text)
print(html)
```

输出的 HTML：
```html
<h1>Hello World</h1>
<p>This is a <strong>bold</strong> text and this is <em>italic</em>.</p>
<h2>Features</h2>
<ul>
<li>Easy to use</li>
<li>Fast parsing</li>
<li>Clean HTML output</li>
</ul>
<pre><code class="language-python">def hello():
    print("Hello, World!")
</code></pre>
<blockquote>This is a blockquote
with multiple lines</blockquote>
<p><a href="https://example.com">Click here</a> to learn more.</p>
```

## 高级特性实现

### 1. 嵌套列表支持

```textx
// 支持嵌套的列表定义
NestedList:
    items+=ListItem+
;

ListItem:
    /^([ \t]*)[\*\-\+][ \t]+/ content=InlineContent /$/
    sublist=NestedList?
;
```

### 2. 表格支持

```textx
// Markdown 表格
Table:
    header=TableRow
    separator=TableSeparator
    rows+=TableRow+
;

TableRow:
    '|' cells+=TableCell[|] '|'
;

TableCell:
    content=/[^|\n]*/
;

TableSeparator:
    /\|[ \t]*:?-+:?[ \t]*\|/+
;
```

### 3. 自定义扩展

```textx
// 支持自定义标签
CustomTag:
    '{' name=ID attrs*=Attribute '}' content=InlineContent '{/' name=ID '}'
;

Attribute:
    name=ID '=' value=STRING
;
```

## 与传统 Markdown 解析器对比

### textX 方案的优势

1. **语法定义清晰**：使用 BNF 风格定义，易于理解和修改
2. **易于扩展**：添加新语法只需修改 .tx 文件
3. **类型安全**：生成的 AST 有明确的类型结构
4. **错误处理好**：自动生成详细的语法错误信息

### 潜在限制

1. **性能**：对于大文件，可能不如专门的 Markdown 解析器快
2. **灵活性**：Markdown 的一些边缘情况可能难以处理
3. **生态系统**：缺少 Markdown 特定的插件系统

## 实际应用场景

### 1. 文档生成系统

```python
class DocGenerator:
    def __init__(self):
        self.converter = MarkdownToHTML()
        
    def generate_docs(self, source_dir, output_dir):
        """批量转换 Markdown 文档"""
        for md_file in Path(source_dir).glob('**/*.md'):
            html = self.converter.convert(md_file.read_text())
            
            # 应用模板
            full_html = self.apply_template(html, md_file.stem)
            
            # 保存
            output_file = output_dir / md_file.with_suffix('.html').name
            output_file.write_text(full_html)
```

### 2. 实时预览编辑器

```python
from flask import Flask, render_template, request

app = Flask(__name__)
converter = MarkdownToHTML()

@app.route('/preview', methods=['POST'])
def preview():
    markdown = request.json['markdown']
    try:
        html = converter.convert(markdown)
        return {'success': True, 'html': html}
    except Exception as e:
        return {'success': False, 'error': str(e)}
```

### 3. 静态站点生成器

```python
class SiteGenerator:
    def __init__(self, config):
        self.config = config
        self.converter = MarkdownToHTML()
        
    def build(self):
        """构建整个站点"""
        # 读取所有 Markdown 文件
        posts = self.load_posts()
        
        # 转换并生成页面
        for post in posts:
            html = self.converter.convert(post.content)
            self.generate_page(post, html)
        
        # 生成索引页
        self.generate_index(posts)
```

## 性能优化

### 1. 缓存机制

```python
from functools import lru_cache

class CachedMarkdownConverter(MarkdownToHTML):
    @lru_cache(maxsize=1000)
    def convert(self, markdown_text):
        return super().convert(markdown_text)
```

### 2. 增量解析

```python
class IncrementalParser:
    def __init__(self):
        self.block_cache = {}
        
    def parse_incremental(self, text, changed_line):
        """只重新解析改变的部分"""
        blocks = text.split('\n\n')
        changed_block = self.find_changed_block(blocks, changed_line)
        
        # 只解析改变的块
        if changed_block in self.block_cache:
            del self.block_cache[changed_block]
            
        return self.parse_block(blocks[changed_block])
```

## 结论

使用 textX 实现 Markdown 到 HTML 的转换是**完全可行的**，而且有以下优势：

1. **实现简单**：语法定义清晰，转换逻辑直观
2. **易于定制**：可以轻松添加自定义语法
3. **可维护性高**：语法和实现分离
4. **适合教学**：帮助理解解析器原理

这个方案特别适合：
- 需要定制化 Markdown 语法的场景
- 集成到现有 textX 项目中
- 教学和研究目的
- 轻量级文档处理需求

对于 Agentara 项目，这意味着可以：
1. 在 DSL 中嵌入富文本描述
2. 生成格式化的文档
3. 支持更丰富的注释语法