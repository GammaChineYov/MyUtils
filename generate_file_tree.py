import os
import json

def generate_file_tree(directory, flatten=False, relative=False):
    """
    生成指定目录的文件树，格式为 JSON。
    
    :param directory: 需要生成文件树的目录路径
    :param flatten: 是否将文件树展开为一维列表，默认值为 False
    :param relative: 是否将路径裁切为相对输入目录的路径，默认值为 False
    :return: 文件树的 JSON 结构或一维列表
    """
    
    # 定义需要排除的目录
    exclude_dirs = {'__pycache__', '.git', '.svn', '.hg', 'node_modules'}

    def build_tree(dir_path):
        tree = {'name': os.path.basename(dir_path), 'children': []}
        try:
            entries = os.listdir(dir_path)
        except PermissionError:
            return tree  # 无权限访问，返回空树
        
        for entry in entries:
            entry_path = os.path.join(dir_path, entry)
            if os.path.isdir(entry_path):
                if entry not in exclude_dirs:  # 只添加未排除的目录
                    tree['children'].append(build_tree(entry_path))  # 递归构建子目录
            else:
                tree['children'].append({'name': entry})  # 添加文件
        return tree
    
    file_tree = build_tree(directory)

    if flatten:
        # 如果需要展开为一维列表，递归提取文件名
        def extract_files(node, base_path):
            files = []
            if 'children' in node:
                for child in node['children']:
                    if 'children' in child:
                        child_files = extract_files(child, os.path.join(base_path, child['name']))
                        # child_files = [os.path.join(node["name"], f) for f in child_files]
                        files.extend(child_files)
                    else:
                        # 根据 relative 参数决定路径
                        if relative:
                            files.append(os.path.relpath(os.path.join(base_path, child['name']), directory))
                        else:
                            files.append(os.path.join(base_path, child['name']))
            return files
        
        return extract_files(file_tree, directory)  # 传递基础路径
    
    # 根据 relative 参数处理路径
    if relative:
        def make_relative_tree(node):
            node['name'] = os.path.relpath(node['name'], directory)
            for child in node.get('children', []):
                make_relative_tree(child)
        make_relative_tree(file_tree)

    return json.dumps(file_tree, indent=4, ensure_ascii=False)  # 返回格式化的 JSON

# 使用示例
if __name__ == '__main__':
    directory_path = './'  # 替换为你的目录路径
    directory_path = os.path.abspath(directory_path)
    print(generate_file_tree(directory_path, flatten=False, relative=False))  # 以 JSON 结构输出
    print(generate_file_tree(directory_path, flatten=True, relative=True))   # 以一维列表输出，路径相对
