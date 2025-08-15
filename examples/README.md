# 使用示例

本目录包含Q Chat API服务的使用示例和演示脚本。

## 文件说明

### session_isolation_demo.py

会话隔离功能的完整演示脚本，展示以下功能：

- **基本会话隔离**: 创建会话、生成文件、查看文件列表
- **并行会话处理**: 同时处理多个会话的不同任务
- **文件管理**: 在会话中创建多个文件并管理

#### 运行方式

```bash
# 确保API服务正在运行
python app.py

# 在另一个终端运行演示
python examples/session_isolation_demo.py
```

#### 演示内容

1. **基本隔离演示**:
   - 创建会话并获取工作目录信息
   - 请求AI创建Python脚本
   - 查看生成的文件列表
   - 清理会话和文件

2. **并行处理演示**:
   - 同时创建3个会话
   - 并行执行不同的编程任务（Python、JavaScript、Shell）
   - 展示会话间的完全隔离
   - 批量清理所有会话

3. **文件管理演示**:
   - 在单个会话中创建多种类型的文件
   - 实时查看文件列表变化
   - 展示文件管理API的使用

#### 预期输出

```
🎯 Q Chat 会话隔离功能演示
==================================================
✅ API服务运行正常

🔍 演示基本会话隔离功能
----------------------------------------
✅ 创建会话: 550e8400-e29b-41d4-a716-446655440000
📁 工作目录: sessions/550e8400-e29b-41d4-a716-446655440000

💬 请求创建Python脚本...
🤖 AI回复: 我来为您创建一个简单的Python脚本...

📄 会话文件数量: 1
   - hello.py (156 bytes)

🗑️ 会话已删除: 550e8400-e29b-41d4-a716-446655440000

🔍 演示并行会话处理
----------------------------------------
✅ 创建会话 1: 660f9511-f3ac-52e5-b827-557766551111
✅ 创建会话 2: 770a0622-04bd-63f6-c938-668877662222
✅ 创建会话 3: 880b1733-15ce-74g7-da49-779988773333

🚀 开始处理 Python任务 (会话: 660f9511...)
🚀 开始处理 JavaScript任务 (会话: 770a0622...)
🚀 开始处理 Shell任务 (会话: 880b1733...)

✅ Python任务 完成 (会话: 660f9511...)
✅ JavaScript任务 完成 (会话: 770a0622...)
✅ Shell任务 完成 (会话: 880b1733...)

📄 Python任务 生成了 1 个文件
📄 JavaScript任务 生成了 1 个文件
📄 Shell任务 生成了 1 个文件

📊 所有会话的最终状态:
   会话 1: 1 个文件，目录: sessions/660f9511-f3ac-52e5-b827-557766551111
   会话 2: 1 个文件，目录: sessions/770a0622-04bd-63f6-c938-668877662222
   会话 3: 1 个文件，目录: sessions/880b1733-15ce-74g7-da49-779988773333

🗑️ 清理所有会话...
   ✅ 已删除会话: 660f9511...
   ✅ 已删除会话: 770a0622...
   ✅ 已删除会话: 880b1733...

🔍 演示文件管理功能
----------------------------------------
✅ 创建会话: 990c2844-26df-85h8-eb5a-88aa99884444
📁 工作目录: sessions/990c2844-26df-85h8-eb5a-88aa99884444

💬 任务 1: 请创建一个config.json文件，包含应用配置信息...
🤖 任务 1 完成

💬 任务 2: 请创建一个README.md文件，说明项目用途...
🤖 任务 2 完成

💬 任务 3: 请创建一个requirements.txt文件，列出Python依赖...
🤖 任务 3 完成

📄 最终文件列表:
   总文件数: 3
   工作目录: sessions/990c2844-26df-85h8-eb5a-88aa99884444
   - config.json (245 KB)
   - README.md (512 KB)
   - requirements.txt (89 KB)

🗑️ 会话已删除，文件已清理

==================================================
🎉 演示完成！

💡 要点总结:
   - 每个会话都有独立的工作目录
   - 不同会话的文件操作完全隔离
   - 可以并行处理多个会话
   - 会话删除时自动清理文件
   - 提供API查看会话文件列表
```

## 其他示例

### 基本API调用示例

```python
import requests

# 创建会话
response = requests.post('http://localhost:8080/api/v1/sessions')
session_id = response.json()['session_id']

# 发送消息
chat_data = {
    'session_id': session_id,
    'message': '请创建一个Python脚本'
}
response = requests.post('http://localhost:8080/api/v1/chat', json=chat_data)
print(response.json()['message'])

# 查看文件列表
response = requests.get(f'http://localhost:8080/api/v1/sessions/{session_id}/files')
files = response.json()
print(f"生成了 {files['file_count']} 个文件")

# 删除会话
requests.delete(f'http://localhost:8080/api/v1/sessions/{session_id}')
```

### 流式聊天示例

```python
import requests
import json

def stream_chat(session_id, message):
    data = {
        'session_id': session_id,
        'message': message
    }
    
    response = requests.post(
        'http://localhost:8080/api/v1/chat/stream',
        json=data,
        stream=True
    )
    
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = json.loads(line[6:])
                if data.get('type') == 'chunk':
                    print(data['message'], end='', flush=True)
                elif data.get('type') == 'done':
                    print('\n完成')
                    break

# 使用示例
session_id = 'your-session-id'
stream_chat(session_id, '请详细介绍Python的特性')
```

## 注意事项

1. **服务依赖**: 运行示例前请确保API服务正在运行
2. **Amazon Q CLI**: 确保已正确安装和配置Amazon Q CLI
3. **网络连接**: 某些功能需要网络连接到Amazon Q服务
4. **权限设置**: 确保有足够的文件系统权限创建和删除目录
5. **资源清理**: 示例会自动清理创建的会话和文件

## 故障排除

### 常见问题

1. **连接错误**: 检查API服务是否在正确端口运行
2. **权限错误**: 检查文件系统权限设置
3. **Q CLI错误**: 检查Amazon Q CLI配置和网络连接
4. **超时错误**: 某些操作可能需要较长时间，请耐心等待

### 调试技巧

```bash
# 查看API服务日志
tail -f app.log

# 检查会话目录
ls -la sessions/

# 手动测试API
curl -X POST http://localhost:8080/api/v1/sessions
curl http://localhost:8080/health
```