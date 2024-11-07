from git import Repo, GitCommandError
import os
import re
import subprocess
import sys


"""
简介：
该脚本使用 GitPython 库自动化将本地项目上传到多种 Git 仓库平台（如 GitHub 和 Gitee）。它能够初始化 Git 仓库，添加远程仓库，提交更改，并处理推送过程中可能出现的冲突。

使用方法：
- 通过命令行参数传入本地项目路径和远程仓库地址。
- 确保已安装 GitPython 库。
- 运行该脚本自动管理和推送本地 Git 仓库。
"""

# 检查命令行参数是否正确
if len(sys.argv)!= 3:
    print("Usage: python script.py <local_repo_path> <remote_repo_url>")
    exit(1)

# 获取本地项目路径和远程仓库地址
local_repo_path = sys.argv[1]
remote_repo_url = sys.argv[2]

# 检查 Git 是否安装
def check_git_installed():
    try:
        subprocess.run(['git', '--version'], check=True)
        print("Git 已安装，版本为:", subprocess.check_output(['git', '--version']).decode().strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Git 未安装或未在系统路径中，请先安装 Git.")
        exit(1)

# 检查远程仓库 URL 格式（支持 HTTPS 和 SSH）
def is_valid_git_url(url):
    return bool(re.match(r'^(https:\/\/[^\/]+\/[^\/]+\/[^\/]+\.git|git@[^:]+:[^\/]+\/[^\/]+\.git)$', url))

# 检查本地项目是否存在
if not os.path.exists(local_repo_path):
    print(f"路径 {local_repo_path} 不存在，请检查.")
    exit(1)

# 检查仓库 URL 的有效性
if not is_valid_git_url(remote_repo_url):
    print(f"远程仓库 URL '{remote_repo_url}' 格式不正确，请检查.")
    exit(1)

# 检查 Git 是否安装
check_git_installed()

try:
    # 尝试获取现有仓库
    repo = Repo(local_repo_path)
    print("找到现有的 Git 仓库.")
except Exception as e:
    # 如果仓库不存在，则初始化一个新的 Git 仓库
    print("未找到 Git 仓库，正在初始化...")
    repo = Repo.init(local_repo_path)

# 检查是否已经添加远程仓库
remote_names = [remote.name for remote in repo.remotes]
if 'origin' not in remote_names:
    # 添加远程仓库
    origin = repo.create_remote('origin', remote_repo_url)
    print(f"添加远程仓库: {remote_repo_url}")
else:
    print("远程仓库已存在.")

# 检查用户信息
try:
    user_name = repo.git.config('--global', 'user.name')
    user_email = repo.git.config('--global', 'user.email')
except GitCommandError:
    user_name = None
    user_email = None

if not user_name or not user_email:
    # 提取仓库名称并设置邮箱
    match = re.search(r'git@.+?:(.+?)/', remote_repo_url)
    if match:
        repo_name = match.group(1)  # 提取仓库名
        user_name = repo_name  # 使用仓库名作为用户名
        user_email = f"{repo_name}@139.com"  # 设置邮箱
        repo.git.config('--global', 'user.name', user_name)
        repo.git.config('--global', 'user.email', user_email)
        print(f"设置用户信息: 姓名={user_name}, 邮箱={user_email}")

# 添加文件到暂存区
repo.git.add(A=True)

# 检查是否有未提交的更改
if repo.is_dirty(untracked_files=True):
    commit_message = "提交更改"
    repo.index.commit(commit_message)
    print("更改已提交.")
    # 显示本次提交的文件名录
    committed_files = [item.a_path for item in repo.index.diff("HEAD", create_patch=True)]
    print("本次上传的文件名录:")
    for file in committed_files:
        print(f"- {file}")
else:
    print("没有未提交的更改.")

# 检查当前分支状态
if not repo.active_branch or not repo.active_branch.is_valid():
    print("当前分支无效，无法推送.")
    exit(1)

# 推送到远程仓库
try:
    print("开始推送到远程仓库...")
    repo.git.push('origin', 'main', set_upstream=True)
    print("项目已成功推送到远程仓库.")
except GitCommandError as e:
    print(f"推送失败: {e}. 尝试解决远程仓库的冲突.")
    # 处理由于推送被拒绝而导致的非快进错误
    if 'non-fast-forward' in str(e) or 'behind' in str(e):
        print("检测到当前分支落后于远程分支，正在拉取远程更改...")
        try:
            repo.git.pull('origin', 'main', '--allow-unrelated-histories', '--no-rebase')
            print("成功拉取远程更改。")
            # 再次推送
            repo.git.push('origin', 'main', set_upstream=True)
            print("项目已成功推送到远程仓库（更新后的远程更改已合并）.")
        except GitCommandError as e:
            print(f"拉取失败: {e}. 请手动解决冲突.")
