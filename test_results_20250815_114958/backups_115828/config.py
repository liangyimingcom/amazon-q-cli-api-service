"""
配置管理模块 - 核心版本

管理应用的核心配置项，支持环境变量配置。
"""

import os
from dataclasses import dataclass


@dataclass
class Config:
    """应用配置类 - 只包含核心配置"""
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    DEBUG: bool = False
    
    # 会话配置
    SESSION_EXPIRY: int = 3600  # 1小时，单位：秒
    MAX_HISTORY_LENGTH: int = 10  # 最大历史消息数（简化为10条）
    
    # Q CLI配置
    QCLI_TIMEOUT: int = 45  # Q CLI调用超时时间，单位：秒（根据实际测试调整）
    FORCE_CHINESE: bool = True  # 强制使用中文回复
    
    # AWS配置
    AWS_DEFAULT_REGION: str = "us-east-1"  # 默认AWS区域，减少网络延迟
    
    # 会话工作目录配置
    SESSIONS_BASE_DIR: str = "sessions"  # 会话基础目录
    AUTO_CLEANUP_SESSIONS: bool = True  # 自动清理过期会话目录
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量创建配置实例"""
        return cls(
            HOST=os.getenv("HOST", cls.HOST),
            PORT=int(os.getenv("PORT", str(cls.PORT))),
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            SESSION_EXPIRY=int(os.getenv("SESSION_EXPIRY", str(cls.SESSION_EXPIRY))),
            MAX_HISTORY_LENGTH=int(os.getenv("MAX_HISTORY_LENGTH", str(cls.MAX_HISTORY_LENGTH))),
            QCLI_TIMEOUT=int(os.getenv("QCLI_TIMEOUT", str(cls.QCLI_TIMEOUT))),
            FORCE_CHINESE=os.getenv("FORCE_CHINESE", "true").lower() == "true",
            AWS_DEFAULT_REGION=os.getenv("AWS_DEFAULT_REGION", cls.AWS_DEFAULT_REGION),
            SESSIONS_BASE_DIR=os.getenv("SESSIONS_BASE_DIR", cls.SESSIONS_BASE_DIR),
            AUTO_CLEANUP_SESSIONS=os.getenv("AUTO_CLEANUP_SESSIONS", "true").lower() == "true",
        )
    
    def validate(self) -> None:
        """验证配置的有效性"""
        if self.PORT < 1 or self.PORT > 65535:
            raise ValueError(f"端口号必须在1-65535范围内，当前值: {self.PORT}")
        
        if self.SESSION_EXPIRY < 60:
            raise ValueError(f"会话过期时间不能少于60秒，当前值: {self.SESSION_EXPIRY}")
        
        if self.MAX_HISTORY_LENGTH < 1:
            raise ValueError(f"最大历史消息数必须大于0，当前值: {self.MAX_HISTORY_LENGTH}")
        
        if self.QCLI_TIMEOUT < 5:
            raise ValueError(f"Q CLI超时时间不能少于5秒，当前值: {self.QCLI_TIMEOUT}")


# 全局配置实例
config = Config.from_env()