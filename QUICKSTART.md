# 快速开始指南

本指南将帮助您快速设置和使用Q Chat API服务的会话隔离功能。

## 🚀 5分钟快速体验

### 1. 启动服务

```bash
# 克隆项目（如果还没有）
git clone <repository-url>
cd amazon-q-cli-api-service

# 安装依赖
make install

# 启动服务
make dev
```

服务将在 `http://localhost:8080` 启动。

### 2. 验证服务

```bash
# 健康检查
make health

# 或者手动检查
curl http://localhost:8080/health
```

### 3. 体验会话隔离

```bash
# 运行完整演示
make demo
```

这将展示：
- 创建独立会话
- 在不同会话中并行处理任务
- 查看会话文件列表
- 自动清理会话目录

## 📋 基本使用流程

### 创建会话并使用

```bash
# 1. 创建会话
SESSION_ID=$(curl -s -X POST http://localhost:8080/api/v1/sessions | jq -r '.session_id')
echo "会话ID: $SESSION_ID"

# 2. 查看会话信息
curl http://localhost:8080/api/v1/sessions/$SESSION_ID | jq

# 3. 发送消息（AI会在独立目录中工作）
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"请创建一个Python脚本hello.py\"}"

# 4. 查看生成的文件
curl http://localhost:8080/api/v1/sessions/$SESSION_ID/files | jq

# 5. 清理会话
curl -X DELETE http://localhost:8080/api/v1/sessions/$SESSION_ID
```

### 管理会话目录

```bash
# 列出所有会话目录
make list-sessions

# 清理空目录
make clean-sessions

# 清理过期目录
make clean-old-sessions

# 导出会话信息
make export-sessions
```

## 🔧 配置选项

### 环境变量配置

```bash
# 自定义会话基础目录
export SESSIONS_BASE_DIR=my_sessions

# 禁用自动清理（不推荐）
export AUTO_CLEANUP_SESSIONS=false

# 其他配置
export HOST=0.0.0.0
export PORT=8080
export DEBUG=false
```

### 配置文件

编辑 `qcli_api_service/config.py` 修改默认配置：

```python
# 会话工作目录配置
SESSIONS_BASE_DIR: str = "sessions"  # 会话基础目录
AUTO_CLEANUP_SESSIONS: bool = True   # 自动清理过期会话目录
```

## 🧪 测试功能

### 自动化测试

```bash
# 运行会话隔离功能测试
make test-isolation
```

### 手动测试

```bash
# 创建两个会话测试隔离
SESSION1=$(curl -s -X POST http://localhost:8080/api/v1/sessions | jq -r '.session_id')
SESSION2=$(curl -s -X POST http://localhost:8080/api/v1/sessions | jq -r '.session_id')

# 在不同会话中创建同名文件
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION1\", \"message\": \"创建test.txt，内容为'Session 1'\"}"

curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION2\", \"message\": \"创建test.txt，内容为'Session 2'\"}"

# 验证文件隔离
curl http://localhost:8080/api/v1/sessions/$SESSION1/files
curl http://localhost:8080/api/v1/sessions/$SESSION2/files

# 清理
curl -X DELETE http://localhost:8080/api/v1/sessions/$SESSION1
curl -X DELETE http://localhost:8080/api/v1/sessions/$SESSION2
```

## 📁 目录结构

会话隔离后的目录结构：

```
project_root/
├── sessions/                    # 会话基础目录
│   ├── session-id-1/           # 会话1的工作目录
│   │   ├── hello.py            # AI生成的文件
│   │   └── data.json           # 用户数据
│   ├── session-id-2/           # 会话2的工作目录
│   │   ├── script.sh           # 不同会话的文件
│   │   └── config.yaml         # 完全隔离
│   └── ...                     # 其他会话
├── qcli_api_service/           # 服务代码
└── ...                         # 其他项目文件
```

## 🐍 Python客户端示例

```python
import requests
import json

class QChatClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def create_session(self):
        response = requests.post(f"{self.base_url}/api/v1/sessions")
        return response.json()["session_id"]
    
    def chat(self, session_id, message):
        data = {"session_id": session_id, "message": message}
        response = requests.post(f"{self.base_url}/api/v1/chat", json=data)
        return response.json()["message"]
    
    def get_files(self, session_id):
        response = requests.get(f"{self.base_url}/api/v1/sessions/{session_id}/files")
        return response.json()
    
    def delete_session(self, session_id):
        requests.delete(f"{self.base_url}/api/v1/sessions/{session_id}")

# 使用示例
client = QChatClient()

# 创建会话
session_id = client.create_session()
print(f"创建会话: {session_id}")

# 发送消息
response = client.chat(session_id, "请创建一个Python脚本")
print(f"AI回复: {response[:100]}...")

# 查看文件
files = client.get_files(session_id)
print(f"生成文件: {files['file_count']} 个")

# 清理
client.delete_session(session_id)
print("会话已清理")
```

## 🌐 JavaScript客户端示例

```javascript
class QChatClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }
    
    async createSession() {
        const response = await fetch(`${this.baseUrl}/api/v1/sessions`, {
            method: 'POST'
        });
        const data = await response.json();
        return data.session_id;
    }
    
    async chat(sessionId, message) {
        const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, message })
        });
        const data = await response.json();
        return data.message;
    }
    
    async getFiles(sessionId) {
        const response = await fetch(`${this.baseUrl}/api/v1/sessions/${sessionId}/files`);
        return await response.json();
    }
    
    async deleteSession(sessionId) {
        await fetch(`${this.baseUrl}/api/v1/sessions/${sessionId}`, {
            method: 'DELETE'
        });
    }
}

// 使用示例
(async () => {
    const client = new QChatClient();
    
    // 创建会话
    const sessionId = await client.createSession();
    console.log(`创建会话: ${sessionId}`);
    
    // 发送消息
    const response = await client.chat(sessionId, '请创建一个JavaScript函数');
    console.log(`AI回复: ${response.substring(0, 100)}...`);
    
    // 查看文件
    const files = await client.getFiles(sessionId);
    console.log(`生成文件: ${files.file_count} 个`);
    
    // 清理
    await client.deleteSession(sessionId);
    console.log('会话已清理');
})();
```

## 🔍 故障排除

### 常见问题

1. **服务启动失败**
   ```bash
   # 检查端口占用
   lsof -i :8080
   
   # 检查Amazon Q CLI
   q --version
   ```

2. **目录权限问题**
   ```bash
   # 检查目录权限
   ls -la sessions/
   
   # 修复权限
   chmod 755 sessions/
   ```

3. **会话创建失败**
   ```bash
   # 检查磁盘空间
   df -h
   
   # 检查服务日志
   tail -f app.log
   ```

### 调试技巧

```bash
# 启用调试模式
DEBUG=true make dev

# 查看详细日志
tail -f app.log | grep -E "(会话|目录|错误)"

# 检查会话状态
make list-sessions

# 手动清理
make clean-sessions
```

## 📚 更多资源

- [完整API文档](docs/API.md)
- [会话隔离详细说明](docs/SESSION_ISOLATION.md)
- [部署指南](docs/DEPLOYMENT.md)
- [使用示例](examples/README.md)

## 🆘 获取帮助

如果遇到问题：

1. 查看 [故障排除](#-故障排除) 部分
2. 运行 `make test-isolation` 检查功能
3. 查看项目 Issues
4. 提交新的 Issue 描述问题

---

🎉 **恭喜！** 您已经成功设置并体验了Q Chat API服务的会话隔离功能。现在每个会话都在独立的目录中运行，完全避免了文件冲突问题。