"""
API控制器 - 修复版本

使用会话记忆功能的控制器实现。
"""

import logging
import time
import json
import os
from flask import request, jsonify, Response, stream_with_context, current_app
from qcli_api_service.models.core import ChatRequest, ChatResponse, Message
from qcli_api_service.services.session_manager import session_manager
from qcli_api_service.utils.validators import input_validator
from qcli_api_service.utils.errors import (
    APIError, ValidationError, SessionError, ServiceError, InternalError,
    handle_qcli_error, log_error, ERRORS
)

# 导入修复后的服务
import sys
sys.path.append(os.path.dirname(__file__))
from qcli_service_fixed import qcli_service

logger = logging.getLogger(__name__)


def stream_chat():
    """流式聊天接口 - 修复版本"""
    try:
        # 解析请求
        data = request.get_json(force=True, silent=True)
        if data is None:
            error = ERRORS["EMPTY_REQUEST"]
            log_error(error, {"endpoint": "/api/v1/chat/stream", "method": "POST"})
            return error.to_response()
        
        # 验证请求数据
        is_valid, error_msg = input_validator.validate_request_data(data)
        if not is_valid:
            error = ValidationError(error_msg)
            log_error(error, {"endpoint": "/api/v1/chat/stream", "method": "POST", "data": data})
            return error.to_response()
        
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
                error = SessionError("指定的会话不存在", session_id=chat_request.session_id)
                log_error(error, {"endpoint": "/api/v1/chat/stream", "session_id": chat_request.session_id})
                return error.to_response()
        else:
            session = session_manager.create_session()
            chat_request.session_id = session.session_id
        
        # 添加用户消息到会话（用于日志记录）
        user_message = Message.create_user_message(chat_request.message)
        session_manager.add_message(session.session_id, user_message)
        
        # 获取对话上下文（仅用于日志记录，不发送给Q Chat）
        context = session_manager.get_context(session.session_id)
        logger.info(f"会话 {session.session_id} 上下文长度: {len(context)} 字符（仅用于日志）")
        
        # 创建流式响应
        def generate():
            try:
                # 发送会话ID
                yield f"data: {{'session_id': '{session.session_id}', 'type': 'session'}}\n\n"
                
                # 收集完整回复用于保存到会话
                full_response = []
                
                # 流式调用Q CLI（使用会话记忆，不发送历史上下文）
                for chunk in qcli_service.stream_chat(
                    chat_request.message, 
                    session.session_id,  # 传递会话ID而不是上下文
                    work_directory=session.work_directory
                ):
                    full_response.append(chunk)
                    # 发送数据块
                    yield f"data: {{'message': '{_escape_json(chunk)}', 'type': 'chunk'}}\n\n"
                
                # 发送完成信号
                yield f"data: {{'type': 'done'}}\n\n"
                
                # 保存完整回复到会话（用于日志记录）
                if full_response:
                    complete_response = "\n".join(full_response)
                    assistant_message = Message.create_assistant_message(complete_response)
                    session_manager.add_message(session.session_id, assistant_message)
                
            except RuntimeError as e:
                # 处理Q CLI错误
                error = handle_qcli_error(e)
                log_error(error, {
                    "endpoint": "/api/v1/chat/stream", 
                    "session_id": session.session_id,
                    "message_length": len(chat_request.message)
                })
                # 发送详细错误信息
                error_data = {
                    'error': error.message,
                    'code': error.code,
                    'suggestions': error.suggestions,
                    'type': 'error'
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            except Exception as e:
                error = InternalError("流式聊天内部错误", original_error=e)
                log_error(error, {"endpoint": "/api/v1/chat/stream", "session_id": session.session_id})
                error_data = {
                    'error': error.message,
                    'code': error.code,
                    'suggestions': error.suggestions,
                    'type': 'error'
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
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
        
    except APIError as e:
        # API错误已经处理过了，直接返回
        return e.to_response()
    except Exception as e:
        error = InternalError("流式聊天服务内部错误", original_error=e)
        log_error(error, {"endpoint": "/api/v1/chat/stream", "method": "POST"})
        return error.to_response()


def chat():
    """标准聊天接口 - 修复版本"""
    try:
        # 解析请求
        data = request.get_json(force=True, silent=True)
        if data is None:
            error = ERRORS["EMPTY_REQUEST"]
            log_error(error, {"endpoint": "/api/v1/chat", "method": "POST"})
            return error.to_response()
        
        # 验证请求数据
        is_valid, error_msg = input_validator.validate_request_data(data)
        if not is_valid:
            error = ValidationError(error_msg)
            log_error(error, {"endpoint": "/api/v1/chat", "method": "POST", "data": data})
            return error.to_response()
        
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
                error = SessionError("指定的会话不存在", session_id=chat_request.session_id)
                log_error(error, {"endpoint": "/api/v1/chat", "session_id": chat_request.session_id})
                return error.to_response()
        else:
            session = session_manager.create_session()
            chat_request.session_id = session.session_id
        
        # 添加用户消息到会话（用于日志记录）
        user_message = Message.create_user_message(chat_request.message)
        session_manager.add_message(session.session_id, user_message)
        
        # 获取对话上下文（仅用于日志记录）
        context = session_manager.get_context(session.session_id)
        logger.info(f"会话 {session.session_id} 上下文长度: {len(context)} 字符（仅用于日志）")
        
        # 调用Q CLI（使用会话记忆）
        try:
            response_text = qcli_service.chat(
                chat_request.message, 
                session.session_id,  # 传递会话ID而不是上下文
                work_directory=session.work_directory
            )
        except RuntimeError as e:
            error = handle_qcli_error(e)
            log_error(error, {
                "endpoint": "/api/v1/chat", 
                "session_id": session.session_id,
                "message_length": len(chat_request.message)
            })
            return error.to_response()
        
        # 添加助手回复到会话（用于日志记录）
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
        
    except APIError as e:
        # API错误已经处理过了，直接返回
        return e.to_response()
    except Exception as e:
        error = InternalError("聊天服务内部错误", original_error=e)
        log_error(error, {"endpoint": "/api/v1/chat", "method": "POST"})
        return error.to_response()


def delete_session(session_id: str):
    """删除会话接口 - 修复版本"""
    try:
        # 清理Q Chat进程
        qcli_service.cleanup_session(session_id)
        
        # 删除会话数据
        success = session_manager.delete_session(session_id)
        
        if not success:
            error = SessionError("指定的会话不存在", session_id=session_id)
            log_error(error, {"endpoint": f"/api/v1/sessions/{session_id}", "method": "DELETE"})
            return error.to_response()
        
        return current_app.custom_jsonify({"message": "会话已删除"})
        
    except Exception as e:
        error = InternalError("删除会话失败", original_error=e)
        log_error(error, {"endpoint": f"/api/v1/sessions/{session_id}", "method": "DELETE"})
        return error.to_response()


def _escape_json(text: str) -> str:
    """转义JSON字符串中的特殊字符"""
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')