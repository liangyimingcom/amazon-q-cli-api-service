"""
输入验证工具 - 核心版本

提供请求参数验证和清理功能。
"""

import re
import uuid
from typing import Any, Dict, Optional


class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        验证会话ID格式
        
        参数:
            session_id: 会话ID
            
        返回:
            是否有效
        """
        if not session_id or not isinstance(session_id, str):
            return False
        
        try:
            # 验证是否为有效的UUID格式
            uuid.UUID(session_id)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_message(message: str) -> tuple[bool, Optional[str]]:
        """
        验证消息内容
        
        参数:
            message: 消息内容
            
        返回:
            (是否有效, 错误信息)
        """
        if not message or not isinstance(message, str):
            return False, "消息内容不能为空"
        
        # 去除首尾空白后检查
        cleaned_message = message.strip()
        if not cleaned_message:
            return False, "消息内容不能为空"
        
        # 检查长度限制
        if len(cleaned_message) > 4000:
            return False, "消息内容过长，最大4000字符"
        
        # 检查是否包含恶意内容（基本检查）
        if InputValidator._contains_malicious_content(cleaned_message):
            return False, "消息内容包含不允许的字符"
        
        return True, None
    
    @staticmethod
    def validate_request_data(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证请求数据
        
        参数:
            data: 请求数据字典
            
        返回:
            (是否有效, 错误信息)
        """
        if not isinstance(data, dict):
            return False, "请求数据格式错误"
        
        # 检查必需字段
        if 'message' not in data:
            return False, "缺少必需字段: message"
        
        # 验证消息内容
        message_valid, message_error = InputValidator.validate_message(data['message'])
        if not message_valid:
            return False, message_error
        
        # 验证会话ID（如果提供）
        if 'session_id' in data and data['session_id']:
            if not InputValidator.validate_session_id(data['session_id']):
                return False, "会话ID格式无效"
        
        # 验证流式标志
        if 'stream' in data:
            if not isinstance(data['stream'], bool):
                return False, "stream字段必须为布尔值"
        
        return True, None
    
    @staticmethod
    def clean_message(message: str) -> str:
        """
        清理消息内容
        
        参数:
            message: 原始消息
            
        返回:
            清理后的消息
        """
        if not message:
            return ""
        
        # 去除首尾空白
        cleaned = message.strip()
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 移除潜在的控制字符（保留换行符和制表符）
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def _contains_malicious_content(message: str) -> bool:
        """
        检查是否包含恶意内容
        
        参数:
            message: 消息内容
            
        返回:
            是否包含恶意内容
        """
        # 基本的恶意内容检查
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # JavaScript
            r'javascript:',  # JavaScript协议
            r'on\w+\s*=',  # 事件处理器
            r'<iframe[^>]*>',  # iframe标签
            r'<object[^>]*>',  # object标签
            r'<embed[^>]*>',  # embed标签
        ]
        
        message_lower = message.lower()
        for pattern in malicious_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        return False
    
    @staticmethod
    def sanitize_for_logging(data: Any) -> Any:
        """
        为日志记录清理数据
        
        参数:
            data: 要清理的数据
            
        返回:
            清理后的数据
        """
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in ['password', 'token', 'key', 'secret', 'auth']:
                    sanitized[key] = '[REDACTED]'
                elif isinstance(value, str) and len(value) > 200:
                    sanitized[key] = f"{value[:100]}...[truncated]"
                else:
                    sanitized[key] = InputValidator.sanitize_for_logging(value)
            return sanitized
        elif isinstance(data, list):
            return [InputValidator.sanitize_for_logging(item) for item in data]
        elif isinstance(data, str) and len(data) > 200:
            return f"{data[:100]}...[truncated]"
        else:
            return data


# 全局验证器实例
input_validator = InputValidator()