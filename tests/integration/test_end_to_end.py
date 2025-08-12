"""
端到端集成测试

测试整个系统的完整工作流程。
"""

import pytest
import json
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


class TestEndToEnd:
    """端到端测试"""
    
    def test_complete_workflow(self, client):
        """测试完整的工作流程"""
        # 1. 检查服务状态
        response = client.get('/')
        assert response.status_code == 200
        data = response.get_json()
        assert data['service'] == "Amazon Q CLI API Service"
        
        # 2. 检查健康状态
        with patch('qcli_api_service.services.qcli_service.qcli_service.is_available') as mock_available:
            mock_available.return_value = True
            
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
        
        # 3. 创建会话
        response = client.post('/api/v1/sessions')
        assert response.status_code == 201
        session_data = response.get_json()
        session_id = session_data['session_id']
        assert session_id is not None
        
        # 4. 进行多轮对话
        with patch('qcli_api_service.services.qcli_service.qcli_service.chat') as mock_chat:
            # 第一轮对话
            mock_chat.return_value = "你好！我是AI助手，很高兴为您服务。"
            
            response = client.post('/api/v1/chat', json={
                'session_id': session_id,
                'message': '你好，请介绍一下自己'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['session_id'] == session_id
            assert '你好！我是AI助手' in data['message']
            
            # 第二轮对话 - 测试上下文保持
            mock_chat.return_value = "当然可以！我刚才说了我是AI助手，我可以帮助您解答问题。"
            
            response = client.post('/api/v1/chat', json={
                'session_id': session_id,
                'message': '你能重复一下刚才说的话吗？'
            })
            
            assert response.status_code == 200
            data = response.get_json()
            assert '我刚才说了' in data['message']
            
            # 验证上下文被正确传递
            assert mock_chat.call_count == 2
            second_call_args = mock_chat.call_args_list[1]
            _, context = second_call_args[0]
            assert '你好，请介绍一下自己' in context
            assert '你好！我是AI助手' in context
        
        # 5. 查看会话信息
        response = client.get(f'/api/v1/sessions/{session_id}')
        assert response.status_code == 200
        session_info = response.get_json()
        assert session_info['session_id'] == session_id
        assert session_info['message_count'] == 4  # 2轮对话 = 4条消息
        
        # 6. 删除会话
        response = client.delete(f'/api/v1/sessions/{session_id}')
        assert response.status_code == 200
        
        # 7. 验证会话已删除
        response = client.get(f'/api/v1/sessions/{session_id}')
        assert response.status_code == 404
    
    def test_stream_workflow(self, client):
        """测试流式对话工作流程"""
        # 创建会话
        response = client.post('/api/v1/sessions')
        session_id = response.get_json()['session_id']
        
        # 流式对话
        with patch('qcli_api_service.services.qcli_service.qcli_service.stream_chat') as mock_stream:
            mock_stream.return_value = iter([
                "这是第一部分回复，",
                "这是第二部分回复，",
                "这是最后一部分回复。"
            ])
            
            response = client.post('/api/v1/chat/stream', json={
                'session_id': session_id,
                'message': '请给我一个详细的回答'
            })
            
            assert response.status_code == 200
            assert response.mimetype == 'text/event-stream'
            
            # 读取流式响应
            response_data = b''.join(response.response).decode('utf-8')
            
            # 验证包含会话ID
            assert session_id in response_data
            
            # 验证包含回复内容
            assert '第一部分回复' in response_data
            assert '第二部分回复' in response_data
            assert '最后一部分回复' in response_data
            
            # 验证包含完成信号
            assert "'type': 'done'" in response_data
        
        # 验证消息已保存到会话
        response = client.get(f'/api/v1/sessions/{session_id}')
        session_info = response.get_json()
        assert session_info['message_count'] == 2  # 用户消息 + 助手回复
    
    def test_error_handling_workflow(self, client):
        """测试错误处理工作流程"""
        # 1. 测试无效请求
        response = client.post('/api/v1/chat', json={
            'message': ''  # 空消息
        })
        assert response.status_code == 400
        data = response.get_json()
        assert '消息内容不能为空' in data['error']
        
        # 2. 测试不存在的会话（使用有效UUID格式）
        response = client.post('/api/v1/chat', json={
            'session_id': '550e8400-e29b-41d4-a716-446655440000',
            'message': '你好'
        })
        assert response.status_code == 404
        data = response.get_json()
        assert '会话不存在' in data['error']
        
        # 3. 测试Q CLI错误
        with patch('qcli_api_service.services.qcli_service.qcli_service.chat') as mock_chat:
            mock_chat.side_effect = RuntimeError("Q CLI连接失败")
            
            response = client.post('/api/v1/chat', json={
                'message': '你好'
            })
            assert response.status_code == 503
            data = response.get_json()
            assert 'AI处理失败' in data['error']
        
        # 4. 测试404错误
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == '接口不存在'
    
    def test_concurrent_sessions(self, client):
        """测试并发会话处理"""
        # 创建多个会话
        sessions = []
        for i in range(3):
            response = client.post('/api/v1/sessions')
            session_id = response.get_json()['session_id']
            sessions.append(session_id)
        
        # 在不同会话中并发对话
        with patch('qcli_api_service.services.qcli_service.qcli_service.chat') as mock_chat:
            mock_chat.side_effect = [
                f"会话{i}的回复" for i in range(3)
            ]
            
            responses = []
            for i, session_id in enumerate(sessions):
                response = client.post('/api/v1/chat', json={
                    'session_id': session_id,
                    'message': f'会话{i}的消息'
                })
                responses.append(response)
            
            # 验证所有响应都成功
            for i, response in enumerate(responses):
                assert response.status_code == 200
                data = response.get_json()
                assert f'会话{i}的回复' in data['message']
                assert data['session_id'] == sessions[i]
        
        # 验证会话隔离
        for i, session_id in enumerate(sessions):
            response = client.get(f'/api/v1/sessions/{session_id}')
            session_info = response.get_json()
            assert session_info['message_count'] == 2  # 每个会话1轮对话
    
    def test_message_validation_workflow(self, client):
        """测试消息验证工作流程"""
        # 创建会话
        response = client.post('/api/v1/sessions')
        session_id = response.get_json()['session_id']
        
        # 测试各种无效消息
        invalid_messages = [
            '',  # 空消息
            '   \n\t  ',  # 只有空白字符
            'a' * 4001,  # 过长消息
            '<script>alert("xss")</script>',  # 恶意内容
        ]
        
        for invalid_msg in invalid_messages:
            response = client.post('/api/v1/chat', json={
                'session_id': session_id,
                'message': invalid_msg
            })
            assert response.status_code == 400
            data = response.get_json()
            assert 'error' in data
        
        # 测试有效消息
        with patch('qcli_api_service.services.qcli_service.qcli_service.chat') as mock_chat:
            mock_chat.return_value = "这是有效的回复"
            
            response = client.post('/api/v1/chat', json={
                'session_id': session_id,
                'message': '这是一个有效的消息'
            })
            assert response.status_code == 200
    
    def test_service_degradation(self, client):
        """测试服务降级场景"""
        # 模拟Q CLI不可用
        with patch('qcli_api_service.services.qcli_service.qcli_service.is_available') as mock_available:
            mock_available.return_value = False
            
            # 健康检查应该显示降级状态
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'degraded'
            assert data['qcli_available'] is False
            
            # 但其他功能应该仍然可用
            response = client.post('/api/v1/sessions')
            assert response.status_code == 201
            
            response = client.get('/')
            assert response.status_code == 200