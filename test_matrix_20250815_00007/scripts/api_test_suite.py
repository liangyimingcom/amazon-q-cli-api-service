#!/usr/bin/env python3
"""
API接口测试套件

实现API接口测试矩阵中定义的所有测试用例
"""

import pytest
import requests
import json
import uuid
import time
from datetime import datetime

BASE_URL = "http://localhost:8080"

class TestServiceInfo:
    """服务信息接口测试"""
    
    def test_service_info_basic(self):
        """API001: 获取服务信息"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["service", "version", "status", "endpoints"]
        for field in required_fields:
            assert field in data, f"缺少必需字段: {field}"
        
        # 验证字段类型
        assert isinstance(data["service"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["status"], str)
        assert isinstance(data["endpoints"], dict)
    
    def test_service_info_response_format(self):
        """API002: 响应格式验证"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        
        # 验证Content-Type
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type
        
        # 验证JSON格式
        data = response.json()
        assert data is not None
        
        # 验证endpoints字段包含预期的接口
        endpoints = data["endpoints"]
        expected_endpoints = ["chat", "stream_chat", "sessions", "health"]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints

class TestHealthCheck:
    """健康检查接口测试"""
    
    def test_health_check_basic(self):
        """API003: 健康状态检查"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["status", "timestamp", "qcli_available"]
        for field in required_fields:
            assert field in data, f"缺少必需字段: {field}"
        
        # 验证状态值
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_health_active_sessions(self):
        """API004: 活跃会话统计"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_sessions" in data
        assert isinstance(data["active_sessions"], int)
        assert data["active_sessions"] >= 0
    
    def test_health_qcli_status(self):
        """API005: Q CLI状态检查"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "qcli_available" in data
        assert isinstance(data["qcli_available"], bool)

class TestSessionManagement:
    """会话管理接口测试"""
    
    def test_create_session(self):
        """API006: 创建新会话"""
        response = requests.post(f"{BASE_URL}/api/v1/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "created_at" in data
        
        # 验证时间戳
        assert isinstance(data["created_at"], (int, float))
        assert data["created_at"] > 0
    
    def test_session_id_format(self):
        """API007: 会话ID格式验证"""
        response = requests.post(f"{BASE_URL}/api/v1/sessions")
        assert response.status_code == 200
        
        data = response.json()
        session_id = data["session_id"]
        
        # 验证UUID格式
        try:
            uuid.UUID(session_id)
        except ValueError:
            pytest.fail(f"会话ID不是有效的UUID格式: {session_id}")
    
    def test_get_existing_session(self):
        """API009: 获取存在的会话"""
        # 先创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 获取会话信息
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "created_at" in data
        assert "work_directory" in data
    
    def test_get_nonexistent_session(self):
        """API010: 获取不存在的会话"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{fake_id}")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
    
    def test_invalid_session_id_format(self):
        """API011: 无效会话ID格式"""
        response = requests.get(f"{BASE_URL}/api/v1/sessions/invalid-id")
        assert response.status_code in [400, 404]  # 可能返回400或404
        
        data = response.json()
        assert "error" in data
    
    def test_session_info_completeness(self):
        """API012: 会话信息完整性"""
        # 创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 获取会话信息
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "session_id", "created_at", "work_directory", 
            "absolute_work_directory"
        ]
        for field in required_fields:
            assert field in data, f"缺少必需字段: {field}"
    
    def test_delete_existing_session(self):
        """API013: 删除存在的会话"""
        # 创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 删除会话
        response = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data or "success" in data
    
    def test_delete_nonexistent_session(self):
        """API014: 删除不存在的会话"""
        fake_id = str(uuid.uuid4())
        response = requests.delete(f"{BASE_URL}/api/v1/sessions/{fake_id}")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
    
    def test_delete_verification(self):
        """API015: 删除后验证"""
        # 创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 删除会话
        delete_response = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}")
        assert delete_response.status_code == 200
        
        # 验证会话不存在
        get_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}")
        assert get_response.status_code == 404

class TestSessionFiles:
    """会话文件接口测试"""
    
    def test_get_session_files(self):
        """API016: 获取会话文件列表"""
        # 创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 获取文件列表
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/files")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = [
            "session_id", "work_directory", "files", "file_count"
        ]
        for field in required_fields:
            assert field in data, f"缺少必需字段: {field}"
        
        assert isinstance(data["files"], list)
        assert isinstance(data["file_count"], int)
    
    def test_empty_directory_files(self):
        """API017: 空目录文件列表"""
        # 创建新会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 获取文件列表（应该为空）
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}/files")
        assert response.status_code == 200
        
        data = response.json()
        assert data["file_count"] == 0
        assert len(data["files"]) == 0
    
    def test_nonexistent_session_files(self):
        """API018: 不存在会话的文件"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{fake_id}/files")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data

class TestChatInterface:
    """聊天接口测试"""
    
    def test_basic_chat(self):
        """API019: 基础聊天请求"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": "你好"}
        )
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["session_id", "message", "timestamp"]
        for field in required_fields:
            assert field in data, f"缺少必需字段: {field}"
        
        # 验证响应内容
        assert isinstance(data["message"], str)
        assert len(data["message"]) > 0
        assert isinstance(data["timestamp"], (int, float))
    
    def test_chat_with_session(self):
        """API020: 指定会话聊天"""
        # 创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 在指定会话中聊天
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"session_id": session_id, "message": "你好"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
    
    def test_empty_message(self):
        """API021: 空消息请求"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": ""}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    def test_missing_message_field(self):
        """API022: 缺少message字段"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    def test_long_message(self):
        """API023: 超长消息请求"""
        long_message = "x" * 5000  # 5000字符的消息
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": long_message}
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
    
    def test_invalid_session_chat(self):
        """API024: 无效会话ID"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"session_id": "invalid-id", "message": "test"}
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data

class TestStreamingChat:
    """流式聊天接口测试"""
    
    def test_basic_streaming(self):
        """API025: 基础流式聊天"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/stream",
            json={"message": "介绍Python"},
            stream=True
        )
        assert response.status_code == 200
        
        # 验证Content-Type
        content_type = response.headers.get("content-type", "")
        assert "text/event-stream" in content_type
    
    def test_streaming_event_format(self):
        """API026: 流式事件格式"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/stream",
            json={"message": "test"},
            stream=True
        )
        assert response.status_code == 200
        
        # 读取前几行验证SSE格式
        lines = []
        for line in response.iter_lines(decode_unicode=True):
            lines.append(line)
            if len(lines) >= 10:  # 只读取前10行
                break
        
        # 验证SSE格式
        data_lines = [line for line in lines if line.startswith("data:")]
        assert len(data_lines) > 0, "没有找到data:行"
        
        # 验证JSON格式
        for data_line in data_lines[:3]:  # 检查前3个data行
            json_str = data_line[5:].strip()  # 移除"data:"前缀
            if json_str:
                try:
                    json.loads(json_str)
                except json.JSONDecodeError:
                    pytest.fail(f"无效的JSON格式: {json_str}")

class TestRequestValidation:
    """请求参数验证测试"""
    
    def test_correct_content_type(self):
        """API029: 正确的JSON类型"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            headers={"Content-Type": "application/json"},
            json={"message": "test"}
        )
        assert response.status_code == 200
    
    def test_wrong_content_type(self):
        """API030: 错误的内容类型"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            headers={"Content-Type": "text/plain"},
            data="test"
        )
        assert response.status_code == 400
    
    def test_valid_json_format(self):
        """API032: 有效JSON格式"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": "test"}
        )
        assert response.status_code == 200
    
    def test_invalid_json_format(self):
        """API033: 无效JSON格式"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            headers={"Content-Type": "application/json"},
            data="{invalid json}"
        )
        assert response.status_code == 400

class TestHTTPStatusCodes:
    """HTTP状态码测试"""
    
    def test_successful_get(self):
        """API035: 成功获取资源"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
    
    def test_successful_post(self):
        """API036: 成功创建资源"""
        response = requests.post(f"{BASE_URL}/api/v1/sessions")
        assert response.status_code == 200
    
    def test_successful_delete(self):
        """API037: 成功删除资源"""
        # 先创建会话
        create_response = requests.post(f"{BASE_URL}/api/v1/sessions")
        session_id = create_response.json()["session_id"]
        
        # 删除会话
        response = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}")
        assert response.status_code == 200
    
    def test_bad_request(self):
        """API038: 请求参数错误"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"invalid": "parameter"}
        )
        assert response.status_code == 400
    
    def test_not_found(self):
        """API039: 资源不存在"""
        fake_id = str(uuid.uuid4())
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{fake_id}")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """API040: 方法不允许"""
        response = requests.put(f"{BASE_URL}/api/v1/sessions")
        assert response.status_code == 405

class TestResponseFormat:
    """响应格式验证测试"""
    
    def test_json_content_type(self):
        """API043: 响应Content-Type"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type
    
    def test_utf8_encoding(self):
        """API044: 响应字符编码"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": "测试中文字符"}
        )
        assert response.status_code == 200
        
        # 验证能正确处理中文
        data = response.json()
        assert isinstance(data["message"], str)
        
        # 验证编码
        content_type = response.headers.get("content-type", "")
        assert "utf-8" in content_type.lower() or "charset" not in content_type.lower()
    
    def test_error_response_format(self):
        """API045: 错误响应格式"""
        response = requests.get(f"{BASE_URL}/api/v1/sessions/invalid")
        assert response.status_code in [400, 404]
        
        data = response.json()
        assert "error" in data
        assert isinstance(data["error"], str)

class TestTimestampFormat:
    """时间戳格式测试"""
    
    def test_created_at_format(self):
        """API046: 创建时间格式"""
        response = requests.post(f"{BASE_URL}/api/v1/sessions")
        assert response.status_code == 200
        
        data = response.json()
        created_at = data["created_at"]
        
        # 验证是数字类型的时间戳
        assert isinstance(created_at, (int, float))
        assert created_at > 0
        
        # 验证时间戳合理性（应该是最近的时间）
        current_time = time.time()
        assert abs(current_time - created_at) < 60  # 差异应小于60秒
    
    def test_response_timestamp_format(self):
        """API047: 响应时间格式"""
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json={"message": "test"}
        )
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # 验证时间戳格式
        assert isinstance(timestamp, (int, float))
        assert timestamp > 0
        
        # 验证时间戳合理性
        current_time = time.time()
        assert abs(current_time - timestamp) < 60

# 测试夹具和工具函数
@pytest.fixture(scope="session")
def service_health_check():
    """会话级别的服务健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            pytest.skip(f"服务不健康: HTTP {response.status_code}")
    except requests.RequestException as e:
        pytest.skip(f"无法连接到服务: {e}")

@pytest.fixture
def clean_session():
    """创建一个测试会话，测试完成后自动清理"""
    # 创建会话
    response = requests.post(f"{BASE_URL}/api/v1/sessions")
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        yield session_id
        
        # 清理会话
        try:
            requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}")
        except:
            pass  # 忽略清理错误
    else:
        pytest.skip("无法创建测试会话")

# 使用服务健康检查夹具
pytestmark = pytest.mark.usefixtures("service_health_check")