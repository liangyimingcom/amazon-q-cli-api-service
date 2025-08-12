"""
错误处理工具 - 核心版本

提供统一的错误处理和日志记录功能。
"""

import logging
import traceback
from typing import Dict, Any, Optional
from qcli_api_service.models.core import ErrorResponse


logger = logging.getLogger(__name__)


class ErrorHandler:
    """错误处理器"""
    
    @staticmethod
    def handle_qcli_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """
        处理Q CLI相关错误
        
        参数:
            error: 异常对象
            context: 错误上下文信息
            
        返回:
            错误响应对象
        """
        error_msg = f"AI处理失败: {str(error)}"
        
        # 记录错误日志
        ErrorHandler.log_error(error, context, "Q CLI错误")
        
        return ErrorResponse(
            error=error_msg,
            code=503,
            details="请检查Amazon Q CLI是否正常工作"
        )
    
    @staticmethod
    def handle_session_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """
        处理会话相关错误
        
        参数:
            error: 异常对象
            context: 错误上下文信息
            
        返回:
            错误响应对象
        """
        error_msg = f"会话处理失败: {str(error)}"
        
        # 记录错误日志
        ErrorHandler.log_error(error, context, "会话错误")
        
        return ErrorResponse(
            error=error_msg,
            code=500,
            details="会话管理出现问题"
        )
    
    @staticmethod
    def handle_validation_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """
        处理验证错误
        
        参数:
            error: 异常对象
            context: 错误上下文信息
            
        返回:
            错误响应对象
        """
        error_msg = str(error)
        
        # 记录警告日志（验证错误通常不是系统错误）
        logger.warning(f"验证错误: {error_msg}, 上下文: {context}")
        
        return ErrorResponse(
            error=error_msg,
            code=400,
            details="请检查请求参数格式"
        )
    
    @staticmethod
    def handle_generic_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> ErrorResponse:
        """
        处理通用错误
        
        参数:
            error: 异常对象
            context: 错误上下文信息
            
        返回:
            错误响应对象
        """
        error_msg = "内部服务器错误"
        
        # 记录错误日志
        ErrorHandler.log_error(error, context, "通用错误")
        
        return ErrorResponse(
            error=error_msg,
            code=500,
            details="服务器处理请求时发生错误"
        )
    
    @staticmethod
    def log_error(error: Exception, context: Optional[Dict[str, Any]] = None, error_type: str = "未知错误") -> None:
        """
        记录错误日志
        
        参数:
            error: 异常对象
            context: 错误上下文信息
            error_type: 错误类型
        """
        try:
            # 构建日志消息
            log_data = {
                "error_type": error_type,
                "error_message": str(error),
                "error_class": error.__class__.__name__,
                "traceback": traceback.format_exc(),
            }
            
            if context:
                log_data["context"] = context
            
            # 记录错误日志
            logger.error(f"错误详情: {log_data}")
            
        except Exception as log_error:
            # 如果日志记录本身出错，使用简单的日志记录
            logger.error(f"日志记录失败: {log_error}, 原始错误: {error}")
    
    @staticmethod
    def sanitize_error_message(message: str) -> str:
        """
        清理错误消息，移除敏感信息
        
        参数:
            message: 原始错误消息
            
        返回:
            清理后的错误消息
        """
        # 移除可能的敏感信息
        sensitive_patterns = [
            r'password[=:]\s*\S+',
            r'token[=:]\s*\S+',
            r'key[=:]\s*\S+',
            r'secret[=:]\s*\S+',
        ]
        
        import re
        cleaned_message = message
        for pattern in sensitive_patterns:
            cleaned_message = re.sub(pattern, '[REDACTED]', cleaned_message, flags=re.IGNORECASE)
        
        return cleaned_message
    
    @staticmethod
    def create_error_context(request_data: Optional[Dict[str, Any]] = None, 
                           session_id: Optional[str] = None,
                           user_message: Optional[str] = None) -> Dict[str, Any]:
        """
        创建错误上下文信息
        
        参数:
            request_data: 请求数据
            session_id: 会话ID
            user_message: 用户消息
            
        返回:
            错误上下文字典
        """
        context = {}
        
        if session_id:
            context["session_id"] = session_id
        
        if user_message:
            # 只记录消息长度，不记录具体内容（隐私保护）
            context["message_length"] = len(user_message)
        
        if request_data:
            # 只记录请求的基本信息，不记录敏感数据
            safe_data = {}
            for key, value in request_data.items():
                if key.lower() not in ['password', 'token', 'key', 'secret']:
                    if isinstance(value, str) and len(value) > 100:
                        safe_data[key] = f"{value[:50]}...[truncated]"
                    else:
                        safe_data[key] = value
            context["request_data"] = safe_data
        
        return context


# 全局错误处理器实例
error_handler = ErrorHandler()