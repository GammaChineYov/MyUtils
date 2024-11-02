# /content/utils/py_parser.py

import os  # 用于遍历文件目录
import ast  # 用于解析Python代码结构
from collections import defaultdict, deque  # 用于构建依赖关系和进行拓扑排序

def list_python_files_and_contents(directory_path):
    """
    列出指定目录中的所有Python文件，生成文件依赖顺序，并解析文件中所有类、方法声明、类公开字段、
    全局变量及其注释，支持三个"的块注释。

    :param directory_path: 目录路径，如 /content/utils
    :return: 包含文件名、脚本说明、类声明、公开字段及其注释、方法声明及其注释的列表
    """
    # 1. 生成文件依赖图
    dependencies = generate_dependency_graph(directory_path)

    # 2. 通过拓扑排序获取依赖顺序
    sorted_files = topological_sort(dependencies)

    # 3. 按依赖顺序解析文件
    result = []
    for file_path in sorted_files:
        result.append(parse_python_file(file_path))

    return result



def parse_python_file(file_path):
    """
    解析Python文件中的类、方法声明、类公开字段及其注释，支持三个"的块注释，全局变量注释，脚本说明。

    :param file_path: 文件路径
    :return: 文件名，脚本说明，类，公开字段，方法及注释信息
    """
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    # 解析Python文件
    tree = ast.parse(file_content)
    file_lines = file_content.splitlines()  # 将文件按行分割，便于逐行处理注释

    file_info = {
        "file_name": os.path.basename(file_path),
        "script_docstring": ast.get_docstring(tree),  # 脚本的顶层文档字符串
        "global_vars": [],
        "classes": [],
        "functions": []
    }

    # 遍历语法树，查找类、函数定义及全局变量
    for node in ast.walk(tree):
        # 2. 提取类声明及其注释
        if isinstance(node, ast.ClassDef):
            class_info = {
                "class_name": node.name,
                "docstring": ast.get_docstring(node),  # 类的注释
                "fields": [],
                "methods": []
            }

            # 3. 提取类中的公开字段及其注释
            for class_body in node.body:
                if isinstance(class_body, ast.Assign):  # 检测字段
                    for target in class_body.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            field_info = {
                                "field_name": target.id,
                                "docstring": get_field_docstring(class_body, file_lines)
                            }
                            class_info["fields"].append(field_info)

                # 4. 提取类中的方法声明及其注释
                if isinstance(class_body, ast.FunctionDef):
                    method_info = {
                        "method_name": class_body.name,
                        "docstring": ast.get_docstring(class_body)  # 方法的注释
                    }
                    class_info["methods"].append(method_info)

            file_info["classes"].append(class_info)

        # 5. 提取顶级函数声明及其注释
        elif isinstance(node, ast.FunctionDef):
            function_info = {
                "function_name": node.name,
                "docstring": ast.get_docstring(node)  # 函数的注释
            }
            file_info["functions"].append(function_info)

        # 6. 提取全局变量及其注释
        elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            global_var_info = {
                "global_var_name": node.targets[0].id,
                "docstring": get_field_docstring(node, file_lines)
            }
            file_info["global_vars"].append(global_var_info)

    return file_info

def get_field_docstring(assign_node, file_lines):
    """
    获取类的字段或全局变量注释。支持三个"的块注释，行尾注释，及前几行的多行注释。

    :param assign_node: ast.Assign 节点，表示字段的赋值或全局变量
    :param file_lines: 文件的行内容列表
    :return: 字段或全局变量的注释字符串（如果存在）
    """
    line_num = assign_node.lineno - 1  # AST中的行号从1开始，文件列表行号从0开始

    # 1. 尝试获取字段所在行后的注释
    line = file_lines[line_num].strip()
    if "#" in line:  # 检查是否有行尾注释
        comment_index = line.index("#")
        return line[comment_index:].strip("#").strip()  # 提取并去除#

    # 2. 尝试获取字段声明前的"""块注释或多行注释
    comments = []
    is_block_comment = False
    for i in range(line_num - 1, -1, -1):  # 从当前行往上查找
        prev_line = file_lines[i].strip()
        if prev_line.startswith('"""') or prev_line.startswith("'''"):  # 检查块注释
            if not is_block_comment:
                is_block_comment = True
                comments.append(prev_line.strip('"""').strip("'''").strip())
            else:
                comments.append(prev_line.strip('"""').strip("'''").strip())
                break  # 完成块注释的解析，停止查找
        elif prev_line.startswith("#"):  # 找到行注释
            comments.append(prev_line.strip("#").strip())
        elif prev_line == "" or prev_line.startswith("class") or prev_line.startswith("def"):
            # 遇到空行、类定义或函数定义时，停止查找
            break

    if comments:
        return "\n".join(reversed(comments))  # 合并多行注释，保留换行

    return None  # 未找到注释

import os
import ast
from collections import defaultdict, deque
import traceback  # 用于打印错误堆栈
def process_files_with_callback(directory_path, callback):
    """
    列出指定目录中的所有Python文件，并生成文件依赖顺序，逐个文件传递给回调函数。

    :param directory_path: 目录路径
    :param callback: 回调函数，接受文件路径作为参数
    """
    try:
        # 1. 检查目录是否存在
        if not os.path.isdir(directory_path):
            raise ValueError(f"指定的目录路径不存在: {directory_path}")

        print(f"开始处理目录 '{directory_path}' 的文件依赖图...")
        
        # 2. 生成文件依赖图
        dependencies = generate_dependency_graph(directory_path)

        # 3. 打印依赖拓扑图
        print_dependency_graph(dependencies)

        # 4. 通过拓扑排序获取依赖顺序
        sorted_files = topological_sort(dependencies)

        # 5. 按依赖顺序遍历文件，并将文件路径传递给回调函数
        for file_path in sorted_files:
            print(f"正在处理文件: {file_path}")
            try:
                # 将文件路径传递给回调函数
                callback(file_path)
            except Exception as cb_error:
                print(f"回调函数处理文件 '{file_path}' 时发生错误: {cb_error}")
                traceback.print_exc()

    except Exception as e:
        print(f"处理目录时发生错误: {e}")
        traceback.print_exc()



def generate_dependency_graph(directory_path):
    """
    生成指定目录中Python文件的依赖关系图。

    :param directory_path: 目录路径
    :return: 文件依赖关系图，字典形式 {文件路径: [依赖文件路径]}
    """
    dependencies = defaultdict(list)
    py_files = []

    try:
        # 遍历所有Python文件，构建依赖关系
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    py_files.append(file_path)
                    print(f"正在解析文件: {file_path}")

                    imported_files = get_imported_modules(file_path, directory_path)
                    if imported_files is None:
                        print(f"警告: 无法解析依赖项，跳过文件 {file_path}")
                        continue

                    for imported_file in imported_files:
                        dependencies[file_path].append(imported_file)
                        print(f"  -> 发现依赖: {imported_file}")

        return dependencies

    except Exception as e:
        print(f"生成依赖图时发生错误: {e}")
        traceback.print_exc()
        return {}

def get_imported_modules(file_path, directory_path):
    """
    解析Python文件中的import语句，获取项目内部的模块依赖。

    :param file_path: 当前文件路径
    :param directory_path: 项目根目录路径
    :return: 被导入的项目内模块文件路径列表，解析失败时返回None
    """
    imported_files = []

    try:
        if not os.path.exists(file_path):
            raise ValueError(f"文件路径不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        # 解析Python文件
        tree = ast.parse(file_content)

        # 查找import和from ... import语句
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_path = resolve_module_path(alias.name, directory_path)
                    if module_path:
                        imported_files.append(module_path)
                    else:
                        # print(f"警告: 无法解析模块 {alias.name}，在 {file_path}")
                        pass

            elif isinstance(node, ast.ImportFrom):
                module_path = resolve_module_path(node.module, directory_path)
                if module_path:
                    imported_files.append(module_path)
                else:
                    # print(f"警告: 无法解析模块 {node.module}，在 {file_path}")
                    pass

        return imported_files

    except Exception as e:
        print(f"解析文件依赖时发生错误: {e} (文件: {file_path})")
        traceback.print_exc()
        return None

def resolve_module_path(module_name, directory_path):
    """
    根据模块名称解析项目内模块的文件路径。

    :param module_name: 模块名称（如 utils.parser）
    :param directory_path: 项目根目录路径
    :return: 对应的文件路径，如果模块在项目内存在，返回其文件路径；否则返回None
    """
    try:
        # 将模块名转换为文件路径
        module_path = os.path.join(directory_path, module_name.replace(".", "/") + ".py")
        if os.path.exists(module_path):
            return module_path
        else:
            # print(f"警告: 模块路径不存在 {module_path} (模块: {module_name})")
            return None
    except Exception as e:
        # print(f"解析模块路径时发生错误: {e} (模块: {module_name})")
        traceback.print_exc()
        return None

def topological_sort(dependencies):
    """
    根据文件依赖关系进行拓扑排序，返回按依赖顺序排序的文件列表。

    :param dependencies: 文件依赖关系图，字典形式 {文件路径: [依赖文件路径]}
    :return: 拓扑排序后的文件路径列表
    """
    try:
        indegree = {file: 0 for file in dependencies}  # 记录每个文件的入度
        for file, deps in dependencies.items():
            for dep in deps:
                if(dep not in indegree):
                    indegree[dep] = 0
                indegree[dep] += 1

        # 使用队列记录入度为0的文件
        queue = deque([file for file, deg in indegree.items() if deg == 0])
        sorted_files = []

        while queue:
            current_file = queue.popleft()
            sorted_files.append(current_file)

            for dep in dependencies[current_file]:
                indegree[dep] -= 1
                if indegree[dep] == 0:
                    queue.append(dep)

        return sorted_files

    except Exception as e:
        print(f"拓扑排序时发生错误: {e}")
        traceback.print_exc()
        return []

def print_dependency_graph(dependencies):
    """
    打印文件依赖拓扑图，显示每个文件的依赖项。

    :param dependencies: 文件依赖关系图，字典形式 {文件路径: [依赖文件路径]}
    """
    try:
        print("\n文件依赖拓扑图:")
        for file, deps in dependencies.items():
            print(f"{file} 依赖 -> {', '.join(deps) if deps else '无'}")
    except Exception as e:
        print(f"打印依赖拓扑图时发生错误: {e}")
        traceback.print_exc()



def depth_first_traverse_directory(directory_path, callback, exclude_dirs=None):
    """
    深度优先遍历指定目录，将目录路径传递给回调函数，并支持排除指定的目录。
    
    遍历顺序为从最深层的子目录开始，逐步返回并处理上层目录，直到最顶层目录。
    
    :param directory_path: 要遍历的根目录路径
    :param callback: 处理每个目录的回调函数，接受目录路径作为参数
    :param exclude_dirs: 排除的目录列表，默认为 ['.git', '.github', '.ci']
    """
    try:
        # 设置默认的排除目录列表
        if exclude_dirs is None:
            exclude_dirs = ['.git', '.github', '.ci']

        # 递归深度优先遍历
        def traverse(dir_path):
            # 遍历子目录
            try:
                with os.scandir(dir_path) as it:
                    subdirs = []
                    for entry in it:
                        # 如果是目录并且不在排除列表中，递归遍历子目录
                        if entry.is_dir() and entry.name not in exclude_dirs:
                            subdirs.append(entry.path)
                    
                    # 先递归处理子目录
                    for subdir in subdirs:
                        traverse(subdir)

                # 子目录处理完成后，再处理当前目录
                callback(dir_path)
            except Exception as e:
                print(f"处理目录 {dir_path} 时发生错误: {e}")
                traceback.print_exc()

        # 从根目录开始遍历
        traverse(directory_path)

    except Exception as e:
        print(f"深度优先遍历目录时发生错误: {e}")
        traceback.print_exc()

# 示例回调函数
def example_directory_callback(dir_path):
    """
    示例回调函数，处理传递进来的目录路径。
    
    :param dir_path: 目录路径
    """
    print(f"回调函数处理目录: {dir_path}")

# 封装的深度优先遍历示例
def run_depth_first_traverse_example(directory_path):
    """
    运行深度优先遍历目录的示例，使用默认的排除目录。
    """
    print("\n=== 运行深度优先遍历目录示例 ===")
    # 默认排除 '.git', '.github', '.ci' 等目录
    depth_first_traverse_directory(directory_path, example_directory_callback)

def run_depth_first_traverse_with_custom_excludes(directory_path, custom_excludes):
    """
    运行深度优先遍历目录的示例，使用自定义的排除目录。
    
    :param directory_path: 根目录路径
    :param custom_excludes: 自定义排除的目录列表
    """
    print("\n=== 运行自定义排除目录的深度优先遍历目录示例 ===")
    depth_first_traverse_directory(directory_path, example_directory_callback, exclude_dirs=custom_excludes)



# 示例回调函数
def example_callback(file_path):
    """
    一个示例回调函数，打印传递进来的文件路径。

    :param file_path: 文件路径
    """
    print(f"回调函数处理文件: {file_path}")

# 封装的示例函数
def run_list_files_example(directory_path):
    """
    运行 list_python_files_and_contents 示例。
    """
    print("\n=== 运行 list_python_files_and_contents 示例 ===")
    python_files_info = list_python_files_and_contents(directory_path)
    for file_info in python_files_info:
        print(f"文件名: {file_info['file_name']}")
        print(f"  脚本说明: {file_info['script_docstring']}")
        for global_var_info in file_info["global_vars"]:
            print(f"  全局变量: {global_var_info['global_var_name']}, 注释: {global_var_info['docstring']}")
        for class_info in file_info["classes"]:
            print(f"  类: {class_info['class_name']}, 注释: {class_info['docstring']}")
            for field_info in class_info["fields"]:
                print(f"    字段: {field_info['field_name']}, 注释: {field_info['docstring']}")
            for method_info in class_info["methods"]:
                print(f"    方法: {method_info['method_name']}, 注释: {method_info['docstring']}")
        for function_info in file_info["functions"]:
            print(f"  函数: {function_info['function_name']}, 注释: {function_info['docstring']}")

def run_callback_example(directory_path):
    """
    运行 process_files_with_callback 示例。
    """
    print("\n=== 运行 process_files_with_callback 示例 ===")
    process_files_with_callback(directory_path, example_callback)

def run_dependency_graph_example(directory_path):
    """
    运行生成并打印依赖图的示例。
    """
    print("\n=== 运行生成并打印依赖图的示例 ===")
    dependencies = generate_dependency_graph(directory_path)
    print_dependency_graph(dependencies)



if __name__ == "__main__":
    directory_path = "/content/utils"  # 指定目录路径
    
    # 运行list_python_files_and_contents示例
    # run_list_files_example(directory_path)
    
    # 运行process_files_with_callback示例
    # run_callback_example(directory_path)
    
    # 运行依赖图生成和打印示例
    # run_dependency_graph_example(directory_path)

    # 运行深度优先遍历目录示例
    # run_depth_first_traverse_example(directory_path)

    # 运行自定义排除目录的示例
    # custom_excludes = []#['.git', '.env']  # 自定义排除的目录
    # run_depth_first_traverse_with_custom_excludes(directory_path, custom_excludes)

