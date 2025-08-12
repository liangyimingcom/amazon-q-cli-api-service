"""
上下文保持功能集成测试
"""

import pytest
from unittest.mock import patch
from qcli_api_service.app import create_app


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestContextPersistence:
    """上下文保持功能测试"""
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_context_preservation_in_session(self, mock_chat, client):
        """测试会话中的上下文保持"""
        # 模拟Q CLI回复
        mock_chat.side_effect = [
            "我的名字是小助手",
            "是的，我刚才说了我的名字是小助手"
        ]
        
        # 创建会话
        session_response = client.post('/api/v1/sessions')
        session_id = session_response.get_json()['session_id']
        
        # 第一轮对话
        response1 = client.post('/api/v1/chat', json={
            'session_id': session_id,
            'message': '你的名字是什么？'
        })
        
        assert response1.status_code == 200
        data1 = response1.get_json()
        assert data1['message'] == "我的名字是小助手"
        
        # 第二轮对话 - 应该包含上下文
        response2 = client.post('/api/v1/chat', json={
            'session_id': session_id,
            'message': '你刚才说了什么？'
        })
        
        assert response2.status_code == 200
        data2 = response2.get_json()
        assert data2['message'] == "是的，我刚才说了我的名字是小助手"
        
        # 验证Q CLI被调用时包含了上下文
        assert mock_chat.call_count == 2
        
        # 第二次调用应该包含上下文
        second_call_args = mock_chat.call_args_list[1]
        message, context = second_call_args[0]
        
        assert message == '你刚才说了什么？'
        assert '用户: 你的名字是什么？' in context
        assert '助手: 我的名字是小助手' in context
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_context_isolation_between_sessions(self, mock_chat, client):
        """测试不同会话间的上下文隔离"""
        mock_chat.return_value = "这是回复"
        
        # 创建两个会话
        session1_response = client.post('/api/v1/sessions')
        session1_id = session1_response.get_json()['session_id']
        
        session2_response = client.post('/api/v1/sessions')
        session2_id = session2_response.get_json()['session_id']
        
        # 在第一个会话中对话
        client.post('/api/v1/chat', json={
            'session_id': session1_id,
            'message': '我在会话1中说话'
        })
        
        # 在第二个会话中对话
        client.post('/api/v1/chat', json={
            'session_id': session2_id,
            'message': '我在会话2中说话'
        })
        
        # 验证两次调用的上下文是独立的
        assert mock_chat.call_count == 2
        
        # 第一次调用只包含当前用户消息的上下文
        first_call_args = mock_chat.call_args_list[0]
        _, first_context = first_call_args[0]
        assert '我在会话1中说话' in first_context
        assert '我在会话2中说话' not in first_context
        
        # 第二次调用只包含第二个会话的上下文
        second_call_args = mock_chat.call_args_list[1]
        _, second_context = second_call_args[0]
        assert '我在会话2中说话' in second_context
        assert '我在会话1中说话' not in second_context
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_context_length_limit(self, mock_chat, client):
        """测试上下文长度限制"""
        mock_chat.return_value = "收到"
        
        # 创建会话
        session_response = client.post('/api/v1/sessions')
        session_id = session_response.get_json()['session_id']
        
        # 发送多条消息，超过历史长度限制
        for i in range(8):  # 发送8条消息，产生16条记录（用户+助手）
            client.post('/api/v1/chat', json={
                'session_id': session_id,
                'message': f'消息{i}'
            })
        
        # 最后一次调用应该只包含最近的消息
        last_call_args = mock_chat.call_args_list[-1]
        _, context = last_call_args[0]
        
        # 上下文应该被限制在最近的10条消息内
        # 由于每次对话产生2条消息（用户+助手），所以应该包含最近5轮对话
        assert '消息0' not in context
        assert '消息1' not in context
        assert '消息2' not in context
        
        # 但应该包含最近的消息
        assert '消息6' in context
        assert '消息7' in context
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_context_format(self, mock_chat, client):
        """测试上下文格式"""
        mock_chat.side_effect = ["第一个回复", "第二个回复"]
        
        # 创建会话
        session_response = client.post('/api/v1/sessions')
        session_id = session_response.get_json()['session_id']
        
        # 第一轮对话
        client.post('/api/v1/chat', json={
            'session_id': session_id,
            'message': '第一个问题'
        })
        
        # 第二轮对话
        client.post('/api/v1/chat', json={
            'session_id': session_id,
            'message': '第二个问题'
        })
        
        # 检查第二次调用的上下文格式
        second_call_args = mock_chat.call_args_list[1]
        _, context = second_call_args[0]
        
        # 验证上下文格式正确（包含历史对话和当前用户消息）
        lines = context.split('\n')
        assert len(lines) == 3
        assert lines[0] == '用户: 第一个问题'
        assert lines[1] == '助手: 第一个回复'
        assert lines[2] == '用户: 第二个问题'
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.stream_chat')
    def test_context_in_stream_chat(self, mock_stream_chat, client):
        """测试流式聊天中的上下文保持"""
        # 模拟流式回复
        mock_stream_chat.side_effect = [
            iter(["第一个流式回复"]),
            iter(["第二个流式回复"])
        ]
        
        # 创建会话
        session_response = client.post('/api/v1/sessions')
        session_id = session_response.get_json()['session_id']
        
        # 第一次流式对话
        response1 = client.post('/api/v1/chat/stream', json={
            'session_id': session_id,
            'message': '第一个流式问题'
        })
        
        # 消费第一次响应
        list(response1.response)
        
        # 第二次流式对话
        response2 = client.post('/api/v1/chat/stream', json={
            'session_id': session_id,
            'message': '第二个流式问题'
        })
        
        # 消费第二次响应
        list(response2.response)
        
        # 验证第二次调用包含上下文
        assert mock_stream_chat.call_count == 2
        
        second_call_args = mock_stream_chat.call_args_list[1]
        _, context = second_call_args[0]
        
        # 应该包含第一次对话的内容
        assert '用户: 第一个流式问题' in context
        assert '助手: 第一个流式回复' in context
    
    def test_session_info_includes_message_count(self, client):
        """测试会话信息包含消息数量"""
        # 创建会话
        session_response = client.post('/api/v1/sessions')
        session_id = session_response.get_json()['session_id']
        
        # 检查初始消息数量
        info_response = client.get(f'/api/v1/sessions/{session_id}')
        info_data = info_response.get_json()
        assert info_data['message_count'] == 0
        
        # 发送消息后检查消息数量
        with patch('qcli_api_service.services.qcli_service.qcli_service.chat') as mock_chat:
            mock_chat.return_value = "回复"
            
            client.post('/api/v1/chat', json={
                'session_id': session_id,
                'message': '测试消息'
            })
        
        # 再次检查消息数量
        info_response = client.get(f'/api/v1/sessions/{session_id}')
        info_data = info_response.get_json()
        assert info_data['message_count'] == 2  # 用户消息 + 助手回复