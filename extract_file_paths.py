import re
import json

class MatchResult:
    """
    匹配结果类
    使用方法：
    1. 创建 MatchResult 对象并传入输出结果和参数。
    2. 直接打印对象将以 JSON 格式输出。
    工作流：
    1. 初始化对象
    """

    def __init__(self, output, is_file=False, is_just_filename=False, extension="", filename=""):
        self.output = output  # 原始匹配的整个路径或文件名
        self.is_file = is_file  # 是否为文件
        self.is_just_filename = is_just_filename  # 是否为单独的文件名
        self.extension = extension  # 文件扩展名
        self.filename = filename  # 仅文件名（不包含路径）

    def __str__(self):
        """以 JSON 格式返回对象字符串，包括 filename 字段"""
        return json.dumps({
            'output': self.output,
            'is_file': self.is_file,
            'is_just_filename': self.is_just_filename,
            'extension': self.extension,
            'filename': self.filename
        }, ensure_ascii=False, indent=4)  # 确保中文字符正常显示

# 匹配文件路径和文件名的正则表达式
system_file_pattern = r"""[^ \\/:*?"<>|\r\n\t]"""  # 符合文件系统的命名
rule_file_pattern = r"""[\w\-\.]"""  # 正常命名
re_pattern_format = r'((/?{0}+/)+({0}+(\.{0}+))?|(/?{0}+(\.{0}+)))'
pattern1 = re.compile(re_pattern_format.format(system_file_pattern))
pattern2 = re.compile(re_pattern_format.format(rule_file_pattern))

def extract_path(line, single=True, system_mode=False, custom_format=None):
    # 匹配规则
    # 1.不能有空格
    # 2.目录后缀必须带 /
    # 3.文件必须有后缀
    # system_mode 匹配效果极差，只确保符合文件系统命名规则
    pattern = pattern1 if system_mode else pattern2 if not custom_format else re.compile(re_pattern_format.format(custom_format))
    line = line.replace("\\", "/")  # 统一路径分隔符
    res = re.search(pattern, line) if single else pattern.findall(line)
    
    if res:
        outputs = []
        groups = [res.groups(0)] if single else res
        for group in groups:
            # 匹配结果分析：group 的结构
            result = MatchResult(group[0])
            if group[4]:  # 仅文件名
                result.is_just_filename = True
                result.is_file = True
                result.extension = group[5]
                result.filename = group[4]
            elif group[2]:  # 包含路径和文件名
                result.is_file = True
                result.extension = group[3]
                result.filename = group[2]
            outputs.append(result)
        return outputs
    else:
        return []

def extract_file_paths(comment: str, single: bool = False, system_mode=False, custom_format=None):
    """
    从给定的注释字符串中提取文件路径。

    参数：
    - comment (str): 要从中提取文件路径的注释字符串。
    - single (bool, 可选): 如果为 True，只返回第一个匹配的文件路径；如果为 False，返回所有匹配的文件路径列表。默认值为 False。

    返回：
    - list[str] 或 str: 如果 single 为 False，返回文件路径列表；如果 single 为 True，返回列表里只有单个文件路径字符串，如果没有找到匹配则返回空列表。
    """
    res = [res.output for res in extract_path(comment, single, system_mode=system_mode, custom_format=custom_format) if res.is_file]
    return res

def find_longest_path(*comments):
    """
    传入多个注释字符串，提取文件路径后比较，返回其中字数最多的路径。

    参数：
    - *comments: 多个注释字符串。

    返回：
    - str: 字数最多的文件路径。如果所有注释字符串提取后都为空，则返回 None。
    """
    longest_path = None
    max_length = 0

    for comment in comments:
        paths = extract_file_paths(comment, single=False)
        if paths:
            path = paths[-1]  # 提取第一个匹配的路径
            path_length = len(path)
            if path_length > max_length:
                max_length = path_length
                longest_path = path

    return longest_path

if __name__ == "__main__":
    # 示例注释
    comment1 = """// Another path: C:/Users/Example/file.js
    /* Path in CSS: assets/style.css */
    <!-- HTML path: /index.html -->
    # main.py
    """
    comment2 = "Some short comment"
    comment3 = "A longer comment with more words and paths /path1/file1.txt /path2/file2.txt"

    longest = find_longest_path(comment1, comment2, comment3)
    print("\n========= Longest Path in Comments =========")
    print("Longest path found:", longest)
    
    # 测试案例
    lines = [
        ("└── root/test/utils_-工具/ # 通用工具模块文件夹（可选），用于存放其他辅助工具函数", "Root Folder Path"),
        ("# main.py", "Main Python File"),
        ("# test/main.py", "Test Python File"),
        ("# /test/main.py", "Absolute Path Test File"),
        ("    gr.Button(\"恢复文件\").click(file_restore, inputs=filepath,", "UI Component with Function Call")
    ]

    for line, description in lines:
        print(f"\n========= Test Case: {description} =========")
        print("Original Line Content:", line)
        paths = extract_path(line, single=False, system_mode=True)
        for path in paths:
            print(path)
