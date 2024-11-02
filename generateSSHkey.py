import os
import subprocess
import shutil

"""
简介：
    该脚本用于在 Google Colab 环境中自动生成 SSH 密钥，并将其配置到指定目录和系统的 SSH 目录中。脚本还会自动添加 GitHub 和 Gitee 的主机密钥到 `known_hosts` 文件，确保与这些平台的安全连接。

目标：
    - 自动生成 SSH 密钥（如果尚未存在），并将其保存到 Google Drive 的指定目录。
    - 将生成的 SSH 密钥复制到系统的 `.ssh` 目录，并设置适当的权限。
    - 自动添加 GitHub 和 Gitee 的主机密钥到 `known_hosts` 文件，避免首次连接时的交互提示。
    - 输出公钥内容，方便用户将其添加到 GitHub 或 Gitee 的 SSH 密钥设置中。
    
使用方法：
1. 确保已安装 `ssh-keygen` 和 Python 环境。

2. 将本脚本中的 `drive_path` 修改为你希望保存 SSH 密钥的路径。

3. 运行该脚本，它会自动检查并生成 SSH 密钥，并提示用户将公钥添加到 GitHub 或 Gitee。

工作流：
- 定义保存 SSH 密钥的路径
  ├── 检查私钥和公钥是否已经存在
  │   ├── 如果存在，输出信息并跳过生成步骤
  │   └── 如果不存在，生成新的 SSH 密钥
  ├── 确保 SSH 目录存在
  ├── 复制私钥和公钥到 SSH 目录
  ├── 设置私钥和公钥的权限
  ├── 检查并添加 GitHub 和 Gitee 的主机密钥
  │   ├── 检查 known_hosts 是否已存在
  │   ├── 检查 known_hosts 是否已经包含 GitHub 和 Gitee 的主机密钥
  │   └── 如果不存在，添加相应的主机密钥
  ├── 打印公钥内容
  └── 提示用户将公钥添加到 GitHub 或 Gitee 的 SSH 密钥设置中
"""

# 定义保存 SSH 密钥的路径
drive_path = '/content/drive/MyDrive/env'
private_key_path = os.path.join(drive_path, 'id_rsa')
public_key_path = os.path.join(drive_path, 'id_rsa.pub')

# 定义 SSH 目录和 known_hosts 文件路径
ssh_dir = os.path.expanduser('~/.ssh')
known_hosts_path = os.path.join(ssh_dir, 'known_hosts')

# 确保保存目录存在
os.makedirs(drive_path, exist_ok=True)

# 检查私钥和公钥是否已经存在
if os.path.exists(private_key_path) and os.path.exists(public_key_path):
    print("SSH 密钥已存在，无需重复生成。")
else:
    # 生成 SSH 密钥
    print("正在生成 SSH 密钥...")
    subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-C', 'gammachineyov@139.com', 
                    '-f', private_key_path, '-N', ''])  # 无密码短语

# 确保 SSH 目录存在
os.makedirs(ssh_dir, exist_ok=True)

# 复制私钥到 SSH 目录
shutil.copy(private_key_path, os.path.join(ssh_dir, 'id_rsa'))
shutil.copy(public_key_path, os.path.join(ssh_dir, 'id_rsa.pub'))

# 设置私钥和公钥权限
subprocess.run(['chmod', '600', os.path.join(ssh_dir, 'id_rsa')])  # 仅所有者可读写
subprocess.run(['chmod', '644', os.path.join(ssh_dir, 'id_rsa.pub')])  # 所有人可读

# 检查并添加 GitHub 和 Gitee 主机密钥
if not os.path.exists(known_hosts_path):
    # 创建 known_hosts 文件
    with open(known_hosts_path, 'w') as f:
        pass

# 检查 known_hosts 是否已经包含 GitHub 和 Gitee 的主机密钥
with open(known_hosts_path, 'r') as f:
    known_hosts = f.read()

# 检查并添加 GitHub 的主机密钥
if 'github.com' not in known_hosts:
    print("正在添加 GitHub 的主机密钥到 known_hosts...")
    subprocess.run(['ssh-keyscan', '-H', 'github.com'], stdout=open(known_hosts_path, 'a'))

# 检查并添加 Gitee 的主机密钥
if 'gitee.com' not in known_hosts:
    print("正在添加 Gitee 的主机密钥到 known_hosts...")
    subprocess.run(['ssh-keyscan', '-H', 'gitee.com'], stdout=open(known_hosts_path, 'a'))

print("主机密钥已添加。")

# 打印公钥内容
with open(public_key_path, 'r') as pubkey_file:
    public_key = pubkey_file.read()

# 提示用户将公钥添加到 GitHub 或 Gitee
print("请将下述公钥添加到 GitHub 或 Gitee 的 SSH 密钥设置中。")
print("SSH 公钥:")
print(public_key)
