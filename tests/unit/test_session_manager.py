"""
会话管理器单元测试
"""

import time
import pytest
from qcli_api_service.services.session_manager import SessionManager
from qcli_api_service.models.core import Message


class TestSessionManager:
    """会话管理器测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.manager = SessionManager()
    
    def test_create_session(self):
        """测试创建会话"""
        session = self.manager.create_session()
        
        assert session.session_id is not None
        assert len(session.session_id) > 0
        assert session.messages == []
        
        # 验证会话已存储
        retrieved = self.manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
    
    def test_get_nonexistent_session(self):
        """测试获取不存在的会话"""
        result = self.manager.get_session("nonexistent-id")
        assert result is None
    
    def test_delete_session(self):
        """测试删除会话"""
        session = self.manager.create_session()
        session_id = session.session_id
        
        # 确认会话存在
        assert self.manager.get_session(session_id) is not None
        
        # 删除会话
        result = self.manager.delete_session(session_id)
        assert result is True
        
        # 确认会话已删除
        assert self.manager.get_session(session_id) is None
    
    def test_delete_nonexistent_session(self):
        """测试删除不存在的会话"""
        result = self.manager.delete_session("nonexistent-id")
        assert result is False
    
    def test_add_message(self):
        """测试添加消息"""
        session = self.manager.create_session()
        message = Message.create_user_message("测试消息")
        
        result = self.manager.add_message(session.session_id, message)
        assert result is True
        
        # 验证消息已添加
        messages = self.manager.get_conversation_history(session.session_id)
        assert len(messages) == 1
        assert messages[0].content == "测试消息"
    
    def test_add_message_to_nonexistent_session(self):
        """测试向不存在的会话添加消息"""
        message = Message.create_user_message("测试消息")
        result = self.manager.add_message("nonexistent-id", message)
        assert result is False
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        session = self.manager.create_session()
        
        # 添加多条消息
        msg1 = Message.create_user_message("消息1")
        msg2 = Message.create_assistant_message("回复1")
        msg3 = Message.create_user_message("消息2")
        
        self.manager.add_message(session.session_id, msg1)
        self.manager.add_message(session.session_id, msg2)
        self.manager.add_message(session.session_id, msg3)
        
        history = self.manager.get_conversation_history(session.session_id)
        
        assert len(history) == 3
        assert history[0].content == "消息1"
        assert history[1].content == "回复1"
        assert history[2].content == "消息2"
    
    def test_get_conversation_history_nonexistent_session(self):
        """测试获取不存在会话的对话历史"""
        history = self.manager.get_conversation_history("nonexistent-id")
        assert history == []
    
    def test_get_context(self):
        """测试获取对话上下文"""
        session = self.manager.create_session()
        
        # 添加消息
        msg1 = Message.create_user_message("你好")
        msg2 = Message.create_assistant_message("你好！")
        
        self.manager.add_message(session.session_id, msg1)
        self.manager.add_message(session.session_id, msg2)
        
        context = self.manager.get_context(session.session_id)
        
        assert "用户: 你好" in context
        assert "助手: 你好！" in context
    
    def test_get_context_nonexistent_session(self):
        """测试获取不存在会话的上下文"""
        context = self.manager.get_context("nonexistent-id")
        assert context == ""
    
    def test_message_limit(self):
        """测试消息数量限制"""
        # 临时修改配置进行测试
        from qcli_api_service.config import config
        original_limit = config.MAX_HISTORY_LENGTH
        config.MAX_HISTORY_LENGTH = 3
        
        try:
            session = self.manager.create_session()
            
            # 添加超过限制的消息
            for i in range(5):
                msg = Message.create_user_message(f"消息{i}")
                self.manager.add_message(session.session_id, msg)
            
            # 验证只保留最近的消息
            history = self.manager.get_conversation_history(session.session_id)
            assert len(history) == 3
            assert history[0].content == "消息2"  # 最早保留的消息
            assert history[2].content == "消息4"  # 最新的消息
            
        finally:
            # 恢复原始配置
            config.MAX_HISTORY_LENGTH = original_limit
    
    def test_cleanup_expired_sessions(self):
        """测试清理过期会话"""
        # 创建会话
        session1 = self.manager.create_session()
        session2 = self.manager.create_session()
        
        # 模拟一个会话过期
        session1.last_activity = time.time() - 7200  # 2小时前
        
        # 清理过期会话
        cleaned_count = self.manager.cleanup_expired_sessions()
        
        assert cleaned_count == 1
        assert self.manager.get_session(session1.session_id) is None
        assert self.manager.get_session(session2.session_id) is not None
    
    def test_get_active_session_count(self):
        """测试获取活跃会话数量"""
        assert self.manager.get_active_session_count() == 0
        
        session1 = self.manager.create_session()
        assert self.manager.get_active_session_count() == 1
        
        session2 = self.manager.create_session()
        assert self.manager.get_active_session_count() == 2
        
        self.manager.delete_session(session1.session_id)
        assert self.manager.get_active_session_count() == 1
    
    def test_get_session_info(self):
        """测试获取会话信息"""
        session = self.manager.create_session()
        
        # 添加一条消息
        msg = Message.create_user_message("测试")
        self.manager.add_message(session.session_id, msg)
        
        info = self.manager.get_session_info(session.session_id)
        
        assert info is not None
        assert info["session_id"] == session.session_id
        assert info["message_count"] == 1
        assert "created_at" in info
        assert "last_activity" in info
    
    def test_get_session_info_nonexistent(self):
        """测试获取不存在会话的信息"""
        info = self.manager.get_session_info("nonexistent-id")
        assert info is None