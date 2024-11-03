import os
import ast

def print_file_comments(file_path):
    """
    打印文件名、文档注释、类声明及其注释、函数声明及其注释和全局变量及其注释。

    参数:
    - file_path (str): Python 文件的路径。
    """
    if not os.path.isfile(file_path):
        print(f"错误: 文件 '{file_path}' 不存在。")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # 解析 AST
    tree = ast.parse(file_content)

    # 打印文件名
    print(f"文件名: {os.path.basename(file_path)}")

    # 打印模块的文档注释
    docstring = ast.get_docstring(tree)
    if docstring:
        print("文档注释: " + docstring.replace('\n', '\\n'))
    else:
        print("文档注释: 无")

    # 遍历 AST 节点
    for node in ast.walk(tree):
        # 打印类声明及其文档字符串
        if isinstance(node, ast.ClassDef):
            class_comment = ""
            if ast.get_docstring(node):
                class_comment = ast.get_docstring(node).replace('\n', '\\n')

            # 打印类名称和注释
            print(f"class {node.name}: #{class_comment.strip()}")

            # 打印类内部函数
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    func_comment = ""
                    if ast.get_docstring(item):
                        func_comment = ast.get_docstring(item).replace('\n', '\\n')

                    # 打印函数名称和注释
                    print(f"  def {item.name}(self): #{func_comment.strip()}")

        # 打印全局变量声明及其注释
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_comment = ""
                    # 获取行号并尝试获取注释
                    line_number = target.lineno
                    line = file_content.splitlines()[line_number - 1]
                    if '#' in line:
                        var_comment = line.split('#', 1)[1].strip().replace('\n', '\\n')

                    # 确保只打印赋值，而不是函数调用
                    if isinstance(node.value, (ast.Constant, ast.Str, ast.Num, ast.Name)):
                        value_repr = ast.dump(node.value, annotate_fields=False)
                        print(f"{target.id} = {value_repr} #{var_comment.strip()}")

if __name__ == "__main__":
  # 使用示例
  file_path = "/path/to/your/DownloadList.py"  # 替换为你的文件路径
  print_file_comments(file_path)
