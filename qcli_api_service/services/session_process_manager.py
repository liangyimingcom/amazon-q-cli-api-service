"""
会话进程管理器

为每个API会话维护独立的Q Chat进程，实现真正的会话记忆功能。
"""

import os
import subprocess
import threading
import time
import logging
from typing import Dict, Optional, Iterator
from qcli_api_service.config import config

logger = logging.getLogger(__name__)


class SessionProcess:
    """单个会话的Q Chat进程封装"""
    
    def __init__(self, session_id: str, work_directory: str = None):
        self.session_id = session_id
        self.work_directory = work_directory
        self.process: Optional[subprocess.Popen] = None
        self.lock = threading.Lock()
        self.created_at = time.time()
        self.last_activity = time.time()
        
    def start(self) -> bool:
        """启动Q Chat进程"""
        with self.lock:
            if self.process and self.is_alive():
                return True
                
            try:
                # 准备环境变量
                env = os.environ.copy()
                if not env.get("AWS_DEFAULT_REGION"):
                    env["AWS_DEFAULT_REGION"] = config.AWS_DEFAULT_REGION
                
                # 启动Q Chat进程，使用--trust-all-tools参数
                self.process = subprocess.Popen(
                    ["q", "chat", "--trust-all-tools"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,  # 行缓冲
                    universal_newlines=True,
                    cwd=self.work_directory,
                    env=env
                )
                
                logger.info(f"为会话 {self.session_id} 启动Q Chat进程 PID: {self.process.pid}")
                return True
                
            except Exception as e:
                logger.error(f"启动Q Chat进程失败 (会话 {self.session_id}): {e}")
                self.process = None
                return False
    
    def is_alive(self) -> bool:
        """检查进程是否还活着"""
        return self.process is not None and self.process.poll() is None
    
    def send_message(self, message: str) -> bool:
        """发送消息到Q Chat进程"""
        with self.lock:
            if not self.is_alive():
                logger.warning(f"进程已死亡，尝试重启 (会话 {self.session_id})")
                if not self.start():
                    return False
            
            try:
                # 直接发送用户消息，不添加额外的上下文
                if config.FORCE_CHINESE:
                    formatted_message = f"请用中文回答：{message}\n"
                else:
                    formatted_message = f"{message}\n"
                
                self.process.stdin.write(formatted_message)
                self.process.stdin.flush()
                self.last_activity = time.time()
                
                logger.debug(f"向会话 {self.session_id} 发送消息: {message[:50]}...")
                return True
                
            except Exception as e:
                logger.error(f"发送消息失败 (会话 {self.session_id}): {e}")
                return False
    
    def read_response(self) -> Iterator[str]:
        """读取Q Chat的响应（流式）"""
        if not self.is_alive():
            logger.error(f"进程未运行 (会话 {self.session_id})")
            return
        
        try:
            buffer = []
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                
                # 清理ANSI颜色代码
                cleaned_line = self._clean_line(line)
                
                # 跳过无效行
                if not cleaned_line or self._should_skip_line(cleaned_line):
                    continue
                
                buffer.append(cleaned_line)
                
                # 当缓冲区有内容时，返回
                if len(buffer) >= 3:  # 每3行返回一次
                    yield "\n".join(buffer)
                    buffer = []
            
            # 返回剩余内容
            if buffer:
                yield "\n".join(buffer)
                
        except Exception as e:
            logger.error(f"读取响应失败 (会话 {self.session_id}): {e}")
    
    def terminate(self):
        """终止Q Chat进程"""
        with self.lock:
            if self.process:
                try:
                    # 发送退出命令
                    if self.is_alive():
                        self.process.stdin.write("/quit\n")
                        self.process.stdin.flush()
                        
                        # 等待进程正常退出
                        try:
                            self.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            # 强制终止
                            self.process.terminate()
                            try:
                                self.process.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                self.process.kill()
                    
                    logger.info(f"会话 {self.session_id} 的Q Chat进程已终止")
                    
                except Exception as e:
                    logger.error(f"终止进程失败 (会话 {self.session_id}): {e}")
                finally:
                    self.process = None
    
    def _clean_line(self, line: str) -> str:
        """清理单行输出"""
        # 移除ANSI颜色代码
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', line)
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


class SessionProcessManager:
    """会话进程管理器"""
    
    def __init__(self):
        self.processes: Dict[str, SessionProcess] = {}
        self.lock = threading.RLock()
    
    def get_or_create_process(self, session_id: str, work_directory: str = None) -> SessionProcess:
        """获取或创建会话进程"""
        with self.lock:
            if session_id not in self.processes:
                process = SessionProcess(session_id, work_directory)
                if process.start():
                    self.processes[session_id] = process
                    logger.info(f"为会话 {session_id} 创建新的Q Chat进程")
                else:
                    raise RuntimeError(f"无法为会话 {session_id} 启动Q Chat进程")
            
            return self.processes[session_id]
    
    def remove_process(self, session_id: str):
        """移除并清理会话进程"""
        with self.lock:
            if session_id in self.processes:
                process = self.processes[session_id]
                process.terminate()
                del self.processes[session_id]
                logger.info(f"会话 {session_id} 的进程已清理")
    
    def cleanup_expired_processes(self, expiry_seconds: int = 3600):
        """清理过期的进程"""
        with self.lock:
            current_time = time.time()
            expired_sessions = []
            
            for session_id, process in self.processes.items():
                if current_time - process.last_activity > expiry_seconds:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                self.remove_process(session_id)
                logger.info(f"清理过期会话进程: {session_id}")
            
            return len(expired_sessions)
    
    def get_active_process_count(self) -> int:
        """获取活跃进程数量"""
        with self.lock:
            return len(self.processes)
    
    def shutdown_all(self):
        """关闭所有进程"""
        with self.lock:
            for session_id in list(self.processes.keys()):
                self.remove_process(session_id)
            logger.info("所有会话进程已关闭")


# 全局会话进程管理器实例
session_process_manager = SessionProcessManager()