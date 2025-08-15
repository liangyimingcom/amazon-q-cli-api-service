# API接口测试矩阵

## 测试目标
验证所有RESTful API接口的正确性，包括请求格式、响应格式、状态码和错误处理。

## 测试环境
- 服务地址: http://localhost:8080
- 测试工具: pytest, requests, postman
- 认证方式: 无需认证（当前版本）

## 1. 服务信息接口

### 1.1 GET / - 服务基本信息
| 测试用例ID | 测试描述 | 请求方法 | 请求路径 | 预期状态码 | 预期响应字段 | 优先级 |
|-----------|---------|---------|---------|-----------|-------------|--------|
| API001 | 获取服务信息 | GET | / | 200 | service, version, status, endpoints | 高 |
| API002 | 响应格式验证 | GET | / | 200 | JSON格式，包含所有必需字段 | 高 |

### 1.2 GET /health - 健康检查
| 测试用例ID | 测试描述 | 请求方法 | 请求路径 | 预期状态码 | 预期响应字段 | 优先级 |
|-----------|---------|---------|---------|-----------|-------------|--------|
| API003 | 健康状态检查 | GET | /health | 200 | status, timestamp, qcli_available | 高 |
| API004 | 活跃会话统计 | GET | /health | 200 | active_sessions字段为数字 | 中 |
| API005 | Q CLI状态检查 | GET | /health | 200 | qcli_available为布尔值 | 高 |

## 2. 会话管理接口

### 2.1 POST /api/v1/sessions - 创建会话
| 测试用例ID | 测试描述 | 请求体 | 预期状态码 | 预期响应 | 优先级 |
|-----------|---------|--------|-----------|---------|--------|
| API006 | 创建新会话 | {} | 200 | session_id, created_at | 高 |
| API007 | 会话ID格式验证 | {} | 200 | session_id为UUID格式 | 高 |
| API008 | 创建时间验证 | {} | 200 | created_at为时间戳 | 中 |### 
2.2 GET /api/v1/sessions/{session_id} - 获取会话信息
| 测试用例ID | 测试描述 | 请求路径 | 预期状态码 | 预期响应 | 优先级 |
|-----------|---------|---------|-----------|---------|--------|
| API009 | 获取存在的会话 | /api/v1/sessions/{valid_id} | 200 | 完整会话信息 | 高 |
| API010 | 获取不存在的会话 | /api/v1/sessions/{invalid_id} | 404 | 错误信息 | 高 |
| API011 | 无效会话ID格式 | /api/v1/sessions/invalid | 400 | 格式错误信息 | 中 |
| API012 | 会话信息完整性 | /api/v1/sessions/{valid_id} | 200 | 包含work_directory等字段 | 高 |

### 2.3 DELETE /api/v1/sessions/{session_id} - 删除会话
| 测试用例ID | 测试描述 | 请求路径 | 预期状态码 | 预期响应 | 优先级 |
|-----------|---------|---------|-----------|---------|--------|
| API013 | 删除存在的会话 | /api/v1/sessions/{valid_id} | 200 | 删除成功消息 | 高 |
| API014 | 删除不存在的会话 | /api/v1/sessions/{invalid_id} | 404 | 错误信息 | 高 |
| API015 | 删除后验证 | 删除后再次查询 | 404 | 会话不存在 | 高 |

### 2.4 GET /api/v1/sessions/{session_id}/files - 获取会话文件
| 测试用例ID | 测试描述 | 请求路径 | 预期状态码 | 预期响应 | 优先级 |
|-----------|---------|---------|-----------|---------|--------|
| API016 | 获取会话文件列表 | /api/v1/sessions/{valid_id}/files | 200 | 文件列表数组 | 高 |
| API017 | 空目录文件列表 | /api/v1/sessions/{new_id}/files | 200 | 空文件数组 | 中 |
| API018 | 不存在会话的文件 | /api/v1/sessions/{invalid_id}/files | 404 | 错误信息 | 高 |

## 3. 聊天接口

### 3.1 POST /api/v1/chat - 标准聊天
| 测试用例ID | 测试描述 | 请求体 | 预期状态码 | 预期响应 | 优先级 |
|-----------|---------|--------|-----------|---------|--------|
| API019 | 基础聊天请求 | {"message": "你好"} | 200 | session_id, message, timestamp | 高 |
| API020 | 指定会话聊天 | {"session_id": "xxx", "message": "你好"} | 200 | 相同session_id回复 | 高 |
| API021 | 空消息请求 | {"message": ""} | 400 | 错误信息 | 中 |
| API022 | 缺少message字段 | {} | 400 | 参数错误信息 | 中 |
| API023 | 超长消息请求 | {"message": "4000+字符"} | 400 | 长度限制错误 | 中 |
| API024 | 无效会话ID | {"session_id": "invalid", "message": "test"} | 404 | 会话不存在错误 | 高 |

### 3.2 POST /api/v1/chat/stream - 流式聊天
| 测试用例ID | 测试描述 | 请求体 | 预期状态码 | 预期响应类型 | 优先级 |
|-----------|---------|--------|-----------|-------------|--------|
| API025 | 基础流式聊天 | {"message": "介绍Python"} | 200 | text/event-stream | 高 |
| API026 | 流式事件格式 | {"message": "test"} | 200 | SSE格式事件流 | 高 |
| API027 | 流式完成事件 | {"message": "test"} | 200 | 最后包含done事件 | 高 |
| API028 | 流式错误处理 | 触发错误的请求 | 200 | 包含error事件 | 中 |

## 4. 请求参数验证

### 4.1 Content-Type验证
| 测试用例ID | 测试描述 | Content-Type | 预期状态码 | 优先级 |
|-----------|---------|-------------|-----------|--------|
| API029 | 正确的JSON类型 | application/json | 200 | 高 |
| API030 | 错误的内容类型 | text/plain | 400 | 中 |
| API031 | 缺少Content-Type | 无 | 400 | 中 |

### 4.2 JSON格式验证
| 测试用例ID | 测试描述 | 请求体 | 预期状态码 | 优先级 |
|-----------|---------|--------|-----------|--------|
| API032 | 有效JSON格式 | {"message": "test"} | 200 | 高 |
| API033 | 无效JSON格式 | {invalid json} | 400 | 中 |
| API034 | 空请求体 | 空 | 400 | 中 |

## 5. HTTP状态码测试

### 5.1 成功状态码
| 测试用例ID | 测试描述 | 操作 | 预期状态码 | 优先级 |
|-----------|---------|-----|-----------|--------|
| API035 | 成功获取资源 | GET有效资源 | 200 | 高 |
| API036 | 成功创建资源 | POST创建会话 | 200 | 高 |
| API037 | 成功删除资源 | DELETE会话 | 200 | 高 |

### 5.2 客户端错误状态码
| 测试用例ID | 测试描述 | 操作 | 预期状态码 | 优先级 |
|-----------|---------|-----|-----------|--------|
| API038 | 请求参数错误 | 发送无效参数 | 400 | 高 |
| API039 | 资源不存在 | 访问不存在的会话 | 404 | 高 |
| API040 | 方法不允许 | 错误的HTTP方法 | 405 | 中 |

### 5.3 服务器错误状态码
| 测试用例ID | 测试描述 | 操作 | 预期状态码 | 优先级 |
|-----------|---------|-----|-----------|--------|
| API041 | 内部服务器错误 | 触发服务器异常 | 500 | 中 |
| API042 | 服务不可用 | Q CLI不可用时 | 503 | 中 |

## 6. 响应格式验证

### 6.1 JSON响应格式
| 测试用例ID | 测试描述 | 接口 | 验证内容 | 优先级 |
|-----------|---------|-----|---------|--------|
| API043 | 响应Content-Type | 所有JSON接口 | application/json | 高 |
| API044 | 响应字符编码 | 所有接口 | UTF-8编码 | 高 |
| API045 | 错误响应格式 | 错误情况 | 包含error字段 | 高 |

### 6.2 时间戳格式
| 测试用例ID | 测试描述 | 字段 | 验证内容 | 优先级 |
|-----------|---------|-----|---------|--------|
| API046 | 创建时间格式 | created_at | Unix时间戳 | 中 |
| API047 | 响应时间格式 | timestamp | Unix时间戳 | 中 |
| API048 | 文件修改时间 | modified_time | Unix时间戳 | 中 |

## 测试脚本示例

```python
import requests
import json
import pytest

BASE_URL = "http://localhost:8080"

class TestAPIEndpoints:
    
    def test_service_info(self):
        """API001: 测试服务信息接口"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["service", "version", "status", "endpoints"]
        for field in required_fields:
            assert field in data
    
    def test_health_check(self):
        """API003: 测试健康检查接口"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "qcli_available" in data
        assert isinstance(data["qcli_available"], bool)
    
    def test_create_session(self):
        """API006: 测试创建会话"""
        response = requests.post(f"{BASE_URL}/api/v1/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "created_at" in data
        
        # 验证UUID格式
        import uuid
        uuid.UUID(data["session_id"])  # 如果不是有效UUID会抛出异常
    
    def test_chat_basic(self):
        """API019: 测试基础聊天"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": "你好"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "message" in data
        assert "timestamp" in data
    
    def test_invalid_session(self):
        """API010: 测试获取不存在的会话"""
        response = requests.get(f"{BASE_URL}/api/v1/sessions/invalid-id")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
```

## 自动化测试执行

### 测试命令
```bash
# 运行所有API测试
pytest test_matrix/scripts/api_test_suite.py -v

# 运行特定测试类别
pytest test_matrix/scripts/api_test_suite.py::TestAPIEndpoints -v

# 生成测试报告
pytest test_matrix/scripts/api_test_suite.py --html=reports/api_test_report.html
```

### 持续集成配置
```yaml
# .github/workflows/api_tests.yml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start service
        run: python app.py &
      - name: Run API tests
        run: pytest test_matrix/scripts/api_test_suite.py
```

## 测试数据管理

### 测试数据文件
- `test_messages.json`: 各种类型的测试消息
- `invalid_requests.json`: 无效请求示例
- `expected_responses.json`: 预期响应格式

### 测试环境清理
```python
def cleanup_test_sessions():
    """清理测试过程中创建的会话"""
    # 获取所有会话并删除测试会话
    pass
```

## 成功标准

- 所有高优先级API测试通过率 ≥ 98%
- 所有中优先级API测试通过率 ≥ 95%
- 响应时间 < 2秒（非流式接口）
- 错误处理覆盖率 100%
- API文档与实际实现一致性 100%