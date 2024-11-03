import json
import os
import re
import logging
from extract_file_paths import extract_path

# 设置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# 设置打印等级为 INFO
logging.getLogger().setLevel(logging.DEBUG)

class Node:
    """
    目录结构节点类，用于表示文件或文件夹信息。
    包含路径、描述、类型、子节点、父节点以及层级信息。
    """

    def __init__(self, path: str, desc: str, node_type: str, level: int):
        """
        初始化节点。

        参数：
        - path: 节点路径。
        - desc: 节点描述。
        - node_type: 节点类型 ('file' 或 'directory')。
        - level: 节点层级。
        """
        self.path = path
        self.desc = desc
        self.type = node_type
        self.children = []
        self.parent = None
        self.level = level

    def add_child(self, child: 'Node'):
        """添加子节点并设置父节点"""
        self.children.append(child)
        child.parent = self


def parse_directory_structure(dir_structure_text: str) -> Node:
    """
    解析目录结构文本，生成目录结构的根节点。

    参数：
    - dir_structure_text：包含目录结构描述的文本。

    返回：根节点（Node 对象）。
    """
    lines = dir_structure_text.strip().splitlines()
    root = None
    current_node = None
    
    for line in lines:
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue

        match_res_list = extract_path(line)
        if not match_res_list:
            continue
        
        match_res = match_res_list[0]
        path = match_res.output
        current_level = line.index(path)  # 当前层级
        
        desc_match = re.search(r'\s*#(.*)', line)
        desc = desc_match.group(1).strip() if desc_match else ""
        
        node = Node(path=path, desc=desc, node_type="file" if match_res.is_file else "directory", level=current_level)
        
        # 如果当前没有根节点，将第一个节点作为根节点
        if root is None:
            root = node
            current_node = root
            continue
        
        # 建立父子关系
        if current_level > current_node.level:  # 下一级
            current_node.add_child(node)
            current_node = node
        elif current_level == current_node.level:  # 同级
            current_node = current_node.parent
            current_node.add_child(node)
            current_node = node
        else:  # 上一级
            while current_node.level > current_level:
                current_node = current_node.parent
            current_node.parent.add_child(node)
            current_node = node

    return root

def print_directory_structure(node: Node, indent: str = ''):
    """
    递归打印可视化目录结构。

    参数：
    - node：目录结构中的节点对象。
    - indent：缩进字符串，用于表示层级。
    """
    if node.type == 'directory':
        logging.info(f"{indent}{node.path}/ #{node.desc}")
        for child in node.children:
            print_directory_structure(child, indent + '  ')
    else:
        logging.info(f"{indent}{node.path} #{node.desc}")

def create_structure(item: Node, current_path: str, is_replace_file=False):
    """
    递归创建目录和文件结构。

    参数：
    - item：目录结构中的节点对象。
    - current_path：当前路径。
    """
    for child in item.children:
        child_path = os.path.join(current_path, child.path)
        try:
            if child.type == "directory":
                os.makedirs(child_path, exist_ok=True)
                if child.desc:
                    with open(os.path.join(child_path, 'README.txt'), 'w', encoding='utf-8') as f:
                        f.write(child.desc)
                create_structure(child, child_path)
            elif child.type == "file":
                if not os.path.exists(child_path) or is_replace_file:
                    with open(child_path, 'w', encoding='utf-8') as f:
                        if child.desc:
                            f.write(f"# {child.desc}\n")
                        f.write("")
        except OSError as e:
            logging.error(f"Error creating {child.type} at {child_path}: ", exc_info=True)

def create_dir_structure(directory_structure_text: str, project_dir: str, is_replace_file=False) -> None:
    """
    根据目录结构文本创建目录结构。

    参数：
    - directory_structure_text：包含目录结构描述的文本。
    - project_dir: 目标创建路径
    """
    if not isinstance(directory_structure_text, str) or not isinstance(project_dir, str):
        raise ValueError("Both directory_structure_text and project_dir should be strings.")

    parsed_structure = parse_directory_structure(directory_structure_text)
    build_directory_structure(parsed_structure, project_dir, is_replace_file)
    logging.info(f"Directory structure created at: {project_dir}")
    print_directory_structure(parsed_structure)

def build_directory_structure(directory_structure: Node, target_path: str, is_replace_file) -> None:
    """
    构建目录结构。

    参数：
    - directory_structure：表示目录结构的根节点。
    - target_path：目标路径。
    """
    os.makedirs(target_path, exist_ok=True)
    create_structure(directory_structure, target_path, is_replace_file)

def main():
    directory_structure_text = """
    project_root/ # 项目根目录
    │
    ├── main.py # 主程序文件，包含Gradio界面的构建和各功能模块的集成调用
    │
    ├── config/ # 配置模块文件夹，存放基础配置的相关代码
    │   ├── repo_config.py # 基础配置脚本，包含仓库路径配置、创建符号链接等相关功能
    │
    ├── git_functions/ # Git功能模块文件夹，存放与Git操作相关的代码
    │   ├── git_utils.py # Git操作工具模块，包含提交、推送、克隆、拉取等Git功能的实现
    │
    ├── file_operations/ # 文件操作模块文件夹，存放与文件管理相关的代码
    │   ├── file_utils.py # 文件操作工具模块，包含文件打开、备份、注释打印等功能
    │
    ├── assets/ # 资源文件夹，用于存放依赖文件、需求说明及其他资源
    │   ├── 需求说明.txt # 项目需求说明文件，描述项目需求和功能
    │   ├── DownloadList.py # 示例Python脚本文件，可用于测试和展示文件操作功能
    │   ├── Scraper.py # 示例Python脚本文件，演示抓取相关代码
    │   ├── AScript_spider.py # 示例Python脚本文件，展示特定功能模块代码
    │   ├── requirements.txt # 依赖文件，列出项目所需的外部Python库
    │
    └── utils/ # 通用工具模块文件夹（可选），用于存放其他辅助工具函数
    """
    project_dir = "/content/test"
    create_dir_structure(directory_structure_text, project_dir=project_dir)

if __name__ == "__main__":
    main()
