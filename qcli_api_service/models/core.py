"""
核心数据模型

定义系统中使用的基本数据结构。
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Message:
    """消息数据模型"""
    timestamp: float
    role: str  # 'user' 或 'assistant'
    content: str
    
    @classmethod
    def create_user_message(cls, content: str) -> 'Message':
        """创建用户消息"""
        return cls(
            timestamp=time.time(),
            role='user',
            content=content
        )
    
    @classmethod
    def create_assistant_message(cls, content: str) -> 'Message':
        """创建助手消息"""
        return cls(
            timestamp=time.time(),
            role='assistant',
            content=content
        )


@dataclass
class Session:
    """会话数据模型"""
    session_id: str
    created_at: float
    last_activity: float
    messages: List[Message] = field(default_factory=list)
    
    @classmethod
    def create_new(cls) -> 'Session':
        """创建新会话"""
        current_time = time.time()
        return cls(
            session_id=str(uuid.uuid4()),
            created_at=current_time,
            last_activity=current_time,
            messages=[]
        )
    
    def add_message(self, message: Message) -> None:
        """添加消息到会话"""
        self.messages.append(message)
        self.last_activity = time.time()
    
    def get_context(self, max_messages: int = 10) -> str:
        """获取对话上下文"""
        if not self.messages:
            return ""
        
        # 获取最近的消息
        recent_messages = self.messages[-max_messages:]
        
        # 格式化为上下文字符串
        context_parts = []
        for msg in recent_messages:
            prefix = "用户: " if msg.role == "user" else "助手: "
            context_parts.append(f"{prefix}{msg.content}")
        
        return "\n".join(context_parts)
    
    def is_expired(self, expiry_seconds: int) -> bool:
        """检查会话是否过期"""
        return (time.time() - self.last_activity) > expiry_seconds


@dataclass
class ChatRequest:
    """聊天请求数据模型"""
    session_id: Optional[str]
    message: str
    stream: bool = False
    
    def validate(self) -> None:
        """验证请求数据"""
        if not self.message or not self.message.strip():
            raise ValueError("消息内容不能为空")
        
        if len(self.message) > 4000:  # 限制消息长度
            raise ValueError("消息内容过长，最大4000字符")


@dataclass
class ChatResponse:
    """聊天响应数据模型"""
    session_id: str
    message: str
    timestamp: float
    
    @classmethod
    def create(cls, session_id: str, message: str) -> 'ChatResponse':
        """创建聊天响应"""
        return cls(
            session_id=session_id,
            message=message,
            timestamp=time.time()
        )


@dataclass
class ErrorResponse:
    """错误响应数据模型"""
    error: str
    code: int
    details: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            "error": self.error,
            "code": self.code
        }
        if self.details:
            result["details"] = self.details
        return result