import re


# 预编译正则表达式
pattern = re.compile(r'(\./|/?(\w+/)*\w+\.\w+)')


def extract_file_paths(comment: str, single: bool = False):
    """
    从给定的注释字符串中提取文件路径。

    参数：
    - comment (str): 要从中提取文件路径的注释字符串。
    - single (bool, 可选): 如果为 True，只返回第一个匹配的文件路径；如果为 False，返回所有匹配的文件路径列表。默认值为 False。

    返回：
    - list[str] 或 str: 如果 single 为 False，返回文件路径列表；如果 single 为 True，返回列表里只有单个文件路径字符串，如果没有找到匹配则返回空列表。

    使用方法：
    paths = extract_file_paths(your_comment_string, single=True)

    """
    comment = comment.replace("\\", "/")
    if single:
        # 使用 search 只查找第一个匹配
        match = pattern.search(comment)
        return [match.group(0)] if match else []
    else:
        # 使用 findall 提取所有路径
        return [b[0] for b in pattern.findall(comment)]


def find_longest_path(*comments):
    """
    传入多个注释字符串，提取文件路径后比较，返回其中字数最多的路径。

    参数：
    - *comments: 多个注释字符串。

    返回：
    - str: 字数最多的注释字符串。如果所有注释字符串提取后都为空，则返回 None。
    """
    longest_comment = ""
    max_length = 0
    for comment in comments:
        path = extract_file_paths(comment,single=True)[0]
        path_length = len(path)
        if path_length > max_length:
            max_length = path_length
            longest_path = path
    return longest_comment


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
    print(longest)

