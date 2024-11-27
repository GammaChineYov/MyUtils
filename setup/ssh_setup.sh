#!/bin/bash

# 检查传入参数个数是否为0
if [[ $# -eq 0 ]]; then
    echo "用法: $0 --user [用户名] --ip [IP地址] --password [密码]"
    echo "示例: $0 --user root --ip 192.168.1.100 --password your_password"
    exit 1
fi

# 用于存储解析后的参数
user=""
ip=""
password=""

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --user)
            user="$2"
            shift 2
            ;;
        --ip)
            ip="$2"
            shift 2
            ;;
        --password)
            password="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查参数是否完整
if [[ -z $user ]] || [[ -z $ip ]] || [[ -z $password ]]; then
    echo "请提供完整的参数: --user --ip --password"
    exit 1
fi

# 生成SSH密钥对（如果不存在）
if [[ ! -f ~/.ssh/id_rsa ]]; then
    echo "生成SSH密钥对..."
    ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa
else
    echo "SSH密钥已存在，跳过生成步骤。"
fi

# 使用sshpass将公钥复制到远程主机并设置密码
echo "将公钥复制到远程主机..."
sshpass -p "$password" ssh-copy-id -i ~/.ssh/id_rsa.pub "$user@$ip"

# 检查公钥是否成功复制
if [[ $? -ne 0 ]]; then
    echo "公钥复制失败，退出脚本。"
    exit 1
fi

# 配置远程主机的sshd_config文件
echo "配置远程主机的SSH设置..."
ssh -o StrictHostKeyChecking=no -t "$user@$ip" "
    sudo sed -i.bak 's/^#\(PubkeyAuthentication yes\)/\1/' /etc/ssh/sshd_config &&
    sudo service ssh restart
"

# 检查 SSH 配置是否成功
if [[ $? -eq 0 ]]; then
    echo "SSH配置成功，重新启动服务完成。"
else
    echo "SSH配置失败，请手动检查远程主机的sshd_config文件。"
    exit 1
fi

echo "脚本执行完毕，您可以通过SSH无密码登录远程主机。"

