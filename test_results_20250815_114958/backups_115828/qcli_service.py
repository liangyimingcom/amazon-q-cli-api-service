"""
Amazon Q CLI服务 - 核心版本

封装Amazon Q CLI的调用逻辑，支持流式输出。
"""

import os
import re
import subprocess
import tempfile
import logging
from typing import Iterator, Optional, List
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
    
    def chat(self, message: str, context: str = "", work_directory: str = None) -> str:
        """
        调用Q CLI进行对话（非流式）
        
        参数:
            message: 用户消息
            context: 对话上下文（可选）
            work_directory: 工作目录（可选）
            
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
                # 准备环境变量
                env = os.environ.copy()
                if not env.get("AWS_DEFAULT_REGION"):
                    env["AWS_DEFAULT_REGION"] = config.AWS_DEFAULT_REGION
                
                # 调用Q CLI
                with open(temp_file_path, 'r') as input_file:
                    process = subprocess.Popen(
                        ["q", "chat"],
                        stdin=input_file,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        universal_newlines=True,
                        cwd=work_directory if work_directory else None,
                        env=env
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
            error_msg = f"Q CLI调用超时（{config.QCLI_TIMEOUT}秒）。AI处理复杂问题需要较长时间，请尝试简化问题或稍后重试。"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Q CLI调用失败: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def stream_chat(self, message: str, context: str = "", work_directory: str = None) -> Iterator[str]:
        """
        调用Q CLI进行对话（流式）
        
        参数:
            message: 用户消息
            context: 对话上下文（可选）
            work_directory: 工作目录（可选）
            
        返回:
            流式输出的迭代器
        """
        try:
            # 立即发送初始进度提示
            yield "🤖 正在处理您的请求，请稍候...\n"
            
            # 准备完整消息
            full_message = self._prepare_message(message, context)
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(full_message)
                temp_file.write("\n/quit\n")
                temp_file_path = temp_file.name
            
            try:
                # 准备环境变量
                env = os.environ.copy()
                if not env.get("AWS_DEFAULT_REGION"):
                    env["AWS_DEFAULT_REGION"] = config.AWS_DEFAULT_REGION
                
                # 启动Q CLI进程
                with open(temp_file_path, 'r') as input_file:
                    process = subprocess.Popen(
                        ["q", "chat"],
                        stdin=input_file,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1,  # 行缓冲
                        universal_newlines=True,
                        cwd=work_directory if work_directory else None,
                        env=env
                    )
                
                # 发送AI思考进度提示
                yield "🔄 AI正在思考中，请耐心等待...\n"
                
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
            error_msg = f"Q CLI流式调用超时（{config.QCLI_TIMEOUT}秒）。AI处理复杂问题需要较长时间，请尝试简化问题或稍后重试。"
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
                # 如果行以">"开头且包含实际内容，移除">"符号
                if cleaned_line.startswith("> "):
                    cleaned_line = cleaned_line[2:]  # 移除"> "
                elif cleaned_line.startswith(">"):
                    cleaned_line = cleaned_line[1:]  # 移除">"
                
                cleaned_lines.append(cleaned_line)
        
        result = '\n'.join(cleaned_lines)
        
        # 清理重复内容
        result = self._remove_duplicate_content(result)
        
        return result
    
    def _remove_duplicate_content(self, text: str) -> str:
        """
        移除文本中的重复内容（优化版本）
        
        参数:
            text: 原始文本
            
        返回:
            去重后的文本
        """
        if not text or len(text) < 50:  # 短文本直接返回
            return text
        
        # 使用更高效的算法
        # 首先尝试检测和移除完全重复的段落
        text = self._remove_exact_duplicates_optimized(text)
        
        # 然后使用优化的模式匹配移除常见的重复内容
        text = self._remove_pattern_duplicates_optimized(text)
        
        return text
    
    def _remove_exact_duplicates(self, text: str) -> str:
        """移除完全重复的段落"""
        # 按段落分割（双换行符）
        paragraphs = text.split('\n\n')
        
        # 如果只有一个段落，按单换行符分割检查
        if len(paragraphs) == 1:
            lines = text.split('\n')
            return self._remove_duplicate_blocks(lines)
        
        # 检查段落级别的重复
        unique_paragraphs = []
        seen_paragraphs = set()
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph and paragraph not in seen_paragraphs:
                unique_paragraphs.append(paragraph)
                seen_paragraphs.add(paragraph)
        
        return '\n\n'.join(unique_paragraphs)
    
    def _remove_pattern_duplicates(self, text: str) -> str:
        """使用模式匹配移除常见的重复内容"""
        lines = text.split('\n')
        if len(lines) <= 1:
            return text
        
        # 定义常见的重复模式
        help_patterns = [
            "我可以帮助您",
            "我可以帮助你",
            "有什么我可以帮助",
            "请问有什么我可以帮助",
            "什么我可以帮助您的吗",
            "什么我可以帮助你的吗"
        ]
        
        service_patterns = [
            "管理和查询 AWS 资源",
            "AWS 服务管理和配置",
            "代码编写和调试",
            "编写和调试代码",
            "文件系统操作",
            "读写本地文件系统",
            "执行命令行操作",
            "命令行操作"
        ]
        
        # 移除重复的帮助提示行和服务列表项
        unique_lines = []
        seen_help_line = False
        seen_service_lists = set()
        seen_exact_lines = set()
        
        for line in lines:
            line_stripped = line.strip()
            
            # 跳过空行
            if not line_stripped:
                unique_lines.append(line)
                continue
            
            # 检查完全重复的行
            if line_stripped in seen_exact_lines:
                continue
            
            # 检查是否是帮助提示行
            is_help_line = any(pattern in line_stripped for pattern in help_patterns)
            if is_help_line:
                if not seen_help_line:
                    unique_lines.append(line)
                    seen_help_line = True
                    seen_exact_lines.add(line_stripped)
                # 跳过重复的帮助提示行
                continue
            
            # 检查是否是服务列表项（以•开头或包含服务关键词）
            is_service_line = (line_stripped.startswith('•') or 
                             any(pattern in line_stripped for pattern in service_patterns))
            
            if is_service_line:
                # 标准化服务描述
                normalized = self._normalize_service_description(line_stripped)
                if normalized not in seen_service_lists:
                    unique_lines.append(line)
                    seen_service_lists.add(normalized)
                    seen_exact_lines.add(line_stripped)
                # 跳过重复的服务列表项
                continue
            
            # 其他行直接添加
            unique_lines.append(line)
            seen_exact_lines.add(line_stripped)
        
        return '\n'.join(unique_lines)
    
    def _normalize_service_description(self, text: str) -> str:
        """标准化服务描述，用于重复检测"""
        # 移除项目符号和多余空格
        normalized = text.replace('•', '').strip()
        
        # 标准化常见的服务描述
        mappings = {
            "管理和查询 AWS 资源": "aws_management",
            "AWS 服务管理和配置": "aws_management", 
            "代码编写和调试": "code_development",
            "编写和调试代码": "code_development",
            "文件系统操作": "file_operations",
            "读写本地文件系统": "file_operations",
            "读写文件和目录": "file_operations",
            "执行命令行操作": "command_operations",
            "命令行操作": "command_operations",
            "基础设施配置": "infrastructure",
            "基础设施优化": "infrastructure",
            "提供 AWS 最佳实践建议": "aws_best_practices",
            "AWS 最佳实践建议": "aws_best_practices",
            "解决技术问题": "technical_support",
            "技术问题": "technical_support"
        }
        
        for pattern, standard in mappings.items():
            if pattern in normalized:
                return standard
        
        return normalized.lower()
    
    def _remove_duplicate_blocks(self, lines: List[str]) -> str:
        """
        移除重复的行块
        
        参数:
            lines: 文本行列表
            
        返回:
            去重后的文本
        """
        if len(lines) <= 1:
            return '\n'.join(lines)
        
        # 简化算法：检查文本是否在中间位置有完全重复的部分
        text = '\n'.join(lines)
        
        # 尝试找到文本的中点，看是否前半部分和后半部分相同
        text_length = len(text)
        mid_point = text_length // 2
        
        # 在中点附近寻找可能的分割点（换行符）
        for offset in range(-50, 51):  # 在中点前后50个字符内寻找
            split_point = mid_point + offset
            if 0 < split_point < text_length and text[split_point] == '\n':
                first_half = text[:split_point].strip()
                second_half = text[split_point + 1:].strip()
                
                # 如果两半完全相同，返回其中一半
                if first_half == second_half and first_half:
                    return first_half
        
        # 如果没有找到完全重复，返回原文本
        return text
    
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
        # 跳过命令提示符和退出命令，但保留包含实际回复内容的行
        
        # 如果行以">"开头，需要进一步判断
        if line.startswith(">"):
            # 如果">"后面只有空格或者是用户输入的回显，则跳过
            content_after_prompt = line[1:].strip()
            
            # 跳过用户输入的回显（通常是我们发送的问题）
            if (content_after_prompt.startswith("请用中文回答") or 
                content_after_prompt.startswith("以下是我们之前的对话历史") or
                not content_after_prompt):
                return True
            
            # 保留包含AI回复内容的行
            return False
        
        # 其他跳过模式
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
    
    def _remove_exact_duplicates_optimized(self, text: str) -> str:
        """优化版本的完全重复检测"""
        # 快速检查：如果文本长度小于100，跳过复杂检测
        if len(text) < 100:
            return text
        
        # 使用更高效的算法检测重复
        lines = text.split('\n')
        if len(lines) < 4:  # 少于4行，不太可能有重复
            return text
        
        # 检查是否有连续的重复行块
        seen_blocks = set()
        unique_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 检查接下来的3行是否形成重复块
            if i + 2 < len(lines):
                block = '\n'.join([lines[i].strip(), lines[i+1].strip(), lines[i+2].strip()])
                if block in seen_blocks and block.strip():
                    # 跳过重复块
                    i += 3
                    continue
                elif block.strip():
                    seen_blocks.add(block)
            
            unique_lines.append(lines[i])
            i += 1
        
        return '\n'.join(unique_lines)
    
    def _remove_pattern_duplicates_optimized(self, text: str) -> str:
        """优化版本的模式重复检测"""
        lines = text.split('\n')
        if len(lines) <= 2:
            return text
        
        # 使用更高效的重复检测
        unique_lines = []
        seen_patterns = set()
        
        # 预编译常用模式（避免重复编译）
        help_keywords = {"帮助", "help", "可以帮助"}
        service_keywords = {"AWS", "资源", "代码", "文件", "命令"}
        
        for line in lines:
            line_stripped = line.strip()
            
            # 跳过空行
            if not line_stripped:
                unique_lines.append(line)
                continue
            
            # 快速检查是否是重复的帮助或服务行
            line_lower = line_stripped.lower()
            
            # 生成行的特征（用于重复检测）
            is_help_line = any(keyword in line_stripped for keyword in help_keywords)
            is_service_line = (line_stripped.startswith('•') or 
                             any(keyword in line_stripped for keyword in service_keywords))
            
            # 创建行的特征标识
            if is_help_line:
                pattern_key = "help_line"
            elif is_service_line:
                # 标准化服务行
                normalized = line_stripped.replace('•', '').strip()
                pattern_key = f"service_{hash(normalized) % 1000}"
            else:
                pattern_key = line_stripped
            
            # 检查是否已见过此模式
            if pattern_key not in seen_patterns:
                unique_lines.append(line)
                seen_patterns.add(pattern_key)
        
        return '\n'.join(unique_lines)


# 全局Q CLI服务实例
qcli_service = QCLIService()