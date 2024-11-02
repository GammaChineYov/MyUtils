# 相对路径: ./markdown_tree.py
"""
简介：解析 Markdown 文本，生成标题层级结构树，并可选择包含代码块，支持父级访问和查找功能。
使用方法：调用 parse_markdown 函数并传入 Markdown 文本和是否包含代码块的参数，返回结构对象。
工作流：
1. 导入必要的模块
2. 定义节点类
3. 定义解析函数
4. 生成结构树
5. 输出结构树
"""

import re
import json
from markdown_it import MarkdownIt
from enum import Enum


class NodeType(Enum):
    HEADING = "heading"
    CODE_BLOCK = "code_block"
    # 可以添加更多类型


class Node:
    """节点类，表示结构树中的每个节点。"""

    def __init__(self, level, title=None, content=None, node_type=None):
        self.level = level
        self.title = title
        self.content = content
        self.type = node_type
        self.children = []
        self.parent = None

    def add_child(self, child):
        """添加子节点并设置父节点。"""
        child.parent = self
        self.children.append(child)

    def find_title(self, title_pattern):
        """根据标题进行正则查找。"""
        if re.search(title_pattern, self.title or '', re.UNICODE):
            yield self
        for child in self.children:
            yield from child.find_title(title_pattern)

    def find_content(self, content_pattern):
        """根据内容进行正则查找。"""
        if self.content and re.search(content_pattern, self.content, re.UNICODE):
            yield self
        for child in self.children:
            yield from child.find_content(content_pattern)

    def find_type(self, node_type):
        """根据类型查找节点。
        heading_open: 标题开始标签（如 h1, h2, h3）
        heading_close: 标题结束标签
        inline: 行内内容
        fence: 代码块
        code_block: 代码块（带语言标记）
        text: 普通文本
"""
        if self.type == node_type:
            yield self
        for child in self.children:
            yield from child.find_type(node_type)

    def to_dict(self):
        """将节点及其子节点转换为字典结构。"""
        return {
            'level': self.level,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'children': [child.to_dict() for child in self.children]
        }

    def __str__(self):
        """返回节点的 JSON 结构表示。"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def __repr__(self):
        return self.__str__()

def parse_markdown(markdown_text, include_code_blocks=True):
    """
    解析 Markdown 文本，生成结构树，包括可选的代码块。

    使用方法：
    tree = parse_markdown('你的 Markdown 文本', include_code_blocks=True)
    
    工作流：
    1. 解析文本
    2. 构建结构树
    """
    try:
        md = MarkdownIt()
        tokens = md.parse(markdown_text)

        root = Node(level=0)  # 根节点
        stack = [root]
        
        for token in tokens:
            if token.type == 'heading_open':
                level = int(token.tag[1])  # 获取标题级别
                title_token = tokens[tokens.index(token) + 1]
                title = title_token.content if title_token.type == 'inline' else ''

                # 创建标题节点
                node = Node(level, title=title, node_type='heading')

                # 调整栈以匹配层级
                while stack and stack[-1].level >= level:
                    stack.pop()

                stack[-1].add_child(node)
                stack.append(node)

            elif token.type == 'fence' and include_code_blocks:  # 处理代码块
                code_content = token.content.strip()  # 获取代码内容
                code_node = Node(level=stack[-1].level + 1, content=code_content, node_type='code')

                if stack:
                    stack[-1].add_child(code_node)

        return root

    except Exception as e:
        return None


from extract_file_paths import find_longest_path
import os

def markdown_extract_code_to_file(content, project_path):
  tree = parse_markdown(content)
  code_nodes = tree.find_type('code')
  for code_node in code_nodes:
    code_text = code_node.content
    path = find_longest_path(code_text.strip(), code_node.parent.title)
    filepath = os.path.join(project_path, path)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    # 写入
    with open(filepath, 'w') as f:
      f.write(code_text)
      print(f"写入成功->{filepath}")

# 示例用法
if __name__ == "__main__":
    markdown_text = """# 一级标题
## 二级标题1
### 三级标题1

```
print("Hello, World!")
```
## 二级标题2
# 另一个一级标题"""
    
    tree = parse_markdown(markdown_text)
    print("生成的结构树:")
    print(tree)
