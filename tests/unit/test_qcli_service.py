"""
Q CLI服务单元测试
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import subprocess
from qcli_api_service.services.qcli_service import QCLIService


class TestQCLIService:
    """Q CLI服务测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.service = QCLIService()
    
    def test_init(self):
        """测试初始化"""
        assert self.service.ansi_escape is not None
    
    @patch('subprocess.run')
    def test_is_available_success(self, mock_run):
        """测试Q CLI可用性检查 - 成功"""
        mock_run.return_value.returncode = 0
        
        result = self.service.is_available()
        
        assert result is True
        mock_run.assert_called_once_with(
            ["q", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
    
    @patch('subprocess.run')
    def test_is_available_failure(self, mock_run):
        """测试Q CLI可用性检查 - 失败"""
        mock_run.return_value.returncode = 1
        
        result = self.service.is_available()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_is_available_exception(self, mock_run):
        """测试Q CLI可用性检查 - 异常"""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.service.is_available()
        
        assert result is False
    
    def test_prepare_message_with_chinese(self):
        """测试准备消息 - 中文模式"""
        message = "你好"
        context = "用户: 早上好\n助手: 早上好！"
        
        result = self.service._prepare_message(message, context)
        
        assert "请基于这个上下文用中文回答" in result
        assert message in result
        assert context in result
    
    def test_prepare_message_without_context(self):
        """测试准备消息 - 无上下文"""
        message = "你好"
        
        result = self.service._prepare_message(message)
        
        assert "请用中文回答以下问题" in result
        assert message in result
    
    def test_clean_line(self):
        """测试清理单行"""
        # 测试ANSI颜色代码清理
        line_with_ansi = "\x1b[32m这是绿色文本\x1b[0m"
        result = self.service._clean_line(line_with_ansi)
        assert result == "这是绿色文本"
        
        # 测试空白字符清理
        line_with_spaces = "  \t 文本内容  \n  "
        result = self.service._clean_line(line_with_spaces)
        assert result == "文本内容"
    
    def test_should_skip_line(self):
        """测试是否应该跳过行"""
        # 应该跳过的行
        skip_lines = [
            "> 命令提示符",
            "包含/quit的行",
            "q chat 开始",
            "Welcome to Q CLI",
            "Type /quit to exit"
        ]
        
        for line in skip_lines:
            assert self.service._should_skip_line(line) is True
        
        # 不应该跳过的行
        keep_lines = [
            "这是正常的回复",
            "用户问题的答案",
            "AI助手的回复"
        ]
        
        for line in keep_lines:
            assert self.service._should_skip_line(line) is False
    
    def test_clean_output(self):
        """测试清理输出"""
        raw_output = """
> q chat
Welcome to Q CLI
这是第一行回复
这是第二行回复
/quit
"""
        
        result = self.service._clean_output(raw_output)
        
        assert "这是第一行回复" in result
        assert "这是第二行回复" in result
        assert "> q chat" not in result
        assert "Welcome to Q CLI" not in result
        assert "/quit" not in result
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_chat_success(self, mock_file, mock_popen, mock_temp):
        """测试聊天功能 - 成功"""
        # 设置模拟
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
        mock_process = Mock()
        mock_process.communicate.return_value = ("这是Q CLI的回复", "")
        mock_process.returncode = 0
        mock_popen.return_value = mock_process
        
        result = self.service.chat("你好")
        
        assert result == "这是Q CLI的回复"
        mock_popen.assert_called_once()
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_chat_failure(self, mock_file, mock_popen, mock_temp):
        """测试聊天功能 - 失败"""
        # 设置模拟
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
        mock_process = Mock()
        mock_process.communicate.return_value = ("", "错误信息")
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        with pytest.raises(RuntimeError, match="Q CLI执行失败"):
            self.service.chat("你好")
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_chat_timeout(self, mock_file, mock_popen, mock_temp):
        """测试聊天功能 - 超时"""
        # 设置模拟
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
        mock_process = Mock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("q", 30)
        mock_popen.return_value = mock_process
        
        with pytest.raises(RuntimeError, match="Q CLI调用超时"):
            self.service.chat("你好")
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_stream_chat_success(self, mock_file, mock_popen, mock_temp):
        """测试流式聊天功能 - 成功"""
        # 设置模拟
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
        mock_process = Mock()
        
        # 模拟流式输出
        mock_process.stdout.readline.side_effect = [
            "第一行回复\n",
            "第二行回复\n", 
            "第三行回复\n",
            "第四行回复\n",
            ""  # 结束标志
        ]
        mock_process.returncode = 0
        mock_process.stderr.read.return_value = ""
        mock_popen.return_value = mock_process
        
        # 收集流式输出
        results = list(self.service.stream_chat("你好"))
        
        assert len(results) > 0
        # 验证输出包含预期内容
        full_output = "\n".join(results)
        assert "第一行回复" in full_output
        assert "第二行回复" in full_output
    
    @patch('tempfile.NamedTemporaryFile')
    @patch('subprocess.Popen')
    @patch('builtins.open', new_callable=mock_open)
    def test_stream_chat_failure(self, mock_file, mock_popen, mock_temp):
        """测试流式聊天功能 - 失败"""
        # 设置模拟
        mock_temp.return_value.__enter__.return_value.name = "/tmp/test.txt"
        mock_process = Mock()
        mock_process.stdout.readline.return_value = ""  # 立即结束
        mock_process.returncode = 1
        mock_process.stderr.read.return_value = "错误信息"
        mock_popen.return_value = mock_process
        
        with pytest.raises(RuntimeError, match="Q CLI执行失败"):
            list(self.service.stream_chat("你好"))