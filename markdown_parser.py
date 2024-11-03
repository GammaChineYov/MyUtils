# markdown_parser.py
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
import os
import logging as log
from enum import Enum
from markdown_it import MarkdownIt
import traceback
from create_dir_structure import create_dir_structure
from extract_file_paths import extract_path, find_longest_path


class NodeType(Enum):
    HEADING = "heading"
    CODE_BLOCK = "code_block"

class Node:
    """节点类，表示结构树中的每个节点。"""

    def __init__(self, level, title=None, content=None, node_type=None, code_type=""):
        self.level = level
        self.title = title
        self.content = content
        self.type = node_type
        self.code_type = code_type
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
        """根据类型查找节点。"""
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
                code_node = Node(
                  level=stack[-1].level + 1, 
                  content=code_content, 
                  node_type='code_block',
                  code_type=token.info)
                
                if stack:
                    stack[-1].add_child(code_node)

        return root

    except Exception as e:
        log.error("Markdown parsing failed: ", exc_info=True)
        return None

def extract_code(content):
    tree = parse_markdown(content)
    if not tree:
        return []

    code_nodes = tree.find_type('code_block')
    data = []
    for code_node in code_nodes:
        code_text = code_node.content
        # 假设 `find_longest_path` 是已定义的函数，用于根据代码内容获取路径
        path = find_longest_path("\n".join(code_text.strip().split("\n")[:2]), code_node.parent.title)  
        code_type = code_node.code_type

        if code_type == "plaintext":
            path = "project_structure.txt"
        data.append({
            "relative_path": path, 
            "code_type": code_type, 
            "content": code_text
        })
    return data

def get_plaintext_file(codes):
    for item in codes:
        if item["code_type"] == "plaintext":
            return item
    return {}

def process_markdown(markdown_content: str, project_dir: str, is_create_dir_structure: bool = True, is_create_file: bool = True, is_replace_file: bool = True) -> None:
    """
    处理 Markdown 内容，根据参数创建目录结构和文件。

    参数：
    - markdown_content：Markdown 文本内容。
    - project_dir：项目目录路径。
    - is_create_dir_structure：是否创建目录结构，默认为 True。
    - is_create_file：是否创建文件，默认为 True。
    - is_replace_file：是否替换已存在的文件，默认为 True。
    """
    code_files = extract_code(markdown_content)
    directory_structure = get_plaintext_file(code_files)

    if is_create_dir_structure:
        if directory_structure:
            try:
                create_dir_structure(directory_structure["content"], project_dir, is_replace_file)
                print("目录结构创建成功。")
            except Exception as e:
                print("创建目录结构时出现错误：")
                traceback.print_exc()
        else:
            print("没有检测到plaintext目录结构文档")
    else:
        print("跳过创建目录结构。")

    for item in code_files:
        rel_path = item["relative_path"]
        content = item["content"]
        if not rel_path:
            print("rel_path提取失败：无法找到文件名,内容：", content)
            continue
        filepath = os.path.join(project_dir, rel_path)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if is_create_file:
            if not os.path.exists(filepath) or is_replace_file:
                try:
                    with open(filepath, "w") as f:
                        f.write(content)
                    print(f"文件 {filepath} 创建/更新成功。")
                except Exception as e:
                    print(f"写入文件 {filepath} 时出现错误：{e}")
            else:
                print(f"跳过写入已存在的文件 {filepath}，因为不启用替换。")
        else:
            print("跳过文件创建。")

# 示例用法
if __name__ == "__main__":
    markdown_text = """
    # 项目结构

    ## 主程序文件
    main.py # 主程序文件，包含Gradio界面的构建和各功能模块的集成调用

    ## 配置模块
    config/repo_config.py # 基础配置脚本，包含仓库路径配置、创建符号链接等相关功能

    ## Git功能模块
    git_functions/git_utils.py # Git操作工具模块，包含提交、推送、克隆、拉取等Git功能的实现

    ## 文件操作模块
    file_operations/file_utils.py # 文件操作工具模块，包含文件打开、备份、注释打印等功能

    ## 资源文件夹
    assets/需求说明.txt # 项目需求说明文件，描述项目需求和功能
    """
    markdown_text = open("temp.txt","r").read()+"\n\n\n\n"
    project_dir = "/content/utils/QuickUI"
    process_markdown(markdown_text, project_dir)
