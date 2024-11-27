#!/bin/bash

# 创建4GB大小的交换文件
dd if=/dev/zero of=/swapfile bs=1M count=4096

# 设置交换文件权限
chmod 600 /swapfile
#
# # 格式化交换文件
mkswap /swapfile
#
# # 启用交换文件
swapon /swapfile
#
# # 输出提示信息
echo "虚拟内存扩容成功，已添加4GB交换空间。"
#
# （可选）设置开机自动挂载交换文件，以下是示例，需谨慎操作，注释掉是因为可能导致问题
echo "/swapfile none swap sw 0 0" >> /etc/fstab
#
