"""
API接口集成测试
"""

import json
import pytest
from unittest.mock import patch, Mock
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


class TestAPI:
    """API接口测试"""
    
    def test_index(self, client):
        """测试首页接口"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['service'] == "Amazon Q CLI API Service"
        assert data['version'] == "1.0.0"
        assert 'endpoints' in data
    
    def test_health(self, client):
        """测试健康检查接口"""
        with patch('qcli_api_service.services.qcli_service.qcli_service.is_available') as mock_available:
            mock_available.return_value = True
            
            response = client.get('/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
            assert data['qcli_available'] is True
            assert 'active_sessions' in data
            assert 'timestamp' in data
    
    def test_health_degraded(self, client):
        """测试健康检查接口 - 降级状态"""
        with patch('qcli_api_service.services.qcli_service.qcli_service.is_available') as mock_available:
            mock_available.return_value = False
            
            response = client.get('/health')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'degraded'
            assert data['qcli_available'] is False
    
    def test_create_session(self, client):
        """测试创建会话接口"""
        response = client.post('/api/v1/sessions')
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'session_id' in data
        assert 'created_at' in data
        assert len(data['session_id']) > 0
    
    def test_get_session(self, client):
        """测试获取会话接口"""
        # 先创建会话
        create_response = client.post('/api/v1/sessions')
        session_id = create_response.get_json()['session_id']
        
        # 获取会话信息
        response = client.get(f'/api/v1/sessions/{session_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['session_id'] == session_id
        assert 'created_at' in data
        assert 'last_activity' in data
        assert 'message_count' in data
    
    def test_get_nonexistent_session(self, client):
        """测试获取不存在的会话"""
        response = client.get('/api/v1/sessions/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == '会话不存在'
    
    def test_delete_session(self, client):
        """测试删除会话接口"""
        # 先创建会话
        create_response = client.post('/api/v1/sessions')
        session_id = create_response.get_json()['session_id']
        
        # 删除会话
        response = client.delete(f'/api/v1/sessions/{session_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == '会话已删除'
        
        # 验证会话已删除
        get_response = client.get(f'/api/v1/sessions/{session_id}')
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_session(self, client):
        """测试删除不存在的会话"""
        response = client.delete('/api/v1/sessions/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == '会话不存在'
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_chat_with_new_session(self, mock_chat, client):
        """测试聊天接口 - 新会话"""
        mock_chat.return_value = "这是AI的回复"
        
        response = client.post('/api/v1/chat', 
                             json={'message': '你好'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'session_id' in data
        assert data['message'] == "这是AI的回复"
        assert 'timestamp' in data
        
        mock_chat.assert_called_once()
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_chat_with_existing_session(self, mock_chat, client):
        """测试聊天接口 - 现有会话"""
        mock_chat.return_value = "这是AI的回复"
        
        # 先创建会话
        create_response = client.post('/api/v1/sessions')
        session_id = create_response.get_json()['session_id']
        
        # 使用现有会话聊天
        response = client.post('/api/v1/chat', 
                             json={
                                 'session_id': session_id,
                                 'message': '你好'
                             })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['session_id'] == session_id
        assert data['message'] == "这是AI的回复"
    
    def test_chat_empty_message(self, client):
        """测试聊天接口 - 空消息"""
        response = client.post('/api/v1/chat', 
                             json={'message': ''})
        
        assert response.status_code == 400
        data = response.get_json()
        assert '消息内容不能为空' in data['error']
    
    def test_chat_no_json(self, client):
        """测试聊天接口 - 无JSON数据"""
        response = client.post('/api/v1/chat')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == '请求体不能为空'
    
    def test_chat_nonexistent_session(self, client):
        """测试聊天接口 - 不存在的会话"""
        response = client.post('/api/v1/chat', 
                             json={
                                 'session_id': '550e8400-e29b-41d4-a716-446655440000',
                                 'message': '你好'
                             })
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == '会话不存在'
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.chat')
    def test_chat_qcli_error(self, mock_chat, client):
        """测试聊天接口 - Q CLI错误"""
        mock_chat.side_effect = RuntimeError("Q CLI错误")
        
        response = client.post('/api/v1/chat', 
                             json={'message': '你好'})
        
        assert response.status_code == 503
        data = response.get_json()
        assert 'AI处理失败' in data['error']
    
    @patch('qcli_api_service.services.qcli_service.qcli_service.stream_chat')
    def test_stream_chat(self, mock_stream_chat, client):
        """测试流式聊天接口"""
        # 模拟流式输出
        mock_stream_chat.return_value = iter(["第一部分", "第二部分", "第三部分"])
        
        response = client.post('/api/v1/chat/stream', 
                             json={'message': '你好'})
        
        assert response.status_code == 200
        assert response.mimetype == 'text/event-stream'
        
        # 检查响应头
        assert response.headers.get('Cache-Control') == 'no-cache'
        assert response.headers.get('Connection') == 'keep-alive'
    
    def test_404_error(self, client):
        """测试404错误处理"""
        response = client.get('/nonexistent-endpoint')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['error'] == '接口不存在'
        assert data['code'] == 404
    
    def test_405_error(self, client):
        """测试405错误处理"""
        response = client.get('/api/v1/chat')  # 应该是POST
        
        assert response.status_code == 405
        data = response.get_json()
        assert data['error'] == '请求方法不允许'
        assert data['code'] == 405