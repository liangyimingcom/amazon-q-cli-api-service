#!/bin/bash

# Amazon Q CLI API服务安装脚本
# 适用于Ubuntu/Debian系统

set -e

echo "开始安装Amazon Q CLI API服务..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用sudo运行此脚本"
    exit 1
fi

# 更新系统包
echo "更新系统包..."
apt-get update

# 安装Python和必要工具
echo "安装Python和必要工具..."
apt-get install -y python3 python3-pip python3-venv git curl

# 创建服务用户
echo "创建服务用户..."
if ! id "ubuntu" &>/dev/null; then
    useradd -r -s /bin/bash -d /opt/qcli-api-service ubuntu
fi

# 创建服务目录
echo "创建服务目录..."
mkdir -p /opt/qcli-api-service
chown ubuntu:ubuntu /opt/qcli-api-service

# 复制应用文件
echo "复制应用文件..."
cp -r . /opt/qcli-api-service/
chown -R ubuntu:ubuntu /opt/qcli-api-service

# 切换到服务用户
sudo -u ubuntu bash << 'EOF'
cd /opt/qcli-api-service

# 创建虚拟环境
echo "创建Python虚拟环境..."
python3 -m venv venv

# 激活虚拟环境并安装依赖
echo "安装Python依赖..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 创建环境配置文件
echo "创建环境配置文件..."
cp .env.example .env

echo "Python环境设置完成"
EOF

# 安装systemd服务
echo "安装systemd服务..."
cp deploy/systemd/qcli-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable qcli-api.service

# 创建日志目录
mkdir -p /var/log/qcli-api
chown ubuntu:ubuntu /var/log/qcli-api

echo "安装完成！"
echo ""
echo "下一步："
echo "1. 确保Amazon Q CLI已安装并配置"
echo "2. 根据需要修改 /opt/qcli-api-service/.env 配置文件"
echo "3. 启动服务: sudo systemctl start qcli-api"
echo "4. 查看状态: sudo systemctl status qcli-api"
echo "5. 查看日志: sudo journalctl -u qcli-api -f"