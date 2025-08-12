"""
Amazon Q CLI服务 - 核心版本

封装Amazon Q CLI的调用逻辑，支持流式输出。
"""

import os
import re
import subprocess
import tempfile
import logging
from typing import Iterator, Optional
from qcli_api_service.config import config


logger = logging.getLogger(__name__)


class QCLIService:
    """Amazon Q CLI服务类"""
    
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
    
    def chat(self, message: str, context: str = "") -> str:
        """
        调用Q CLI进行对话（非流式）
        
        参数:
            message: 用户消息
            context: 对话上下文（可选）
            
        返回:
            Q CLI的回复
        """
        try:
            # 准备完整消息
            full_message = self._prepare_message(message, context)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(full_message)
                temp_file.write("\n/quit\n")
                temp_file_path = temp_file.name
            
            try:
                # 调用Q CLI
                with open(temp_file_path, 'r') as input_file:
                    process = subprocess.Popen(
                        ["q", "chat"],
                        stdin=input_file,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        universal_newlines=True
                    )
                
                # 等待完成
                stdout, stderr = process.communicate(timeout=config.QCLI_TIMEOUT)
                
                if process.returncode != 0:
                    error_msg = f"Q CLI执行失败: {stderr}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                
                # 清理输出
                cleaned_output = self._clean_output(stdout)
                
                if not cleaned_output:
                    raise RuntimeError("Q CLI没有返回有效输出")
                
                logger.info(f"Q CLI处理完成，回复长度: {len(cleaned_output)} 字符")
                return cleaned_output
                
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            error_msg = "Q CLI调用超时"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Q CLI调用失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def stream_chat(self, message: str, context: str = "") -> Iterator[str]:
        """
        调用Q CLI进行对话（流式）
        
        参数:
            message: 用户消息
            context: 对话上下文（可选）
            
        返回:
            流式输出的迭代器
        """
        try:
            # 准备完整消息
            full_message = self._prepare_message(message, context)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(full_message)
                temp_file.write("\n/quit\n")
                temp_file_path = temp_file.name
            
            try:
                # 启动Q CLI进程
                with open(temp_file_path, 'r') as input_file:
                    process = subprocess.Popen(
                        ["q", "chat"],
                        stdin=input_file,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,  # 行缓冲
                        universal_newlines=True
                    )
                
                # 流式读取输出
                buffer = []
                for line in iter(process.stdout.readline, ''):
                    # 清理行
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
                
                # 等待进程结束
                process.wait(timeout=5)
                
                if process.returncode != 0:
                    stderr = process.stderr.read()
                    error_msg = f"Q CLI执行失败: {stderr}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
                    
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            error_msg = "Q CLI调用超时"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Q CLI流式调用失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def _prepare_message(self, message: str, context: str = "") -> str:
        """
        准备发送给Q CLI的消息
        
        参数:
            message: 用户消息
            context: 对话上下文
            
        返回:
            格式化的完整消息
        """
        if config.FORCE_CHINESE:
            if context:
                return f"以下是我们之前的对话历史，请基于这个上下文用中文回答我的问题：\n\n{context}\n\n现在，请用中文回答我的问题：{message}"
            else:
                return f"请用中文回答以下问题：{message}"
        else:
            if context:
                return f"Previous conversation history:\n\n{context}\n\nNow, please answer my question: {message}"
            else:
                return message
    
    def _clean_output(self, output: str) -> str:
        """
        清理Q CLI输出
        
        参数:
            output: 原始输出
            
        返回:
            清理后的输出
        """
        lines = output.split('\n')
        cleaned_lines = []
        
        for line in lines:
            cleaned_line = self._clean_line(line)
            if cleaned_line and not self._should_skip_line(cleaned_line):
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_line(self, line: str) -> str:
        """
        清理单行输出
        
        参数:
            line: 原始行
            
        返回:
            清理后的行
        """
        # 移除ANSI颜色代码
        cleaned = self.ansi_escape.sub('', line)
        # 去除首尾空白
        return cleaned.strip()
    
    def _should_skip_line(self, line: str) -> bool:
        """
        判断是否应该跳过某行
        
        参数:
            line: 清理后的行
            
        返回:
            是否应该跳过
        """
        # 跳过命令提示符和退出命令
        skip_patterns = [
            lambda l: l.startswith(">"),
            lambda l: "/quit" in l,
            lambda l: l.startswith("q chat"),
            lambda l: "Welcome to" in l,
            lambda l: "Type /quit" in l,
        ]
        
        return any(pattern(line) for pattern in skip_patterns)


# 全局Q CLI服务实例
qcli_service = QCLIService()