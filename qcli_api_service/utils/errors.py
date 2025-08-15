"""
统一错误处理模块

提供统一的错误定义、处理和响应机制。
"""

from typing import Dict, List, Optional
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API错误基类"""
    
    def __init__(
        self, 
        message: str, 
        code: str, 
        http_status: int = 500,
        details: Optional[Dict] = None,
        suggestions: Optional[List[str]] = None,
        user_friendly: bool = True
    ):
        self.message = message
        self.code = code
        self.http_status = http_status
        self.details = details or {}
        self.suggestions = suggestions or []
        self.user_friendly = user_friendly
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        result = {
            "error": self.message,
            "code": self.code,
            "http_status": self.http_status
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.suggestions:
            result["suggestions"] = self.suggestions
        
        return result
    
    def to_response(self):
        """转换为Flask响应"""
        response = current_app.custom_jsonify(self.to_dict())
        response.status_code = self.http_status
        return response


class ValidationError(APIError):
    """请求验证错误"""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        
        suggestions = [
            "请检查请求参数格式是否正确",
            "确保所有必需字段都已提供",
            "参考API文档了解正确的请求格式"
        ]
        
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            http_status=400,
            details=details,
            suggestions=suggestions
        )


class SessionError(APIError):
    """会话相关错误"""
    
    def __init__(self, message: str, session_id: str = None, error_type: str = "NOT_FOUND"):
        details = {}
        if session_id:
            details["session_id"] = session_id
        
        suggestions = []
        if error_type == "NOT_FOUND":
            suggestions = [
                "请检查会话ID是否正确",
                "会话可能已过期，请创建新会话",
                "使用 POST /api/v1/sessions 创建新会话"
            ]
        elif error_type == "EXPIRED":
            suggestions = [
                "会话已过期，请创建新会话",
                "可以通过配置延长会话有效期"
            ]
        
        super().__init__(
            message=message,
            code=f"SESSION_{error_type}",
            http_status=404 if error_type == "NOT_FOUND" else 410,
            details=details,
            suggestions=suggestions
        )


class ServiceError(APIError):
    """服务相关错误"""
    
    def __init__(self, message: str, service: str = "QCLI", error_type: str = "UNAVAILABLE"):
        details = {"service": service}
        
        suggestions = []
        if service == "QCLI":
            if error_type == "UNAVAILABLE":
                suggestions = [
                    "请确认Amazon Q CLI已正确安装",
                    "检查AWS凭证配置是否正确",
                    "尝试运行 'q --version' 验证CLI可用性",
                    "如果问题持续，请联系系统管理员"
                ]
            elif error_type == "TIMEOUT":
                suggestions = [
                    "AI处理复杂问题需要较长时间，请耐心等待",
                    "尝试简化问题或分解为多个小问题",
                    "检查网络连接是否稳定",
                    "如果经常超时，请联系系统管理员调整超时设置"
                ]
            elif error_type == "AUTH_ERROR":
                suggestions = [
                    "请检查AWS凭证配置",
                    "确认AWS账户有使用Amazon Q的权限",
                    "尝试重新配置AWS CLI凭证",
                    "联系AWS管理员检查权限设置"
                ]
        
        super().__init__(
            message=message,
            code=f"{service}_{error_type}",
            http_status=503 if error_type == "UNAVAILABLE" else 408 if error_type == "TIMEOUT" else 401,
            details=details,
            suggestions=suggestions
        )


class InternalError(APIError):
    """内部系统错误"""
    
    def __init__(self, message: str = "系统内部错误", original_error: Exception = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        
        suggestions = [
            "这是系统内部错误，请稍后重试",
            "如果问题持续存在，请联系技术支持",
            "请提供错误发生的时间和操作步骤以便排查"
        ]
        
        super().__init__(
            message=message,
            code="INTERNAL_ERROR",
            http_status=500,
            details=details,
            suggestions=suggestions,
            user_friendly=True
        )


class RateLimitError(APIError):
    """请求频率限制错误"""
    
    def __init__(self, message: str = "请求过于频繁", retry_after: int = 60):
        details = {"retry_after": retry_after}
        
        suggestions = [
            f"请等待 {retry_after} 秒后重试",
            "避免短时间内发送大量请求",
            "考虑使用批量处理减少请求频率"
        ]
        
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            http_status=429,
            details=details,
            suggestions=suggestions
        )


# 错误处理工具函数
def handle_qcli_error(error: Exception) -> APIError:
    """处理Q CLI相关错误"""
    error_msg = str(error)
    
    if "超时" in error_msg or "timeout" in error_msg.lower():
        return ServiceError(
            message="AI处理超时，请稍后重试",
            service="QCLI",
            error_type="TIMEOUT"
        )
    elif "不可用" in error_msg or "unavailable" in error_msg.lower():
        return ServiceError(
            message="Amazon Q CLI服务暂时不可用",
            service="QCLI",
            error_type="UNAVAILABLE"
        )
    elif "权限" in error_msg or "permission" in error_msg.lower() or "auth" in error_msg.lower():
        return ServiceError(
            message="AWS认证失败，请检查凭证配置",
            service="QCLI",
            error_type="AUTH_ERROR"
        )
    else:
        return ServiceError(
            message=f"AI处理失败: {error_msg}",
            service="QCLI",
            error_type="PROCESSING_ERROR"
        )


def handle_validation_error(field: str, value: str, reason: str) -> ValidationError:
    """处理验证错误"""
    message = f"字段 '{field}' 验证失败: {reason}"
    return ValidationError(message, field=field, value=value)


def log_error(error: APIError, request_info: Dict = None):
    """记录错误日志"""
    log_data = {
        "error_code": error.code,
        "error_message": error.message,
        "http_status": error.http_status,
        "details": error.details
    }
    
    if request_info:
        log_data.update(request_info)
    
    if error.http_status >= 500:
        logger.error(f"Internal error: {log_data}")
    elif error.http_status >= 400:
        logger.warning(f"Client error: {log_data}")
    else:
        logger.info(f"API error: {log_data}")


# 常用错误实例
ERRORS = {
    "EMPTY_REQUEST": ValidationError("请求体不能为空"),
    "INVALID_JSON": ValidationError("请求体必须是有效的JSON格式"),
    "MISSING_MESSAGE": ValidationError("消息内容不能为空", field="message"),
    "MESSAGE_TOO_LONG": ValidationError("消息内容过长，请控制在1000字符以内", field="message"),
    "INVALID_SESSION_ID": ValidationError("会话ID格式无效", field="session_id"),
    "SESSION_NOT_FOUND": SessionError("指定的会话不存在"),
    "QCLI_UNAVAILABLE": ServiceError("Amazon Q CLI服务不可用", service="QCLI", error_type="UNAVAILABLE"),
    "INTERNAL_ERROR": InternalError()
}