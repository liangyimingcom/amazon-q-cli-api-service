"""
会话管理器 - 核心版本

管理用户会话和对话历史，使用内存存储。
"""

import threading
import time
from typing import Dict, Optional, List
from qcli_api_service.models.core import Session, Message
from qcli_api_service.config import config


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
    
    def create_session(self) -> Session:
        """创建新会话"""
        with self._lock:
            session = Session.create_new()
            self._sessions[session.session_id] = session
            return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        with self._lock:
            return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    def add_message(self, session_id: str, message: Message) -> bool:
        """向会话添加消息"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                session.add_message(message)
                # 限制历史消息数量
                if len(session.messages) > config.MAX_HISTORY_LENGTH:
                    session.messages = session.messages[-config.MAX_HISTORY_LENGTH:]
                return True
            return False
    
    def get_conversation_history(self, session_id: str) -> List[Message]:
        """获取对话历史"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return session.messages.copy()
            return []
    
    def get_context(self, session_id: str) -> str:
        """获取对话上下文"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return session.get_context(config.MAX_HISTORY_LENGTH)
            return ""
    
    def cleanup_expired_sessions(self) -> int:
        """清理过期会话"""
        with self._lock:
            expired_sessions = []
            for session_id, session in self._sessions.items():
                if session.is_expired(config.SESSION_EXPIRY):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self._sessions[session_id]
            
            return len(expired_sessions)
    
    def get_active_session_count(self) -> int:
        """获取活跃会话数量"""
        with self._lock:
            return len(self._sessions)
    
    def get_session_info(self, session_id: str) -> Optional[dict]:
        """获取会话信息"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return {
                    "session_id": session.session_id,
                    "created_at": session.created_at,
                    "last_activity": session.last_activity,
                    "message_count": len(session.messages)
                }
            return None


# 全局会话管理器实例
session_manager = SessionManager()