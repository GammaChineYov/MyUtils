import os
import re
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

def get_file_types():
    """
    返回支持的文件类型及其注释格式和匹配正则表达式。
    """
    return {
        '.py': {
            'comment_format': "# {}\n",
            'regex': r'^\s*#\s*/?(.+)\s*$'
        },
        '.js': {
            'comment_format': "// {}\n",
            'regex': r'^\s*//\s*/?(.+)\s*$'
        },
        '.ts': {  # TypeScript
            'comment_format': "// {}\n",
            'regex': r'^\s*//\s*/?(.+)\s*$'
        },
        '.jsx': {  # JavaScript XML
            'comment_format': "// {}\n",
            'regex': r'^\s*//\s*/?(.+)\s*$'
        },
        '.tsx': {  # TypeScript XML
            'comment_format': "// {}\n",
            'regex': r'^\s*//\s*/?(.+)\s*$'
        },
        '.css': {
            'comment_format': "/* {} */\n",
            'regex': r'^\s*/\*\s*/?(.+)\s*\*/\s*$'
        },
        '.scss': {  # SASS
            'comment_format': "/* {} */\n",
            'regex': r'^\s*/\*\s*/?(.+)\s*\*/\s*$'
        },
        '.md': {
            'comment_format': "<!-- {} -->\n",
            'regex': r'^\s*<!--\s*/?(.+)\s*-->\s*$'
        },
        '.html': {
            'comment_format': "<!-- {} -->\n",
            'regex': r'^\s*<!--\s*/?(.+)\s*-->\s*$'
        },
        '.xml': {
            'comment_format': "<!-- {} -->\n",
            'regex': r'^\s*<!--\s*/?(.+)\s*-->\s*$'
        },
        '.go': {  # Go
            'comment_format': "// {}\n",
            'regex': r'^\s*//\s*/?(.+)\s*$'
        },
        '.sh': {  # Shell脚本
            'comment_format': "# {}\n",
            'regex': r'^\s*#\s*/?(.+)\s*$'
        },
        # 可以在此处添加更多文件类型
    }

def parse_arguments():
    """
    解析命令行参数。
    """
    parser = argparse.ArgumentParser(description="为指定目录下的文件添加路径注释。")
    parser.add_argument(
        'directory',
        type=str,
        help='要遍历的工程目录路径'
    )
    parser.add_argument(
        '--threads',
        type=int,
        default=4,
        help='使用的线程数（默认为4）'
    )
    return parser.parse_args()

def add_file_path_comment(directory, max_workers=4):
    """
    遍历指定目录，给每种文件类型首行添加文件路径注释。

    :param directory: 要遍历的目录路径
    :param max_workers: 线程池中使用的最大线程数
    """
    file_types = get_file_types()
    supported_extensions = file_types.keys()

    base_path = Path(directory).resolve()
    print(f"项目根目录（绝对路径）：{base_path}\n")

    # 收集待处理的文件
    files_to_process = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            ext = Path(file).suffix
            if ext in supported_extensions:
                file_path = Path(root) / file
                try:
                    relative_path = file_path.relative_to(base_path)
                    # 确保路径以 '/' 开头，并使用正斜杠
                    relative_path_str = '/' + str(relative_path).replace(os.sep, '/')
                except ValueError:
                    # 在极少数情况下，无法计算相对路径时，使用绝对路径并加 '/'
                    relative_path_str = '/' + str(file_path.resolve()).replace(os.sep, '/')
                files_to_process.append((file_path, file_types[ext], relative_path_str))
                print(f"准备处理文件：{file_path}，相对路径：{relative_path_str}")

    print(f"\n共找到 {len(files_to_process)} 个需要处理的文件。\n")

    # 使用线程池处理文件
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(add_comment_to_file, file_path, comment_info, relative_path): file_path
            for file_path, comment_info, relative_path in files_to_process
        }

        for future in as_completed(futures):
            file_path = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"处理文件时出错: {file_path}，错误: {e}")

def add_comment_to_file(file_path, comment_info, relative_path):
    """
    为指定文件添加或替换路径注释。

    :param file_path: 文件的完整路径 (Path 对象)
    :param comment_info: 包含注释格式和匹配正则的字典
    :param relative_path: 文件相对于工程目录的相对路径，前面带 "/"
    """
    comment_format = comment_info['comment_format']
    regex = comment_info['regex']
    path_comment = comment_format.format(relative_path)
    print(f"\n正在处理文件：{file_path}")
    print(f"生成的注释内容：{path_comment.strip()}")

    try:
        with file_path.open('r', encoding='utf-8') as f:
            lines = f.readlines()

        if lines:
            first_line = lines[0]
            match = re.match(regex, first_line)
            if match:
                existing_path = match.group(1).strip()
                # 确保 existing_path 以 '/' 开头
                if not existing_path.startswith('/'):
                    existing_path = '/' + existing_path
                print(f"检测到现有注释路径：'{existing_path}'")
                if existing_path == relative_path:
                    print("注释路径正确，无需修改。")
                    return
                else:
                    # 替换不正确的路径注释
                    lines[0] = path_comment
                    print("注释路径不正确，已替换为正确的相对路径。")
            else:
                # 添加新的路径注释
                lines.insert(0, path_comment)
                print("未检测到注释，已添加新的路径注释。")
        else:
            # 文件为空，直接写入注释
            lines = [path_comment]
            print("文件为空，已添加文件路径注释。")

        # 写回文件
        with file_path.open('w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"成功更新文件：{file_path}")

    except Exception as e:
        print(f"处理文件时出错: {file_path}，错误: {e}")

if __name__ == "__main__":
    args = parse_arguments()
    target_directory = args.directory

    if not Path(target_directory).is_dir():
        print(f"指定的目录不存在或不是一个目录: {target_directory}")
        exit(1)

    print(f"开始为目录 '{target_directory}' 下的文件添加路径注释。\n")
    add_file_path_comment(target_directory, max_workers=args.threads)
    print("\n所有文件处理完毕。")
