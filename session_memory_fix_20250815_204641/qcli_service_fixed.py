"""
Amazon Q CLI服务 - 修复版本

使用持久化会话进程，实现真正的会话记忆功能。
"""

import os
import re
import subprocess
import tempfile
import logging
from typing import Iterator, Optional, List
from qcli_api_service.config import config, get_timeout_for_request

# 导入新的会话进程管理器
import sys
sys.path.append(os.path.dirname(__file__))
from session_process_manager import session_process_manager

logger = logging.getLogger(__name__)


class QCLIService:
    """Amazon Q CLI服务类 - 修复版本"""
    
    def __init__(self):
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    def is_available(self) -> bool:
        """检查Q CLI是否可用"""
        try:
            result = subprocess.run(
                ["q", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            logger.warning(f"Q CLI不可用: {e}")
            return False
    
    def chat(self, message: str, session_id: str, work_directory: str = None) -> str:
        """
        调用Q CLI进行对话（非流式）- 使用会话记忆
        
        参数:
            message: 用户消息
            session_id: 会话ID
            work_directory: 工作目录（可选）
            
        返回:
            Q CLI的回复
        """
        try:
            # 获取或创建会话进程
            process = session_process_manager.get_or_create_process(session_id, work_directory)
            
            # 发送消息（不包含历史上下文，让Q Chat自己维护记忆）
            if not process.send_message(message):
                raise RuntimeError("发送消息到Q Chat进程失败")
            
            # 收集完整响应
            response_parts = []
            for chunk in process.read_response():
                response_parts.append(chunk)
            
            complete_response = "\n".join(response_parts)
            
            if not complete_response:
                raise RuntimeError("Q CLI没有返回有效输出")
            
            logger.info(f"Q CLI处理完成，回复长度: {len(complete_response)} 字符")
            return complete_response
                
        except Exception as e:
            error_msg = f"Q CLI调用失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def stream_chat(self, message: str, session_id: str, work_directory: str = None) -> Iterator[str]:
        """
        调用Q CLI进行对话（流式）- 使用会话记忆
        
        参数:
            message: 用户消息
            session_id: 会话ID
            work_directory: 工作目录（可选）
            
        返回:
            流式输出的迭代器
        """
        try:
            # 立即发送初始进度提示
            yield "🤖 正在处理您的请求，请稍候...\n"
            
            # 获取或创建会话进程
            process = session_process_manager.get_or_create_process(session_id, work_directory)
            
            # 发送AI思考进度提示
            yield "🔄 AI正在思考中，请耐心等待...\n"
            
            # 发送消息（不包含历史上下文）
            if not process.send_message(message):
                raise RuntimeError("发送消息到Q Chat进程失败")
            
            # 流式读取响应
            for chunk in process.read_response():
                if chunk:
                    yield chunk
                    
        except Exception as e:
            error_msg = f"Q CLI流式调用失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def cleanup_session(self, session_id: str):
        """清理会话进程"""
        session_process_manager.remove_process(session_id)
    
    def cleanup_expired_sessions(self, expiry_seconds: int = 3600) -> int:
        """清理过期会话"""
        return session_process_manager.cleanup_expired_processes(expiry_seconds)
    
    def get_active_session_count(self) -> int:
        """获取活跃会话数量"""
        return session_process_manager.get_active_process_count()
    
    # 保留原有的方法用于兼容性，但标记为已弃用
    def _prepare_message(self, message: str, context: str = "") -> str:
        """
        准备发送给Q CLI的消息 - 已弃用
        
        注意：新版本不再使用此方法，因为Q Chat自己维护会话记忆
        """
        logger.warning("_prepare_message方法已弃用，新版本直接发送用户消息")
        return message
    
    # 保留其他清理方法用于兼容性
    def _clean_output(self, output: str) -> str:
        """清理Q CLI输出 - 保留用于兼容性"""
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = self._clean_line(line)
            if cleaned_line and not self._should_skip_line(cleaned_line):
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_line(self, line: str) -> str:
        """清理单行输出"""
        cleaned = self.ansi_escape.sub('', line)
        return cleaned.strip()
    
    def _should_skip_line(self, line: str) -> bool:
        """判断是否应该跳过某行"""
        skip_patterns = [
            lambda l: "/quit" in l,
            lambda l: l.startswith("q chat"),
            lambda l: "Welcome to" in l,
            lambda l: "Type /quit" in l,
            lambda l: "Did you know?" in l,
            lambda l: "Get notified whenever" in l,
            lambda l: "chat.enableNotifications" in l,
            lambda l: "/help all commands" in l,
            lambda l: "ctrl + j new lines" in l,
            lambda l: "You are chatting with" in l,
            lambda l: "Thinking..." in l,
            lambda l: l.startswith("━"),
            lambda l: l.startswith("╭"),
            lambda l: l.startswith("│"),
            lambda l: l.startswith("╰"),
        ]
        
        return any(pattern(line) for pattern in skip_patterns)


# 全局Q CLI服务实例
qcli_service = QCLIService()