"""
API控制器 - 核心版本

处理HTTP请求和响应。
"""

import logging
import time
import json
from flask import request, jsonify, Response, stream_with_context, current_app
from qcli_api_service.models.core import ChatRequest, ChatResponse, ErrorResponse, Message
from qcli_api_service.services.session_manager import session_manager
from qcli_api_service.services.qcli_service import qcli_service
from qcli_api_service.utils.validators import input_validator


logger = logging.getLogger(__name__)


def chat():
    """标准聊天接口"""
    try:
        # 解析请求
        data = request.get_json(force=True, silent=True)
        if not data:
            return _error_response("请求体不能为空", 400)
        
        # 验证请求数据
        is_valid, error_msg = input_validator.validate_request_data(data)
        if not is_valid:
            return _error_response(error_msg, 400)
        
        # 创建请求对象
        chat_request = ChatRequest(
            session_id=data.get('session_id'),
            message=input_validator.clean_message(data.get('message', '')),
            stream=data.get('stream', False)
        )
        
        # 获取或创建会话
        session = None
        if chat_request.session_id:
            session = session_manager.get_session(chat_request.session_id)
            if not session:
                return _error_response("会话不存在", 404)
        else:
            session = session_manager.create_session()
            chat_request.session_id = session.session_id
        
        # 添加用户消息到会话
        user_message = Message.create_user_message(chat_request.message)
        session_manager.add_message(session.session_id, user_message)
        
        # 获取对话上下文
        context = session_manager.get_context(session.session_id)
        
        # 调用Q CLI
        try:
            response_text = qcli_service.chat(chat_request.message, context)
        except RuntimeError as e:
            return _error_response(f"AI处理失败: {str(e)}", 503)
        
        # 添加助手回复到会话
        assistant_message = Message.create_assistant_message(response_text)
        session_manager.add_message(session.session_id, assistant_message)
        
        # 返回响应
        response = ChatResponse.create(session.session_id, response_text)
        
        # 创建响应，确保中文正确显示
        response_data = {
            "session_id": response.session_id,
            "message": response.message,
            "timestamp": response.timestamp
        }
        
        # 使用自定义JSON响应函数
        return current_app.custom_jsonify(response_data)
        
    except Exception as e:
        logger.error(f"聊天接口错误: {e}")
        return _error_response("内部服务器错误", 500)


def stream_chat():
    """流式聊天接口"""
    try:
        # 解析请求
        data = request.get_json(force=True, silent=True)
        if not data:
            return _error_response("请求体不能为空", 400)
        
        # 验证请求数据
        is_valid, error_msg = input_validator.validate_request_data(data)
        if not is_valid:
            return _error_response(error_msg, 400)
        
        # 创建请求对象
        chat_request = ChatRequest(
            session_id=data.get('session_id'),
            message=input_validator.clean_message(data.get('message', '')),
            stream=True
        )
        
        # 获取或创建会话
        session = None
        if chat_request.session_id:
            session = session_manager.get_session(chat_request.session_id)
            if not session:
                return _error_response("会话不存在", 404)
        else:
            session = session_manager.create_session()
            chat_request.session_id = session.session_id
        
        # 添加用户消息到会话
        user_message = Message.create_user_message(chat_request.message)
        session_manager.add_message(session.session_id, user_message)
        
        # 获取对话上下文
        context = session_manager.get_context(session.session_id)
        
        # 创建流式响应
        def generate():
            try:
                # 发送会话ID
                yield f"data: {{'session_id': '{session.session_id}', 'type': 'session'}}\n\n"
                
                # 收集完整回复用于保存到会话
                full_response = []
                
                # 流式调用Q CLI
                for chunk in qcli_service.stream_chat(chat_request.message, context):
                    full_response.append(chunk)
                    # 发送数据块
                    yield f"data: {{'message': '{_escape_json(chunk)}', 'type': 'chunk'}}\n\n"
                
                # 发送完成信号
                yield f"data: {{'type': 'done'}}\n\n"
                
                # 保存完整回复到会话
                if full_response:
                    complete_response = "\n".join(full_response)
                    assistant_message = Message.create_assistant_message(complete_response)
                    session_manager.add_message(session.session_id, assistant_message)
                
            except RuntimeError as e:
                # 发送错误信息
                yield f"data: {{'error': '{_escape_json(str(e))}', 'type': 'error'}}\n\n"
            except Exception as e:
                logger.error(f"流式聊天错误: {e}")
                yield f"data: {{'error': '内部服务器错误', 'type': 'error'}}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        logger.error(f"流式聊天接口错误: {e}")
        return _error_response("内部服务器错误", 500)


def health():
    """健康检查接口"""
    try:
        # 检查Q CLI可用性
        qcli_available = qcli_service.is_available()
        
        # 获取基本统计信息
        active_sessions = session_manager.get_active_session_count()
        
        status = "healthy" if qcli_available else "degraded"
        
        return current_app.custom_jsonify({
            "status": status,
            "timestamp": time.time(),
            "qcli_available": qcli_available,
            "active_sessions": active_sessions,
            "version": "1.0.0"
        })
        
    except Exception as e:
        logger.error(f"健康检查错误: {e}")
        response_data = {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": str(e)
        }
        response = current_app.custom_jsonify(response_data)
        response.status_code = 500
        return response


def create_session():
    """创建会话接口"""
    try:
        session = session_manager.create_session()
        
        response_data = {
            "session_id": session.session_id,
            "created_at": session.created_at
        }
        response = current_app.custom_jsonify(response_data)
        response.status_code = 201
        return response
        
    except Exception as e:
        logger.error(f"创建会话错误: {e}")
        return _error_response("内部服务器错误", 500)


def get_session(session_id: str):
    """获取会话信息接口"""
    try:
        session_info = session_manager.get_session_info(session_id)
        
        if not session_info:
            return _error_response("会话不存在", 404)
        
        return current_app.custom_jsonify(session_info)
        
    except Exception as e:
        logger.error(f"获取会话错误: {e}")
        return _error_response("内部服务器错误", 500)


def delete_session(session_id: str):
    """删除会话接口"""
    try:
        success = session_manager.delete_session(session_id)
        
        if not success:
            return _error_response("会话不存在", 404)
        
        return current_app.custom_jsonify({"message": "会话已删除"})
        
    except Exception as e:
        logger.error(f"删除会话错误: {e}")
        return _error_response("内部服务器错误", 500)


def _error_response(message: str, code: int) -> tuple:
    """创建错误响应"""
    error = ErrorResponse(error=message, code=code)
    response = current_app.custom_jsonify(error.to_dict())
    response.status_code = code
    return response


def _escape_json(text: str) -> str:
    """转义JSON字符串中的特殊字符"""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')