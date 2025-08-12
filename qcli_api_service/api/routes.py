"""
API路由配置 - 核心版本

定义所有API端点的路由。
"""

from flask import Blueprint
from qcli_api_service.api import controllers


# 创建API蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')


# 聊天相关路由
api_bp.add_url_rule('/chat', 'chat', controllers.chat, methods=['POST'])
api_bp.add_url_rule('/chat/stream', 'stream_chat', controllers.stream_chat, methods=['POST'])

# 会话管理路由
api_bp.add_url_rule('/sessions', 'create_session', controllers.create_session, methods=['POST'])
api_bp.add_url_rule('/sessions/<session_id>', 'get_session', controllers.get_session, methods=['GET'])
api_bp.add_url_rule('/sessions/<session_id>', 'delete_session', controllers.delete_session, methods=['DELETE'])


# 创建健康检查蓝图
health_bp = Blueprint('health', __name__)
health_bp.add_url_rule('/health', 'health', controllers.health, methods=['GET'])


def register_routes(app):
    """注册所有路由到Flask应用"""
    app.register_blueprint(api_bp)
    app.register_blueprint(health_bp)