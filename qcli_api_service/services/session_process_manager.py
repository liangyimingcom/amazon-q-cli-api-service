"""
会话进程管理器

为每个API会话维护独立的Q Chat进程，实现真正的会话记忆功能。
"""

import os
import subprocess
import threading
import time
import logging
import select
import sys
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
        
        # 响应处理相关
        self.response_queue = []
        self.response_lock = threading.Lock()
        self.output_thread = None
        self.reading = False
        self.current_response = []
        
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
                
                # 启动后台线程持续读取输出
                self._start_output_reader()
                return True
                
            except Exception as e:
                logger.error(f"启动Q Chat进程失败 (会话 {self.session_id}): {e}")
                self.process = None
                return False
    
    def _start_output_reader(self):
        """启动后台线程持续读取输出"""
        if self.output_thread and self.output_thread.is_alive():
            return
        
        self.reading = True
        self.output_thread = threading.Thread(target=self._read_output_continuously, daemon=True)
        self.output_thread.start()
        logger.debug(f"为会话 {self.session_id} 启动输出读取线程")
    
    def _read_output_continuously(self):
        """持续读取Q Chat输出的后台线程"""
        last_output_time = time.time()
        
        try:
            while self.reading and self.is_alive():
                try:
                    line = self.process.stdout.readline()
                    if not line:
                        # 检查是否长时间没有输出，如果有当前响应则保存
                        current_time = time.time()
                        if current_time - last_output_time > 2.0:  # 2秒没有新输出就保存
                            with self.response_lock:
                                if self.current_response:
                                    response_text = "\n".join(self.current_response)
                                    self.response_queue.append(response_text)
                                    logger.debug(f"自动保存响应到队列 (会话 {self.session_id}): {len(response_text)} 字符")
                                    self.current_response = []
                                    last_output_time = current_time  # 重置时间
                        
                        time.sleep(0.1)
                        continue
                    
                    last_output_time = time.time()
                    
                    # 清理ANSI颜色代码
                    cleaned_line = self._clean_line(line)
                    
                    # 处理输出行
                    self._process_output_line(cleaned_line)
                    
                except Exception as e:
                    logger.debug(f"读取输出行时出错 (会话 {self.session_id}): {e}")
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"输出读取线程异常 (会话 {self.session_id}): {e}")
        finally:
            # 线程结束时保存剩余响应
            with self.response_lock:
                if self.current_response:
                    response_text = "\n".join(self.current_response)
                    self.response_queue.append(response_text)
                    logger.debug(f"线程结束时保存响应 (会话 {self.session_id}): {len(response_text)} 字符")
                    self.current_response = []
            
            logger.debug(f"会话 {self.session_id} 输出读取线程结束")
    
    def _process_output_line(self, line: str):
        """处理单行输出"""
        with self.response_lock:
            # 检查是否是用户输入回显（以 > 开头）
            if line.startswith("> "):
                # 如果有当前响应，保存它
                if self.current_response:
                    response_text = "\n".join(self.current_response)
                    self.response_queue.append(response_text)
                    logger.debug(f"保存响应到队列 (会话 {self.session_id}): {len(response_text)} 字符")
                    self.current_response = []
                return
            
            # 跳过无效行
            if self._should_skip_line(line):
                return
            
            # 收集响应内容
            if line.strip():  # 只收集非空行
                self.current_response.append(line)
                
                # 对于长响应，定期保存部分内容到队列（流式输出）
                if len(self.current_response) >= 20:  # 每20行保存一次，减少频繁保存
                    response_text = "\n".join(self.current_response)
                    self.response_queue.append(response_text)
                    logger.debug(f"保存部分响应到队列 (会话 {self.session_id}): {len(response_text)} 字符")
                    self.current_response = []
    
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
        """从队列读取Q Chat的响应（支持流式输出）"""
        if not self.is_alive():
            logger.error(f"进程未运行 (会话 {self.session_id})")
            return
        
        max_wait_time = 600  # 最大等待时间（秒）- 增加到120-》600秒以支持复杂任务
        start_time = time.time()
        last_response_time = start_time
        response_count = 0
        
        try:
            while time.time() - start_time < max_wait_time:
                current_time = time.time()
                
                # 检查队列中是否有新响应
                with self.response_lock:
                    if self.response_queue:
                        # 获取队列中的响应
                        response = self.response_queue.pop(0)
                        response_count += 1
                        last_response_time = current_time
                        logger.info(f"从队列获取响应 #{response_count} (会话 {self.session_id}): {len(response)} 字符")
                        yield response
                        continue  # 继续检查是否有更多响应
                
                # 如果没有队列响应，检查是否有部分内容
                if current_time - last_response_time > 3.0:  # 3秒没有新响应
                    with self.response_lock:
                        if self.current_response:
                            response = "\n".join(self.current_response)
                            self.current_response = []
                            response_count += 1
                            last_response_time = current_time
                            logger.debug(f"获取部分响应 #{response_count} (会话 {self.session_id}): {len(response)} 字符")
                            yield response
                            continue
                
                # 如果已经有响应且长时间没有新内容，可能响应结束了
                # 对于复杂任务，给更多时间，特别是涉及多个文件创建的任务
                if response_count == 0:
                    idle_timeout = 35.0  # 第一个响应等待25秒
                elif response_count < 5:
                    idle_timeout = 35.0  # 前几个响应等待35秒（复杂任务需要更多思考时间）
                elif response_count < 15:
                    idle_timeout = 65.0  # 中等响应等待30秒
                else:
                    idle_timeout = 100.0  # 后续响应等待25秒
                
                if response_count > 0 and current_time - last_response_time > idle_timeout:
                    logger.info(f"响应可能结束 (会话 {self.session_id})，共 {response_count} 个响应块，空闲时间: {current_time - last_response_time:.1f}秒，使用的超时时间: {idle_timeout}秒")
                    break
                
                # 短暂等待
                time.sleep(0.1)
            
            # 最后检查是否还有剩余内容
            with self.response_lock:
                if self.current_response:
                    response = "\n".join(self.current_response)
                    self.current_response = []
                    response_count += 1
                    logger.debug(f"获取最终响应 #{response_count} (会话 {self.session_id}): {len(response)} 字符")
                    yield response
            
            if response_count == 0:
                logger.warning(f"读取响应超时，未获取到任何响应 (会话 {self.session_id})")
            else:
                logger.info(f"响应读取完成 (会话 {self.session_id})，共 {response_count} 个响应块")
                
        except Exception as e:
            logger.error(f"读取响应失败 (会话 {self.session_id}): {e}")
    
    def terminate(self):
        """终止Q Chat进程"""
        with self.lock:
            # 停止后台读取线程
            self.reading = False
            
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
                    
            # 等待输出线程结束
            if self.output_thread and self.output_thread.is_alive():
                self.output_thread.join(timeout=2)
    
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