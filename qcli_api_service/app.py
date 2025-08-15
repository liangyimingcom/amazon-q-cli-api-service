"""
Flask应用工厂 - 核心版本

创建和配置Flask应用实例。
"""

import logging
import json
from flask import Flask, jsonify, Response
from werkzeug.exceptions import BadRequest
from qcli_api_service.config import config
from qcli_api_service.api.routes import register_routes


def create_app() -> Flask:
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置Flask
    app.config['DEBUG'] = config.DEBUG
    app.config['TESTING'] = False
    # 确保JSON响应使用UTF-8编码，不转义非ASCII字符
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # 自定义JSON编码器，确保中文正确显示
    def custom_jsonify(data):
        """自定义JSON响应函数，确保中文正确显示"""
        response = Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json; charset=utf-8'
        )
        return response
    
    # 将自定义函数添加到应用上下文
    app.custom_jsonify = custom_jsonify
    
    # 设置日志
    if not app.debug:
        app.logger.setLevel(logging.INFO)
    
    # 注册路由
    register_routes(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 添加基本路由
    @app.route('/')
    def index():
        return {
            "service": "Amazon Q CLI API Service",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "chat": "/api/v1/chat",
                "stream_chat": "/api/v1/chat/stream",
                "sessions": "/api/v1/sessions",
                "session_files": "/api/v1/sessions/{session_id}/files",
                "health": "/health"
            }
        }
    
    return app


def register_error_handlers(app: Flask) -> None:
    """注册错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        # 检查是否是JSON解析错误
        if "Failed to decode JSON object" in str(error) or "No JSON object could be decoded" in str(error):
            response = app.custom_jsonify({
                "error": "请求体必须是有效的JSON格式",
                "code": "INVALID_JSON",
                "http_status": 400,
                "suggestions": [
                    "请检查JSON语法是否正确",
                    "确保使用双引号包围字符串",
                    "验证JSON格式是否完整"
                ]
            })
        else:
            response = app.custom_jsonify({
                "error": "请求格式错误",
                "code": "BAD_REQUEST", 
                "http_status": 400,
                "suggestions": [
                    "请检查请求体是否为有效的JSON格式",
                    "确保Content-Type设置为application/json",
                    "参考API文档了解正确的请求格式"
                ]
            })
        response.status_code = 400
        return response
    
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        response = app.custom_jsonify({
            "error": "请求体格式错误或为空",
            "code": "EMPTY_OR_INVALID_REQUEST",
            "http_status": 400,
            "suggestions": [
                "请确保请求体不为空",
                "请检查JSON格式是否正确",
                "确保Content-Type设置为application/json"
            ]
        })
        response.status_code = 400
        return response
    
    @app.errorhandler(404)
    def not_found(error):
        response = app.custom_jsonify({
            "error": "请求的接口不存在",
            "code": "ENDPOINT_NOT_FOUND",
            "http_status": 404,
            "suggestions": [
                "请检查请求URL是否正确",
                "确认API版本号是否正确",
                "参考API文档了解可用的接口"
            ]
        })
        response.status_code = 404
        return response
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        response = app.custom_jsonify({
            "error": "请求方法不被允许",
            "code": "METHOD_NOT_ALLOWED",
            "http_status": 405,
            "suggestions": [
                "请检查HTTP方法是否正确（GET、POST等）",
                "确认接口支持的请求方法",
                "参考API文档了解正确的请求方式"
            ]
        })
        response.status_code = 405
        return response
    
    @app.errorhandler(500)
    def internal_error(error):
        response = app.custom_jsonify({
            "error": "服务器内部错误",
            "code": "INTERNAL_SERVER_ERROR",
            "http_status": 500,
            "suggestions": [
                "这是服务器内部错误，请稍后重试",
                "如果问题持续存在，请联系技术支持",
                "请提供错误发生的时间以便排查"
            ]
        })
        response.status_code = 500
        return response