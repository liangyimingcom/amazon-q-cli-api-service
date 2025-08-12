"""
配置模块单元测试
"""

import os
import pytest
from qcli_api_service.config import Config


class TestConfig:
    """配置类测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = Config()
        
        assert config.HOST == "0.0.0.0"
        assert config.PORT == 8080
        assert config.DEBUG is False
        assert config.SESSION_EXPIRY == 3600
        assert config.MAX_HISTORY_LENGTH == 10  # 简化版本改为10
        assert config.QCLI_TIMEOUT == 30
        assert config.FORCE_CHINESE is True
    
    def test_from_env(self, monkeypatch):
        """测试从环境变量创建配置"""
        # 设置环境变量
        monkeypatch.setenv("HOST", "127.0.0.1")
        monkeypatch.setenv("PORT", "9000")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("SESSION_EXPIRY", "7200")
        monkeypatch.setenv("MAX_HISTORY_LENGTH", "15")
        
        config = Config.from_env()
        
        assert config.HOST == "127.0.0.1"
        assert config.PORT == 9000
        assert config.DEBUG is True
        assert config.SESSION_EXPIRY == 7200
        assert config.MAX_HISTORY_LENGTH == 15
    
    def test_validate_valid_config(self):
        """测试有效配置验证"""
        config = Config()
        # 不应该抛出异常
        config.validate()
    
    def test_validate_invalid_port(self):
        """测试无效端口验证"""
        config = Config(PORT=0)
        
        with pytest.raises(ValueError, match="端口号必须在1-65535范围内"):
            config.validate()
    
    def test_validate_invalid_session_expiry(self):
        """测试无效会话过期时间验证"""
        config = Config(SESSION_EXPIRY=30)
        
        with pytest.raises(ValueError, match="会话过期时间不能少于60秒"):
            config.validate()
    
    def test_validate_invalid_max_history_length(self):
        """测试无效最大历史消息数验证"""
        config = Config(MAX_HISTORY_LENGTH=0)
        
        with pytest.raises(ValueError, match="最大历史消息数必须大于0"):
            config.validate()
    
    def test_validate_invalid_qcli_timeout(self):
        """测试无效Q CLI超时时间验证"""
        config = Config(QCLI_TIMEOUT=3)
        
        with pytest.raises(ValueError, match="Q CLI超时时间不能少于5秒"):
            config.validate()
    
    def test_validate_invalid_qcli_timeout_edge_case(self):
        """测试Q CLI超时时间边界情况"""
        config = Config(QCLI_TIMEOUT=4)
        
        with pytest.raises(ValueError, match="Q CLI超时时间不能少于5秒"):
            config.validate()