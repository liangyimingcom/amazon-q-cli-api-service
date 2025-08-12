# Amazon Q CLI API服务接口文档

## 概述

Amazon Q CLI API服务提供RESTful API接口，用于与Amazon Q CLI进行交互。支持标准聊天和流式聊天两种模式，并提供完整的会话管理功能。

## 基础信息

- **基础URL**: `http://localhost:8080`
- **内容类型**: `application/json`
- **字符编码**: UTF-8

## API接口

### 1. 服务信息

#### GET /

获取服务基本信息。

**响应示例**:
```json
{
  "service": "Amazon Q CLI API Service",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "chat": "/api/v1/chat",
    "stream_chat": "/api/v1/chat/stream",
    "sessions": "/api/v1/sessions",
    "health": "/health"
  }
}
```

#### GET /health

健康检查接口。

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "qcli_available": true,
  "active_sessions": 5,
  "version": "1.0.0"
}
```

**状态说明**:
- `healthy`: 服务正常运行
- `degraded`: Q CLI不可用，但其他功能正常
- `unhealthy`: 服务异常

### 2. 会话管理

#### POST /api/v1/sessions

创建新会话。

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1703123456.789
}
```

#### GET /api/v1/sessions/{session_id}

获取会话信息。

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1703123456.789,
  "last_activity": 1703123500.123,
  "message_count": 6
}
```

#### DELETE /api/v1/sessions/{session_id}

删除会话。

**响应示例**:
```json
{
  "message": "会话已删除"
}
```

### 3. 聊天接口

#### POST /api/v1/chat

标准聊天接口。

**请求参数**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",  // 可选，不提供则创建新会话
  "message": "你好，请介绍一下自己"
}
```

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "你好！我是Amazon Q AI助手，很高兴为您服务。",
  "timestamp": 1703123456.789
}
```

#### POST /api/v1/chat/stream

流式聊天接口，使用Server-Sent Events (SSE)。

**请求参数**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",  // 可选
  "message": "请详细介绍一下Amazon Q的功能"
}
```

**响应格式**: `text/event-stream`

**响应示例**:
```
data: {"session_id": "550e8400-e29b-41d4-a716-446655440000", "type": "session"}

data: {"message": "Amazon Q是一个", "type": "chunk"}

data: {"message": "强大的AI助手", "type": "chunk"}

data: {"message": "，可以帮助您...", "type": "chunk"}

data: {"type": "done"}
```

**事件类型**:
- `session`: 会话信息
- `chunk`: 消息片段
- `done`: 传输完成
- `error`: 错误信息

## 错误处理

所有错误响应都使用标准格式：

```json
{
  "error": "错误描述",
  "code": 400,
  "details": "详细错误信息（可选）"
}
```

**常见错误码**:
- `400`: 请求参数错误
- `404`: 资源不存在（如会话不存在）
- `500`: 内部服务器错误
- `503`: 服务不可用（如Q CLI不可用）

## 使用示例

### Python示例

```python
import requests
import json

# 基础URL
BASE_URL = "http://localhost:8080"

# 创建会话
response = requests.post(f"{BASE_URL}/api/v1/sessions")
session_data = response.json()
session_id = session_data["session_id"]

# 发送消息
chat_data = {
    "session_id": session_id,
    "message": "你好，请介绍一下自己"
}

response = requests.post(f"{BASE_URL}/api/v1/chat", json=chat_data)
result = response.json()

print(f"AI回复: {result['message']}")
```

### JavaScript示例

```javascript
// 创建会话
async function createSession() {
    const response = await fetch('/api/v1/sessions', {
        method: 'POST'
    });
    const data = await response.json();
    return data.session_id;
}

// 发送消息
async function sendMessage(sessionId, message) {
    const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message
        })
    });
    
    const data = await response.json();
    return data.message;
}

// 流式聊天
function streamChat(sessionId, message) {
    const eventSource = new EventSource('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: sessionId,
            message: message
        })
    });
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        
        if (data.type === 'chunk') {
            console.log('收到消息片段:', data.message);
        } else if (data.type === 'done') {
            console.log('消息传输完成');
            eventSource.close();
        }
    };
}
```

### cURL示例

```bash
# 创建会话
curl -X POST http://localhost:8080/api/v1/sessions

# 发送消息
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "你好"
  }'

# 流式聊天
curl -X POST http://localhost:8080/api/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "message": "请详细介绍一下Amazon Q"
  }'

# 健康检查
curl http://localhost:8080/health
```

## 最佳实践

1. **会话管理**: 为每个用户或对话场景创建独立的会话
2. **错误处理**: 始终检查响应状态码并处理错误情况
3. **超时设置**: 设置合理的请求超时时间（建议30-60秒）
4. **流式处理**: 对于长回复，优先使用流式接口提升用户体验
5. **资源清理**: 不再使用的会话应及时删除以释放资源

## 限制说明

1. **消息长度**: 单条消息最大4000字符
2. **会话过期**: 会话在1小时无活动后自动过期
3. **历史长度**: 每个会话最多保留10条历史消息
4. **并发限制**: 建议控制并发请求数量以确保服务稳定性