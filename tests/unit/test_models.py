"""
数据模型单元测试
"""

import time
import pytest
from qcli_api_service.models.core import Message, Session, ChatRequest, ChatResponse, ErrorResponse


class TestMessage:
    """消息模型测试"""
    
    def test_create_user_message(self):
        """测试创建用户消息"""
        content = "你好"
        message = Message.create_user_message(content)
        
        assert message.role == "user"
        assert message.content == content
        assert isinstance(message.timestamp, float)
        assert message.timestamp > 0
    
    def test_create_assistant_message(self):
        """测试创建助手消息"""
        content = "你好！我是AI助手"
        message = Message.create_assistant_message(content)
        
        assert message.role == "assistant"
        assert message.content == content
        assert isinstance(message.timestamp, float)
        assert message.timestamp > 0


class TestSession:
    """会话模型测试"""
    
    def test_create_new_session(self):
        """测试创建新会话"""
        session = Session.create_new()
        
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert isinstance(session.created_at, float)
        assert isinstance(session.last_activity, float)
        assert session.messages == []
    
    def test_add_message(self):
        """测试添加消息"""
        session = Session.create_new()
        message = Message.create_user_message("测试消息")
        
        original_activity = session.last_activity
        time.sleep(0.01)  # 确保时间戳不同
        
        session.add_message(message)
        
        assert len(session.messages) == 1
        assert session.messages[0] == message
        assert session.last_activity > original_activity
    
    def test_get_context_empty(self):
        """测试获取空会话上下文"""
        session = Session.create_new()
        context = session.get_context()
        
        assert context == ""
    
    def test_get_context_with_messages(self):
        """测试获取有消息的会话上下文"""
        session = Session.create_new()
        
        user_msg = Message.create_user_message("你好")
        assistant_msg = Message.create_assistant_message("你好！")
        
        session.add_message(user_msg)
        session.add_message(assistant_msg)
        
        context = session.get_context()
        
        assert "用户: 你好" in context
        assert "助手: 你好！" in context
    
    def test_get_context_max_messages(self):
        """测试获取上下文时的消息数量限制"""
        session = Session.create_new()
        
        # 添加多条消息
        for i in range(15):
            session.add_message(Message.create_user_message(f"消息{i}"))
        
        context = session.get_context(max_messages=5)
        lines = context.split('\n')
        
        assert len(lines) == 5
        assert "消息14" in context  # 应该包含最后的消息
    
    def test_is_expired(self):
        """测试会话过期检查"""
        session = Session.create_new()
        
        # 新会话不应该过期
        assert not session.is_expired(3600)
        
        # 修改最后活动时间为过去
        session.last_activity = time.time() - 7200  # 2小时前
        
        # 现在应该过期
        assert session.is_expired(3600)


class TestChatRequest:
    """聊天请求模型测试"""
    
    def test_valid_request(self):
        """测试有效请求"""
        request = ChatRequest(
            session_id="test-session",
            message="你好",
            stream=False
        )
        
        # 不应该抛出异常
        request.validate()
    
    def test_empty_message(self):
        """测试空消息验证"""
        request = ChatRequest(
            session_id="test-session",
            message="",
            stream=False
        )
        
        with pytest.raises(ValueError, match="消息内容不能为空"):
            request.validate()
    
    def test_whitespace_only_message(self):
        """测试只有空白字符的消息"""
        request = ChatRequest(
            session_id="test-session",
            message="   \n\t  ",
            stream=False
        )
        
        with pytest.raises(ValueError, match="消息内容不能为空"):
            request.validate()
    
    def test_too_long_message(self):
        """测试过长消息验证"""
        long_message = "a" * 4001  # 超过4000字符限制
        request = ChatRequest(
            session_id="test-session",
            message=long_message,
            stream=False
        )
        
        with pytest.raises(ValueError, match="消息内容过长"):
            request.validate()


class TestChatResponse:
    """聊天响应模型测试"""
    
    def test_create_response(self):
        """测试创建响应"""
        session_id = "test-session"
        message = "这是回复"
        
        response = ChatResponse.create(session_id, message)
        
        assert response.session_id == session_id
        assert response.message == message
        assert isinstance(response.timestamp, float)
        assert response.timestamp > 0


class TestErrorResponse:
    """错误响应模型测试"""
    
    def test_error_response_basic(self):
        """测试基本错误响应"""
        error = ErrorResponse(
            error="测试错误",
            code=400
        )
        
        result = error.to_dict()
        
        assert result["error"] == "测试错误"
        assert result["code"] == 400
        assert "details" not in result
    
    def test_error_response_with_details(self):
        """测试带详情的错误响应"""
        error = ErrorResponse(
            error="测试错误",
            code=400,
            details="详细错误信息"
        )
        
        result = error.to_dict()
        
        assert result["error"] == "测试错误"
        assert result["code"] == 400
        assert result["details"] == "详细错误信息"