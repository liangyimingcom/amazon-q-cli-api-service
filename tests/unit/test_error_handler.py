"""
错误处理器单元测试
"""

import pytest
from unittest.mock import patch
from qcli_api_service.utils.error_handler import ErrorHandler
from qcli_api_service.models.core import ErrorResponse


class TestErrorHandler:
    """错误处理器测试"""
    
    def test_handle_qcli_error(self):
        """测试Q CLI错误处理"""
        error = RuntimeError("Q CLI连接失败")
        context = {"session_id": "test-session"}
        
        with patch.object(ErrorHandler, 'log_error') as mock_log:
            result = ErrorHandler.handle_qcli_error(error, context)
        
        assert isinstance(result, ErrorResponse)
        assert result.code == 503
        assert "AI处理失败" in result.error
        assert "Q CLI连接失败" in result.error
        assert result.details == "请检查Amazon Q CLI是否正常工作"
        
        mock_log.assert_called_once_with(error, context, "Q CLI错误")
    
    def test_handle_session_error(self):
        """测试会话错误处理"""
        error = ValueError("会话不存在")
        context = {"session_id": "invalid-session"}
        
        with patch.object(ErrorHandler, 'log_error') as mock_log:
            result = ErrorHandler.handle_session_error(error, context)
        
        assert isinstance(result, ErrorResponse)
        assert result.code == 500
        assert "会话处理失败" in result.error
        assert "会话不存在" in result.error
        assert result.details == "会话管理出现问题"
        
        mock_log.assert_called_once_with(error, context, "会话错误")
    
    def test_handle_validation_error(self):
        """测试验证错误处理"""
        error = ValueError("消息内容不能为空")
        context = {"request_data": {"message": ""}}
        
        with patch('qcli_api_service.utils.error_handler.logger') as mock_logger:
            result = ErrorHandler.handle_validation_error(error, context)
        
        assert isinstance(result, ErrorResponse)
        assert result.code == 400
        assert result.error == "消息内容不能为空"
        assert result.details == "请检查请求参数格式"
        
        mock_logger.warning.assert_called_once()
    
    def test_handle_generic_error(self):
        """测试通用错误处理"""
        error = Exception("未知错误")
        context = {"operation": "test"}
        
        with patch.object(ErrorHandler, 'log_error') as mock_log:
            result = ErrorHandler.handle_generic_error(error, context)
        
        assert isinstance(result, ErrorResponse)
        assert result.code == 500
        assert result.error == "内部服务器错误"
        assert result.details == "服务器处理请求时发生错误"
        
        mock_log.assert_called_once_with(error, context, "通用错误")
    
    def test_sanitize_error_message(self):
        """测试错误消息清理"""
        # 测试包含敏感信息的消息
        message_with_password = "连接失败: password=secret123"
        cleaned = ErrorHandler.sanitize_error_message(message_with_password)
        assert "secret123" not in cleaned
        assert "[REDACTED]" in cleaned
        
        # 测试包含token的消息
        message_with_token = "认证失败: token=abc123xyz"
        cleaned = ErrorHandler.sanitize_error_message(message_with_token)
        assert "abc123xyz" not in cleaned
        assert "[REDACTED]" in cleaned
        
        # 测试正常消息
        normal_message = "连接超时"
        cleaned = ErrorHandler.sanitize_error_message(normal_message)
        assert cleaned == normal_message
    
    def test_create_error_context(self):
        """测试创建错误上下文"""
        request_data = {
            "message": "测试消息",
            "session_id": "test-session",
            "password": "secret"  # 应该被过滤
        }
        session_id = "test-session"
        user_message = "这是一个测试消息"
        
        context = ErrorHandler.create_error_context(
            request_data=request_data,
            session_id=session_id,
            user_message=user_message
        )
        
        assert context["session_id"] == session_id
        assert context["message_length"] == len(user_message)
        assert "request_data" in context
        assert "password" not in context["request_data"]  # 敏感信息被过滤
        assert context["request_data"]["message"] == "测试消息"
    
    def test_create_error_context_long_message(self):
        """测试长消息的上下文创建"""
        long_message = "a" * 200
        request_data = {"message": long_message}
        
        context = ErrorHandler.create_error_context(request_data=request_data)
        
        # 长消息应该被截断
        assert "[truncated]" in context["request_data"]["message"]
        assert len(context["request_data"]["message"]) < len(long_message)
    
    @patch('qcli_api_service.utils.error_handler.logger')
    def test_log_error(self, mock_logger):
        """测试错误日志记录"""
        error = ValueError("测试错误")
        context = {"test": "context"}
        error_type = "测试错误类型"
        
        ErrorHandler.log_error(error, context, error_type)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "测试错误类型" in call_args
        assert "测试错误" in call_args
    
    @patch('qcli_api_service.utils.error_handler.logger')
    def test_log_error_exception(self, mock_logger):
        """测试日志记录异常处理"""
        error = ValueError("测试错误")
        
        # 模拟日志记录失败
        mock_logger.error.side_effect = [Exception("日志失败"), None]
        
        # 不应该抛出异常
        ErrorHandler.log_error(error, None, "测试")
        
        # 应该调用两次logger.error（第一次失败，第二次记录失败信息）
        assert mock_logger.error.call_count == 2