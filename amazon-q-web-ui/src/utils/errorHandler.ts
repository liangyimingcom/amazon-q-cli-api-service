import { notification } from 'antd';
import { 
  AppError, 
  ErrorType, 
  ErrorHandlerOptions,
  ApiErrorDetails,
  FileErrorDetails,
  NetworkErrorDetails,
  ValidationErrorDetails
} from '@/types/errors';

// 重新导出 ErrorType 以便其他模块使用
export { ErrorType } from '@/types/errors';

/**
 * 错误处理器类
 * 统一处理应用中的各种错误
 */
export class ErrorHandler {
  /**
   * 处理应用错误
   * @param error 应用错误对象
   * @param options 处理选项
   */
  static handle(error: AppError, options: ErrorHandlerOptions = {}): void {
    const {
      showNotification = true,
      logToConsole = true,
      reportToService = false,
      retryable = false,
    } = options;

    // 记录错误到控制台
    if (logToConsole) {
      console.error('应用错误:', error);
    }

    // 显示用户友好的错误通知
    if (showNotification) {
      this.showErrorNotification(error, retryable);
    }

    // 上报错误到服务端（可选）
    if (reportToService) {
      this.reportError(error);
    }
  }

  /**
   * 创建应用错误对象
   * @param type 错误类型
   * @param message 错误消息
   * @param details 错误详情
   * @returns 应用错误对象
   */
  static createError(
    type: ErrorType,
    message: string,
    details?: any
  ): AppError {
    return {
      name: 'AppError',
      type,
      message,
      details,
      timestamp: Date.now(),
      stack: new Error().stack,
    };
  }

  /**
   * 创建 API 错误
   * @param message 错误消息
   * @param details API 错误详情
   * @returns 应用错误对象
   */
  static createApiError(
    message: string,
    details: ApiErrorDetails
  ): AppError {
    return this.createError(ErrorType.API_ERROR, message, details);
  }

  /**
   * 创建网络错误
   * @param message 错误消息
   * @param details 网络错误详情
   * @returns 应用错误对象
   */
  static createNetworkError(
    message: string,
    details: NetworkErrorDetails
  ): AppError {
    return this.createError(ErrorType.NETWORK_ERROR, message, details);
  }

  /**
   * 创建文件错误
   * @param message 错误消息
   * @param details 文件错误详情
   * @returns 应用错误对象
   */
  static createFileError(
    message: string,
    details: FileErrorDetails
  ): AppError {
    return this.createError(ErrorType.FILE_ERROR, message, details);
  }

  /**
   * 创建验证错误
   * @param message 错误消息
   * @param details 验证错误详情
   * @returns 应用错误对象
   */
  static createValidationError(
    message: string,
    details: ValidationErrorDetails
  ): AppError {
    return this.createError(ErrorType.VALIDATION_ERROR, message, details);
  }

  /**
   * 显示错误通知
   * @param error 应用错误对象
   * @param retryable 是否可重试
   */
  private static showErrorNotification(
    error: AppError,
    retryable: boolean = false
  ): void {
    const { type, message } = error;
    
    let title = '系统错误';
    let description = message;

    switch (type) {
      case ErrorType.NETWORK_ERROR:
        title = '网络连接错误';
        description = '请检查网络连接后重试';
        break;
        
      case ErrorType.API_ERROR:
        title = 'API 调用失败';
        description = message;
        break;
        
      case ErrorType.FILE_ERROR:
        title = '文件操作失败';
        description = message;
        break;
        
      case ErrorType.VALIDATION_ERROR:
        title = '输入验证失败';
        description = message;
        break;
        
      case ErrorType.SESSION_ERROR:
        title = '会话错误';
        description = message;
        break;
        
      case ErrorType.STREAM_ERROR:
        title = '流式传输错误';
        description = message;
        break;
        
      case ErrorType.TIMEOUT_ERROR:
        title = '请求超时';
        description = '请求处理时间过长，请稍后重试';
        break;
        
      default:
        title = '未知错误';
        description = '发生未知错误，请稍后重试';
    }

    notification.error({
      message: title,
      description,
      duration: retryable ? 0 : 4.5, // 可重试的错误不自动关闭
      placement: 'topRight',
    });
  }

  /**
   * 上报错误到服务端
   * @param error 应用错误对象
   */
  private static reportError(error: AppError): void {
    // 这里可以实现错误上报逻辑
    // 例如发送到错误监控服务
    try {
      // 简单的错误上报实现
      const errorReport = {
        type: error.type,
        message: error.message,
        timestamp: error.timestamp,
        userAgent: navigator.userAgent,
        url: window.location.href,
        details: error.details,
        stack: error.stack,
      };

      // 发送到错误收集服务
      // fetch('/api/errors', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(errorReport),
      // });

      console.log('错误报告:', errorReport);
    } catch (reportError) {
      console.error('错误上报失败:', reportError);
    }
  }

  /**
   * 从 HTTP 响应创建错误
   * @param response HTTP 响应对象
   * @param endpoint 请求端点
   * @param method 请求方法
   * @returns 应用错误对象
   */
  static async fromHttpResponse(
    response: Response,
    endpoint: string,
    method: string
  ): Promise<AppError> {
    let errorData: any = {};
    
    try {
      errorData = await response.json();
    } catch {
      // 如果响应不是 JSON 格式，使用默认错误信息
    }

    const details: ApiErrorDetails = {
      endpoint,
      method,
      status: response.status,
      statusText: response.statusText,
      data: errorData,
    };

    const message = errorData.error_message || 
                   errorData.message || 
                   `HTTP ${response.status}: ${response.statusText}`;

    return this.createApiError(message, details);
  }

  /**
   * 从 JavaScript 错误创建应用错误
   * @param jsError JavaScript 错误对象
   * @param type 错误类型
   * @returns 应用错误对象
   */
  static fromJavaScriptError(
    jsError: Error,
    type: ErrorType = ErrorType.UNKNOWN_ERROR
  ): AppError {
    return {
      name: jsError.name || 'AppError',
      type,
      message: jsError.message,
      timestamp: Date.now(),
      stack: jsError.stack,
    };
  }
}