"""
Flask应用工厂 - 核心版本

创建和配置Flask应用实例。
"""

import logging
import json
from flask import Flask, jsonify, Response
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
                "health": "/health"
            }
        }
    
    return app


def register_error_handlers(app: Flask) -> None:
    """注册错误处理器"""
    
    @app.errorhandler(404)
    def not_found(error):
        response = app.custom_jsonify({
            "error": "接口不存在",
            "code": 404
        })
        response.status_code = 404
        return response
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        response = app.custom_jsonify({
            "error": "请求方法不允许",
            "code": 405
        })
        response.status_code = 405
        return response
    
    @app.errorhandler(500)
    def internal_error(error):
        response = app.custom_jsonify({
            "error": "内部服务器错误",
            "code": 500
        })
        response.status_code = 500
        return response