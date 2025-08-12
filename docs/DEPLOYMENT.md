# Amazon Q CLI API服务部署指南

## 概述

本文档介绍如何在EC2实例上部署Amazon Q CLI API服务。

## 系统要求

### 最低配置
- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **CPU**: 1 vCPU
- **内存**: 1 GB RAM
- **存储**: 10 GB 可用空间
- **网络**: 允许入站端口8080

### 推荐配置
- **操作系统**: Ubuntu 22.04 LTS
- **CPU**: 2 vCPU
- **内存**: 2 GB RAM
- **存储**: 20 GB 可用空间

## 前置条件

1. **Amazon Q CLI**: 必须已安装并配置Amazon Q CLI
2. **Python**: Python 3.8或更高版本
3. **网络**: 确保EC2实例可以访问Amazon Q服务

## 部署方式

### 方式一：自动安装脚本（推荐）

1. **下载项目代码**:
```bash
git clone <repository-url>
cd amazon-q-cli-api-service
```

2. **运行安装脚本**:
```bash
sudo ./deploy/install.sh
```

3. **配置环境变量**:
```bash
sudo nano /opt/qcli-api-service/.env
```

4. **启动服务**:
```bash
sudo systemctl start qcli-api
sudo systemctl enable qcli-api
```

### 方式二：手动安装

#### 1. 准备环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和必要工具
sudo apt install -y python3 python3-pip python3-venv git curl

# 创建服务用户
sudo useradd -r -s /bin/bash -d /opt/qcli-api-service qcli-api

# 创建服务目录
sudo mkdir -p /opt/qcli-api-service
sudo chown qcli-api:qcli-api /opt/qcli-api-service
```

#### 2. 部署应用

```bash
# 复制应用文件
sudo cp -r . /opt/qcli-api-service/
sudo chown -R qcli-api:qcli-api /opt/qcli-api-service

# 切换到服务用户
sudo -u qcli-api bash
cd /opt/qcli-api-service

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置文件
cp .env.example .env
```

#### 3. 配置systemd服务

```bash
# 复制服务文件
sudo cp deploy/systemd/qcli-api.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启用并启动服务
sudo systemctl enable qcli-api
sudo systemctl start qcli-api
```

### 方式三：Docker部署

#### 1. 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo apt install -y docker-compose
```

#### 2. 构建和运行

```bash
# 构建镜像
docker build -t qcli-api-service .

# 使用Docker Compose运行
docker-compose up -d
```

## 配置说明

### 环境变量配置

编辑 `/opt/qcli-api-service/.env` 文件：

```bash
# 服务配置
HOST=0.0.0.0
PORT=8080
DEBUG=false

# 会话配置
SESSION_EXPIRY=3600        # 会话过期时间（秒）
MAX_HISTORY_LENGTH=10      # 最大历史消息数

# Q CLI配置
QCLI_TIMEOUT=30           # Q CLI调用超时时间（秒）
FORCE_CHINESE=true        # 强制中文回复
```

### 防火墙配置

```bash
# 允许API服务端口
sudo ufw allow 8080/tcp

# 如果使用nginx反向代理
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Nginx反向代理（可选）

创建 `/etc/nginx/sites-available/qcli-api`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 支持Server-Sent Events
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/qcli-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 验证部署

### 1. 检查服务状态

```bash
# 检查systemd服务状态
sudo systemctl status qcli-api

# 检查服务日志
sudo journalctl -u qcli-api -f

# 检查端口监听
sudo netstat -tlnp | grep 8080
```

### 2. 测试API接口

```bash
# 健康检查
curl http://localhost:8080/health

# 服务信息
curl http://localhost:8080/

# 创建会话
curl -X POST http://localhost:8080/api/v1/sessions

# 发送测试消息
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，请介绍一下自己"}'
```

### 3. 性能测试

```bash
# 安装测试工具
sudo apt install -y apache2-utils

# 并发测试
ab -n 100 -c 10 http://localhost:8080/health
```

## 监控和维护

### 日志管理

```bash
# 查看实时日志
sudo journalctl -u qcli-api -f

# 查看最近的日志
sudo journalctl -u qcli-api --since "1 hour ago"

# 日志轮转配置
sudo nano /etc/logrotate.d/qcli-api
```

### 性能监控

```bash
# 查看系统资源使用
htop

# 查看服务进程
ps aux | grep python

# 查看网络连接
sudo netstat -tlnp | grep 8080
```

### 备份和恢复

```bash
# 备份配置文件
sudo cp /opt/qcli-api-service/.env /backup/

# 备份应用代码
sudo tar -czf /backup/qcli-api-$(date +%Y%m%d).tar.gz /opt/qcli-api-service/
```

## 故障排查

### 常见问题

1. **服务无法启动**
   - 检查Python虚拟环境是否正确
   - 验证依赖包是否完整安装
   - 检查端口是否被占用

2. **Q CLI不可用**
   - 验证Amazon Q CLI是否正确安装
   - 检查AWS凭证配置
   - 测试Q CLI命令行工具

3. **内存不足**
   - 增加EC2实例内存
   - 优化会话清理策略
   - 减少MAX_HISTORY_LENGTH配置

### 调试命令

```bash
# 手动运行服务（调试模式）
sudo -u qcli-api bash
cd /opt/qcli-api-service
source venv/bin/activate
DEBUG=true python app.py

# 检查Q CLI可用性
q --version
q chat --help

# 检查Python环境
python3 --version
pip list
```

## 安全建议

1. **网络安全**
   - 使用安全组限制访问来源
   - 考虑使用VPN或私有网络
   - 启用HTTPS（使用nginx + Let's Encrypt）

2. **系统安全**
   - 定期更新系统和依赖包
   - 使用非root用户运行服务
   - 配置防火墙规则

3. **应用安全**
   - 启用请求频率限制
   - 监控异常请求模式
   - 定期检查日志

## 扩展部署

### 负载均衡

使用nginx进行负载均衡：

```nginx
upstream qcli_api {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    location / {
        proxy_pass http://qcli_api;
    }
}
```

### 高可用部署

1. 使用多个EC2实例
2. 配置Application Load Balancer
3. 使用Auto Scaling Group
4. 考虑使用ECS或EKS进行容器化部署

## 更新和维护

### 应用更新

```bash
# 停止服务
sudo systemctl stop qcli-api

# 备份当前版本
sudo cp -r /opt/qcli-api-service /backup/qcli-api-backup-$(date +%Y%m%d)

# 更新代码
cd /opt/qcli-api-service
sudo -u qcli-api git pull

# 更新依赖
sudo -u qcli-api bash -c "source venv/bin/activate && pip install -r requirements.txt"

# 重启服务
sudo systemctl start qcli-api
```

### 系统维护

```bash
# 清理过期会话（如果需要）
# 这通常由应用自动处理

# 清理日志文件
sudo journalctl --vacuum-time=30d

# 更新系统包
sudo apt update && sudo apt upgrade -y
```