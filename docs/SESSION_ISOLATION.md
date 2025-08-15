# 会话隔离功能说明

## 概述

为了避免不同会话之间的文件冲突和数据串扰，Q Chat API服务现在为每个会话创建独立的工作目录。每个会话都在自己专用的目录中运行，确保文件操作的隔离性和安全性。

## 功能特性

### 1. 独立工作目录

- **自动创建**: 创建会话时自动生成以SESSION_ID命名的独立目录
- **目录结构**: `sessions/{session_id}/`
- **完全隔离**: 每个会话的文件操作都在自己的目录中进行
- **自动清理**: 会话删除或过期时自动清理对应目录

### 2. 目录管理

- **基础目录**: 默认为项目根目录下的 `sessions/` 文件夹
- **可配置**: 通过环境变量 `SESSIONS_BASE_DIR` 自定义基础目录
- **自动清理**: 通过 `AUTO_CLEANUP_SESSIONS` 控制是否自动清理过期目录

### 3. API增强

- **会话信息**: 获取会话信息时包含工作目录路径
- **文件列表**: 新增API端点获取会话目录中的文件列表
- **相对路径**: 提供相对路径和绝对路径两种格式

## 配置选项

### 环境变量

```bash
# 会话基础目录（默认: sessions）
SESSIONS_BASE_DIR=sessions

# 自动清理过期会话目录（默认: true）
AUTO_CLEANUP_SESSIONS=true
```

### 配置文件

在 `qcli_api_service/config.py` 中可以修改默认配置：

```python
# 会话工作目录配置
SESSIONS_BASE_DIR: str = "sessions"  # 会话基础目录
AUTO_CLEANUP_SESSIONS: bool = True  # 自动清理过期会话目录
```

## API使用示例

### 1. 创建会话

```bash
curl -X POST http://localhost:8080/api/v1/sessions
```

响应：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1703123456.789
}
```

此时会自动创建目录：`sessions/550e8400-e29b-41d4-a716-446655440000/`

### 2. 获取会话信息

```bash
curl http://localhost:8080/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
```

响应：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": 1703123456.789,
  "last_activity": 1703123500.123,
  "message_count": 6,
  "work_directory": "sessions/550e8400-e29b-41d4-a716-446655440000",
  "absolute_work_directory": "/path/to/project/sessions/550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. 获取会话文件列表

```bash
curl http://localhost:8080/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/files
```

响应：
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "work_directory": "sessions/550e8400-e29b-41d4-a716-446655440000",
  "absolute_work_directory": "/path/to/project/sessions/550e8400-e29b-41d4-a716-446655440000",
  "files": [
    {
      "name": "example.py",
      "path": "example.py",
      "size": 1024,
      "modified_time": 1703123500.123
    }
  ],
  "file_count": 1
}
```

## 管理工具

### 命令行管理脚本

提供了 `scripts/manage_sessions.py` 脚本来管理会话目录：

```bash
# 列出所有会话目录
python scripts/manage_sessions.py list

# 查看指定会话详情
python scripts/manage_sessions.py detail 550e8400-e29b-41d4-a716-446655440000

# 清理空目录
python scripts/manage_sessions.py cleanup-empty

# 清理过期目录（超过24小时）
python scripts/manage_sessions.py cleanup-old --hours 24

# 导出会话信息到JSON文件
python scripts/manage_sessions.py export sessions_info.json
```

### 程序化管理

可以使用 `SessionDirectoryManager` 类进行程序化管理：

```python
from qcli_api_service.utils.session_directory_manager import session_directory_manager

# 列出所有会话目录
directories = session_directory_manager.list_session_directories()

# 获取指定会话目录信息
info = session_directory_manager.get_directory_info(session_id)

# 清理空目录
cleaned_count = session_directory_manager.cleanup_empty_directories()

# 清理过期目录
cleaned_count = session_directory_manager.cleanup_old_directories(hours=24)
```

## 工作原理

### 1. 会话创建流程

1. 用户调用创建会话API
2. 系统生成唯一的SESSION_ID
3. 在基础目录下创建以SESSION_ID命名的子目录
4. 返回会话信息，包含工作目录路径

### 2. Q CLI执行流程

1. 接收到聊天请求时，获取会话的工作目录
2. 将工作目录作为 `cwd` 参数传递给Q CLI进程
3. Q CLI在指定目录中执行，所有文件操作都在该目录内进行

### 3. 清理机制

1. **手动删除**: 调用删除会话API时立即清理目录
2. **自动过期**: 会话过期时自动清理目录（如果启用）
3. **批量清理**: 使用管理脚本批量清理空目录或过期目录

## 目录结构示例

```
project_root/
├── sessions/                           # 会话基础目录
│   ├── 550e8400-e29b-41d4-a716-446655440000/  # 会话1的工作目录
│   │   ├── example.py                  # Q CLI生成的文件
│   │   ├── data.json                   # 用户数据文件
│   │   └── output/                     # 子目录
│   │       └── result.txt              # 输出文件
│   ├── 660f9511-f3ac-52e5-b827-557766551111/  # 会话2的工作目录
│   │   ├── script.sh                   # 不同会话的文件
│   │   └── config.yaml                 # 完全隔离
│   └── ...                             # 其他会话目录
├── qcli_api_service/                   # 服务代码
├── docs/                               # 文档
└── scripts/                            # 管理脚本
```

## 最佳实践

### 1. 目录管理

- **定期清理**: 使用管理脚本定期清理过期或空的会话目录
- **监控空间**: 监控会话目录占用的磁盘空间
- **备份重要数据**: 对重要的会话数据进行备份

### 2. 安全考虑

- **权限控制**: 确保会话目录有适当的文件权限
- **路径验证**: API不直接暴露文件系统路径给客户端
- **隔离保证**: 每个会话只能访问自己的工作目录

### 3. 性能优化

- **异步清理**: 在后台异步执行目录清理操作
- **批量操作**: 批量处理多个会话的清理操作
- **缓存信息**: 缓存会话目录信息以提高查询性能

## 故障排除

### 常见问题

1. **目录创建失败**
   - 检查基础目录的写权限
   - 确保磁盘空间充足

2. **文件访问权限问题**
   - 检查Q CLI进程的用户权限
   - 确保目录权限设置正确

3. **清理失败**
   - 检查是否有进程正在使用目录中的文件
   - 确保有删除权限

### 日志监控

系统会记录以下关键操作的日志：

- 会话目录创建
- 会话目录删除
- 清理操作结果
- 错误和异常情况

查看日志：
```bash
tail -f app.log | grep -E "(创建新会话|删除会话|清理)"
```

## 升级说明

### 从旧版本升级

如果从不支持会话隔离的版本升级，需要注意：

1. **配置更新**: 检查并更新配置文件中的新配置项
2. **目录迁移**: 现有会话将在下次活动时自动创建工作目录
3. **API兼容**: 新增的API字段向后兼容，不会影响现有客户端

### 数据迁移

如果需要迁移现有数据到会话目录：

```python
# 示例迁移脚本
import os
import shutil
from qcli_api_service.services.session_manager import session_manager

# 为现有会话创建工作目录并迁移数据
for session_id, session in session_manager._sessions.items():
    if not hasattr(session, 'work_directory'):
        # 创建工作目录
        work_dir = os.path.join("sessions", session_id)
        os.makedirs(work_dir, exist_ok=True)
        session.work_directory = work_dir
        
        # 迁移现有文件（如果有）
        # shutil.move(old_file_path, os.path.join(work_dir, filename))
```