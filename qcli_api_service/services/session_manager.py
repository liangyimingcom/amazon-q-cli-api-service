"""
会话管理器 - 核心版本

管理用户会话和对话历史，使用内存存储。
支持为每个会话创建独立的工作目录。
"""

import threading
import time
import os
import shutil
import logging
from typing import Dict, Optional, List
from qcli_api_service.models.core import Session, Message
from qcli_api_service.config import config

logger = logging.getLogger(__name__)


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        # 确保会话基础目录存在
        os.makedirs(config.SESSIONS_BASE_DIR, exist_ok=True)
    
    def create_session(self) -> Session:
        """创建新会话"""
        with self._lock:
            session = Session.create_new(config.SESSIONS_BASE_DIR)
            self._sessions[session.session_id] = session
            logger.info(f"创建新会话: {session.session_id}, 工作目录: {session.work_directory}")
            return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        with self._lock:
            return self._sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                # 删除会话工作目录
                self._cleanup_session_directory(session.work_directory)
                del self._sessions[session_id]
                logger.info(f"删除会话: {session_id}, 工作目录: {session.work_directory}")
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
                    expired_sessions.append((session_id, session.work_directory))
            
            for session_id, work_dir in expired_sessions:
                # 清理会话工作目录
                if config.AUTO_CLEANUP_SESSIONS:
                    self._cleanup_session_directory(work_dir)
                del self._sessions[session_id]
                logger.info(f"清理过期会话: {session_id}, 工作目录: {work_dir}")
            
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
                    "message_count": len(session.messages),
                    "work_directory": session.get_relative_work_directory(),
                    "absolute_work_directory": session.get_absolute_work_directory()
                }
            return None
    
    def _cleanup_session_directory(self, work_directory: str) -> None:
        """清理会话工作目录"""
        try:
            if os.path.exists(work_directory):
                shutil.rmtree(work_directory)
                logger.info(f"已清理会话目录: {work_directory}")
        except Exception as e:
            logger.error(f"清理会话目录失败 {work_directory}: {e}")
    
    def get_session_work_directory(self, session_id: str) -> Optional[str]:
        """获取会话工作目录"""
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                return session.get_absolute_work_directory()
            return None


# 全局会话管理器实例
session_manager = SessionManager()