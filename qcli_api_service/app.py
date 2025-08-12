"""
Flask应用工厂 - 核心版本

创建和配置Flask应用实例。
"""

import logging
from flask import Flask, jsonify
from qcli_api_service.config import config
from qcli_api_service.api.routes import register_routes


def create_app() -> Flask:
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置Flask
    app.config['DEBUG'] = config.DEBUG
    app.config['TESTING'] = False
    
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
        return jsonify({
            "error": "接口不存在",
            "code": 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "error": "请求方法不允许",
            "code": 405
        }), 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "内部服务器错误",
            "code": 500
        }), 500