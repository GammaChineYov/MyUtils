"""
该文档存储了创建符号链接（软路由）的方法。
"""
import os
import platform

def create_symlink(source_path, link_path, replace_existing=False):
    """
    创建符号链接（软路由）的方法。
    
    :param source_path: 源路径，指向原始目录。
    :param link_path: 链接路径，指向要创建的符号链接。
    :param replace_existing: 是否替换已存在的链接，默认为 False。
    
    :return: None
    """
    try:
        # 检查源路径是否存在
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"源路径 {source_path} 不存在。")

        # 检查目标路径是否已存在
        if os.path.exists(link_path):
            if replace_existing:
                print(f"目标路径 {link_path} 已存在，正在替换...")
                if platform.system() == "Windows":
                    os.remove(link_path)  # 删除文件或链接
                else:
                    os.unlink(link_path)  # 删除符号链接
                print(f"已删除现有链接：{link_path}")
            else:
                print(f"警告：目标路径 {link_path} 已存在，未进行替换。")
                return

        # 创建符号链接
        if platform.system() == "Windows":
            os.system(f'mklink /D "{link_path}" "{source_path}"')
        else:
            os.symlink(source_path, link_path)

        print(f"符号链接已成功创建：{link_path} -> {source_path}")

    except Exception as e:
        print(f"创建符号链接时出错：{e}")

# 使用示例
# source = '/content/drive/MyDrive/aiUserHelper'
# link = '/content/aiUserHelper'
# # 传入 replace_existing 参数来决定是否替换
# create_symlink(source, link, replace_existing=True)  # 将替换已存在的链接
