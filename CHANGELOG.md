# 更新日志

## [1.1.0] - 2024-01-15

### 新增功能 ✨

#### 会话隔离功能
- **独立工作目录**: 每个会话现在在以SESSION_ID命名的独立目录中运行
- **文件隔离**: 完全避免不同会话之间的文件冲突和数据串扰
- **自动目录管理**: 会话创建时自动创建目录，删除时自动清理
- **新增API端点**: `GET /api/v1/sessions/{session_id}/files` 获取会话文件列表

#### 管理工具
- **命令行管理脚本**: `scripts/manage_sessions.py` 提供完整的会话目录管理功能
- **会话目录管理器**: `SessionDirectoryManager` 类提供程序化管理接口
- **批量清理功能**: 支持清理空目录和过期目录

#### 配置增强
- **新增配置项**: `SESSIONS_BASE_DIR` 自定义会话基础目录
- **自动清理控制**: `AUTO_CLEANUP_SESSIONS` 控制是否自动清理过期目录
- **环境变量支持**: 所有新配置项都支持环境变量配置

### API 变更 🔄

#### 新增端点
- `GET /api/v1/sessions/{session_id}/files` - 获取会话文件列表

#### 响应格式变更
- 会话信息响应新增字段：
  - `work_directory`: 相对工作目录路径
  - `absolute_work_directory`: 绝对工作目录路径

#### 服务信息更新
- 根路径响应新增 `session_files` 端点信息

### 文档更新 📚

#### 新增文档
- `docs/SESSION_ISOLATION.md` - 会话隔离功能详细说明
- `examples/README.md` - 使用示例说明文档

#### 更新文档
- `docs/API.md` - 更新API文档，添加新端点说明
- `README.md` - 添加会话隔离功能介绍和使用示例

### 示例和工具 🛠️

#### 新增示例
- `examples/session_isolation_demo.py` - 完整的会话隔离功能演示
- `scripts/test_session_isolation.py` - 自动化测试脚本

#### 管理工具
- `scripts/manage_sessions.py` - 会话目录管理命令行工具
  - `list` - 列出所有会话目录
  - `detail` - 查看指定会话详情
  - `cleanup-empty` - 清理空目录
  - `cleanup-old` - 清理过期目录
  - `export` - 导出会话信息

#### Makefile 增强
- 新增会话管理相关命令
- 新增测试和演示命令
- 新增健康检查命令

### 技术实现 🔧

#### 核心变更
- `Session` 模型新增 `work_directory` 字段
- `SessionManager` 增加目录管理功能
- `QCLIService` 支持在指定工作目录中执行
- 控制器传递工作目录参数给Q CLI服务

#### 新增模块
- `qcli_api_service/utils/session_directory_manager.py` - 会话目录管理器

#### 安全增强
- 路径验证和清理
- 目录权限检查
- 错误处理和日志记录

### 向后兼容性 ✅

- 所有现有API保持完全兼容
- 新增字段不影响现有客户端
- 配置项都有合理的默认值
- 现有会话在下次活动时自动获得工作目录

### 升级指南 📋

#### 从 v1.0.0 升级

1. **更新代码**: 拉取最新代码
2. **安装依赖**: 运行 `pip install -r requirements.txt`
3. **配置检查**: 检查新的配置项（可选）
4. **重启服务**: 重启API服务
5. **验证功能**: 运行测试脚本验证新功能

#### 可选配置
```bash
# 自定义会话基础目录
export SESSIONS_BASE_DIR=my_sessions

# 禁用自动清理（不推荐）
export AUTO_CLEANUP_SESSIONS=false
```

#### 验证安装
```bash
# 运行功能测试
make test-isolation

# 运行演示
make demo

# 检查会话目录
make list-sessions
```

### 性能影响 📊

- **目录创建**: 每个会话创建时增加约1-2ms的目录创建时间
- **文件操作**: Q CLI在独立目录中运行，性能基本无影响
- **内存使用**: 每个会话增加约100字节的目录路径存储
- **磁盘空间**: 根据会话中生成的文件数量而定

### 已知限制 ⚠️

- 会话目录路径长度受文件系统限制
- 大量并发会话可能影响文件系统性能
- 目录清理操作可能需要一定时间

### 故障排除 🔧

#### 常见问题
1. **目录创建失败**: 检查基础目录权限
2. **清理失败**: 确保没有进程占用目录
3. **路径过长**: 考虑缩短基础目录路径

#### 调试命令
```bash
# 查看会话目录状态
make list-sessions

# 清理问题目录
make clean-sessions

# 检查服务日志
tail -f app.log | grep -E "(会话|目录)"
```

---

## [1.0.0] - 2024-01-01

### 初始发布 🎉

#### 核心功能
- Amazon Q CLI集成
- RESTful API接口
- 流式回复支持
- 会话管理
- 上下文保持
- 健康监控

#### API端点
- `POST /api/v1/chat` - 标准聊天
- `POST /api/v1/chat/stream` - 流式聊天
- `POST /api/v1/sessions` - 创建会话
- `GET /api/v1/sessions/{id}` - 获取会话信息
- `DELETE /api/v1/sessions/{id}` - 删除会话
- `GET /health` - 健康检查

#### 安全特性
- 输入验证和清理
- 错误信息脱敏
- 请求参数验证
- 恶意内容检测

#### 部署支持
- Docker容器化
- systemd服务配置
- EC2自动部署脚本
- 环境变量配置

#### 测试覆盖
- 单元测试
- 集成测试
- 覆盖率报告
- 自动化测试流程