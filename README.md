# Amazon Q CLI API服务

一个基于Flask的RESTful API服务，提供Amazon Q CLI集成功能。支持AI对话处理、流式回复和上下文保持。

## ✨ 核心功能

- 🤖 **AI对话处理** - 调用Amazon Q CLI生成智能回复
- 🔄 **流式回复** - 实时发送回复内容，提升用户体验
- 💬 **上下文保持** - 维护对话历史，支持连续多轮对话
- 🔧 **会话管理** - 支持多用户、多会话的并发处理
- 🛡️ **安全防护** - 输入验证、错误处理和安全防护
- 📊 **健康监控** - 提供健康检查和状态监控接口

## 🚀 快速开始

### 前置条件

- Python 3.8+
- Amazon Q CLI（已安装并配置）
- 2GB+ 内存的服务器

### 安装和运行

1. **克隆项目**:
```bash
git clone <repository-url>
cd amazon-q-cli-api-service
```

2. **创建虚拟环境**:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

3. **安装依赖**:
```bash
pip install -r requirements.txt
```

4. **配置环境**:
```bash
cp .env.example .env
# 根据需要修改 .env 文件
```

5. **启动服务**:
```bash
python app.py
```

服务将在 `http://localhost:8080` 启动。

### 验证安装

```bash
# 健康检查
curl http://localhost:8080/health

# 创建会话并发送消息
curl -X POST http://localhost:8080/api/v1/sessions
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}'
```

## 📖 API文档

### 主要接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/` | GET | 服务信息 |
| `/health` | GET | 健康检查 |
| `/api/v1/sessions` | POST | 创建会话 |
| `/api/v1/sessions/{id}` | GET/DELETE | 会话管理 |
| `/api/v1/chat` | POST | 标准聊天 |
| `/api/v1/chat/stream` | POST | 流式聊天 |

### 使用示例

**创建会话并聊天**:
```bash
# 1. 创建会话
SESSION_ID=$(curl -s -X POST http://localhost:8080/api/v1/sessions | jq -r '.session_id')

# 2. 发送消息
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"你好，请介绍一下自己\"}"
```

**流式聊天**:
```bash
curl -X POST http://localhost:8080/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "请详细介绍Amazon Q的功能"}' \
  --no-buffer
```

**流式聊天**:
```bash
# 1. 创建会话
SESSION_ID=$(curl -s -X POST http://localhost:8080/api/v1/sessions | jq -r '.session_id')

# 2. 发送消息

curl -X POST http://localhost:8080/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"你好，请介绍一下自己\"}" \
  --no-buffer
```



详细API文档请参考 [docs/API.md](docs/API.md)。

## 🏗️ 项目结构

```
amazon-q-cli-api-service/
├── qcli_api_service/          # 主要应用代码
│   ├── api/                   # API控制器和路由
│   ├── models/                # 数据模型
│   ├── services/              # 业务逻辑服务
│   ├── utils/                 # 工具函数
│   ├── config.py              # 配置管理
│   └── app.py                 # Flask应用工厂
├── tests/                     # 测试代码
│   ├── unit/                  # 单元测试
│   └── integration/           # 集成测试
├── deploy/                    # 部署配置
├── docs/                      # 文档
├── app.py                     # 应用入口
├── requirements.txt           # Python依赖
└── README.md                  # 项目说明
```

## 🔧 配置选项

主要配置项（通过环境变量设置）：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 8080 | 服务端口 |
| `DEBUG` | false | 调试模式 |
| `SESSION_EXPIRY` | 3600 | 会话过期时间（秒） |
| `MAX_HISTORY_LENGTH` | 10 | 最大历史消息数 |
| `QCLI_TIMEOUT` | 30 | Q CLI调用超时时间（秒） |
| `FORCE_CHINESE` | true | 强制中文回复 |

## 🚀 部署

### EC2部署（推荐）

使用自动安装脚本：

```bash
sudo ./deploy/install.sh
```

手动部署步骤请参考 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

### Docker部署

```bash
# 构建镜像
docker build -t qcli-api-service .

# 运行容器
docker run -d -p 8080:8080 --name qcli-api qcli-api-service

# 或使用Docker Compose
docker-compose up -d
```

### systemd服务

```bash
# 安装服务
sudo cp deploy/systemd/qcli-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable qcli-api
sudo systemctl start qcli-api
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
python -m pytest

# 运行单元测试
python -m pytest tests/unit/

# 运行集成测试
python -m pytest tests/integration/

# 生成覆盖率报告
python -m pytest --cov=qcli_api_service --cov-report=html
```

## 📊 监控

### 健康检查

```bash
curl http://localhost:8080/health
```

响应示例：
```json
{
  "status": "healthy",
  "qcli_available": true,
  "active_sessions": 5,
  "timestamp": 1703123456.789
}
```

### 日志监控

```bash
# systemd服务日志
sudo journalctl -u qcli-api -f

# 应用日志
tail -f qcli_api_service.log
```

## 🔒 安全考虑

- ✅ 输入验证和清理
- ✅ 错误信息脱敏
- ✅ 会话隔离
- ✅ 请求参数验证
- ✅ 恶意内容检测
- ⚠️ 建议配置HTTPS
- ⚠️ 建议启用请求频率限制

## 🛠️ 开发

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行开发服务器
DEBUG=true python app.py

# 代码格式化
black qcli_api_service/ tests/

# 代码检查
flake8 qcli_api_service/ tests/
```

### 贡献指南

1. Fork项目
2. 创建功能分支
3. 编写测试
4. 确保所有测试通过
5. 提交Pull Request

## 📝 更新日志

### v1.0.0 (2024-01-01)

- ✨ 初始版本发布
- 🤖 Amazon Q CLI集成
- 🔄 流式回复支持
- 💬 上下文保持功能
- 🔧 会话管理
- 🛡️ 安全防护
- 📊 健康监控
- 🧪 完整测试套件

## 🤝 支持

如果遇到问题或需要帮助：

1. 查看 [API文档](docs/API.md)
2. 查看 [部署指南](docs/DEPLOYMENT.md)
3. 检查 [Issues](../../issues)
4. 提交新的Issue

## 📄 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- Amazon Q CLI团队
- Flask框架
- 所有贡献者