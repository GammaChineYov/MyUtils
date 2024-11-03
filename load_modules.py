import importlib
import logging
import os
import pkg_resources
import socket
import subprocess
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("module_loader.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


def is_internet_available():
    """检查网络连接是否可用。"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def load_module(module_name, package_name=None, min_version=None):
    """
    动态加载模块。如果模块未安装，则通过 pip 安装指定的包名。

    :param module_name: 要加载的模块名（用于导入）
    :param package_name: 如果与模块名不同，用于 pip 安装的包名
    :param min_version: 模块的最小版本要求（字符串），如 '1.0.0'
    :return: 导入的模块
    """
    if package_name is None:
        package_name = module_name

    # 检查 Python 版本
    required_python = (3, 6)
    if sys.version_info < required_python:
        logging.error(f"当前 Python 版本为 {sys.version_info.major}.{sys.version_info.minor}，但需要至少 {required_python[0]}.{required_python[1]}。")
        raise EnvironmentError(f"Python 版本过低，需要至少 {required_python[0]}.{required_python[1]}。")

    try:
        pkg = pkg_resources.get_distribution(package_name)
        logging.info(f"发现已安装的包 '{package_name}' 版本为 {pkg.version}。")
        if min_version and pkg_resources.parse_version(pkg.version) < pkg_resources.parse_version(min_version):
            logging.warning(f"包 '{package_name}' 的版本 {pkg.version} 小于要求的最低版本 {min_version}。尝试升级。")
            if not is_internet_available():
                logging.error("网络连接不可用，无法升级包。")
                raise ConnectionError("网络连接不可用，无法升级包。")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
    except pkg_resources.DistributionNotFound:
        logging.info(f"包 '{package_name}' 未安装。")

    try:
        module = importlib.import_module(module_name)
        logging.info(f"模块 '{module_name}' 已成功加载。")
    except ImportError:
        logging.info(f"模块 '{module_name}' 未安装，准备安装包 '{package_name}'。")
        if not is_internet_available():
            logging.error("网络连接不可用，无法安装包。")
            raise ConnectionError("网络连接不可用，无法安装包。")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            module = importlib.import_module(module_name)
            logging.info(f"模块 '{module_name}' 已成功安装并加载。")
        except subprocess.CalledProcessError as e:
            logging.error(f"安装包 '{package_name}' 失败。错误信息：{e}")
            raise
        except ImportError as e:
            logging.error(f"安装包 '{package_name}' 后导入模块 '{module_name}' 失败。错误信息：{e}")
            raise

    # 检查模块版本
    if min_version:
        try:
            installed_version = getattr(module, '__version__', None)
            if installed_version is None:
                logging.warning(f"无法获取模块 '{module_name}' 的版本信息。")
            elif pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(min_version):
                logging.error(f"模块 '{module_name}' 的版本 {installed_version} 小于要求的最低版本 {min_version}。")
                raise ImportError(f"模块 '{module_name}' 的版本 {installed_version} 小于要求的最低版本 {min_version}。")
            else:
                logging.info(f"模块 '{module_name}' 的版本 {installed_version} 满足要求。")
        except Exception as e:
            logging.warning(f"检查模块 '{module_name}' 版本时出错：{e}")

    return module


def load_modules(modules):
    """
    批量加载模块。

    :param modules: 一个包含 (module_name, package_name, min_version) 元组的列表
    :return: 一个包含已加载模块的字典
    """
    loaded_modules = {}
    for module_info in modules:
        module_name = None
        package_name = None
        min_version = None
        if len(module_info) == 3:
            module_name, package_name, min_version = module_info
        elif len(module_info) == 2:
            module_name, package_name = module_info
        elif len(module_info) == 1:
            module_name = module_info[0]

        try:
            loaded_modules[module_name] = load_module(module_name, package_name, min_version)
        except Exception as e:
            logging.error(f"加载模块 '{module_name}' 失败：{e}")
    return loaded_modules


if __name__ == "__main__":
    # 使用示例：加载 GitPython 模块，并要求至少版本 '3.1.0'
    try:
        git = load_module('git', 'gitpython', min_version='3.1.0')
        print(f"GitPython 版本：{git.__version__}")
    except Exception as e:
        logging.error(f"无法加载模块：{e}")

    # 进一步扩展：批量加载多个模块
    modules_to_load = [
        ('git', 'gitpython', '3.1.0'),
        ('requests', 'requests', '2.25.0'),
        ('numpy', 'numpy')  # 无最低版本要求
        # 添加更多需要加载的模块
    ]

    loaded = load_modules(modules_to_load)
