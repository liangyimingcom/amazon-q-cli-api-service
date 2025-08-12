"""
输入验证器单元测试
"""

import pytest
from qcli_api_service.utils.validators import InputValidator


class TestInputValidator:
    """输入验证器测试"""
    
    def test_validate_session_id_valid(self):
        """测试有效会话ID验证"""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        assert InputValidator.validate_session_id(valid_uuid) is True
    
    def test_validate_session_id_invalid(self):
        """测试无效会话ID验证"""
        invalid_ids = [
            "",
            None,
            "invalid-uuid",
            "123",
            "550e8400-e29b-41d4-a716",  # 不完整的UUID
            123,  # 非字符串类型
        ]
        
        for invalid_id in invalid_ids:
            assert InputValidator.validate_session_id(invalid_id) is False
    
    def test_validate_message_valid(self):
        """测试有效消息验证"""
        valid_messages = [
            "你好",
            "这是一个正常的消息",
            "包含数字123和符号!@#的消息",
            "a" * 4000,  # 最大长度
        ]
        
        for message in valid_messages:
            is_valid, error = InputValidator.validate_message(message)
            assert is_valid is True
            assert error is None
    
    def test_validate_message_invalid(self):
        """测试无效消息验证"""
        invalid_cases = [
            ("", "消息内容不能为空"),
            (None, "消息内容不能为空"),
            ("   \n\t  ", "消息内容不能为空"),  # 只有空白字符
            ("a" * 4001, "消息内容过长"),  # 超过长度限制
            ("<script>alert('xss')</script>", "消息内容包含不允许的字符"),  # 恶意内容
        ]
        
        for message, expected_error in invalid_cases:
            is_valid, error = InputValidator.validate_message(message)
            assert is_valid is False
            assert expected_error in error
    
    def test_validate_request_data_valid(self):
        """测试有效请求数据验证"""
        valid_data = {
            "message": "你好",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "stream": False
        }
        
        is_valid, error = InputValidator.validate_request_data(valid_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_request_data_minimal(self):
        """测试最小有效请求数据"""
        minimal_data = {"message": "你好"}
        
        is_valid, error = InputValidator.validate_request_data(minimal_data)
        assert is_valid is True
        assert error is None
    
    def test_validate_request_data_invalid(self):
        """测试无效请求数据验证"""
        invalid_cases = [
            ("not a dict", "请求数据格式错误"),
            ({}, "缺少必需字段: message"),
            ({"message": ""}, "消息内容不能为空"),
            ({"message": "你好", "session_id": "invalid"}, "会话ID格式无效"),
            ({"message": "你好", "stream": "not_bool"}, "stream字段必须为布尔值"),
        ]
        
        for data, expected_error in invalid_cases:
            is_valid, error = InputValidator.validate_request_data(data)
            assert is_valid is False
            assert expected_error in error
    
    def test_clean_message(self):
        """测试消息清理"""
        test_cases = [
            ("  你好  ", "你好"),
            ("你好\n\n世界", "你好 世界"),
            ("多个    空格", "多个 空格"),
            ("包含\x00控制字符", "包含控制字符"),
            ("", ""),
        ]
        
        for input_msg, expected in test_cases:
            result = InputValidator.clean_message(input_msg)
            assert result == expected
    
    def test_contains_malicious_content(self):
        """测试恶意内容检测"""
        malicious_messages = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img onclick='alert()'>",
            "<iframe src='evil.com'>",
            "<object data='evil.swf'>",
            "<embed src='evil.swf'>",
        ]
        
        for message in malicious_messages:
            assert InputValidator._contains_malicious_content(message) is True
        
        # 正常消息不应该被标记为恶意
        normal_messages = [
            "这是正常消息",
            "包含<和>符号但不是标签",
            "讨论JavaScript编程",
        ]
        
        for message in normal_messages:
            assert InputValidator._contains_malicious_content(message) is False
    
    def test_sanitize_for_logging_dict(self):
        """测试字典数据的日志清理"""
        data = {
            "message": "正常消息",
            "password": "secret123",
            "token": "abc123",
            "long_text": "a" * 300,
            "normal_field": "正常值"
        }
        
        sanitized = InputValidator.sanitize_for_logging(data)
        
        assert sanitized["message"] == "正常消息"
        assert sanitized["password"] == "[REDACTED]"
        assert sanitized["token"] == "[REDACTED]"
        assert "[truncated]" in sanitized["long_text"]
        assert sanitized["normal_field"] == "正常值"
    
    def test_sanitize_for_logging_list(self):
        """测试列表数据的日志清理"""
        data = ["正常项", "a" * 300, {"password": "secret"}]
        
        sanitized = InputValidator.sanitize_for_logging(data)
        
        assert sanitized[0] == "正常项"
        assert "[truncated]" in sanitized[1]
        assert sanitized[2]["password"] == "[REDACTED]"
    
    def test_sanitize_for_logging_string(self):
        """测试字符串数据的日志清理"""
        long_string = "a" * 300
        
        sanitized = InputValidator.sanitize_for_logging(long_string)
        
        assert "[truncated]" in sanitized
        assert len(sanitized) < len(long_string)
    
    def test_sanitize_for_logging_other_types(self):
        """测试其他类型数据的日志清理"""
        test_cases = [
            (123, 123),
            (True, True),
            (None, None),
            (12.34, 12.34),
        ]
        
        for input_data, expected in test_cases:
            result = InputValidator.sanitize_for_logging(input_data)
            assert result == expected