import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ErrorHandler } from '../errorHandler';
import { ErrorType, AppError } from '@/types/errors';

// 模拟 antd notification
vi.mock('antd', () => ({
  notification: {
    error: vi.fn(),
  },
}));

describe('ErrorHandler', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // 清除控制台输出
    vi.spyOn(console, 'error').mockImplementation(() => {});
    vi.spyOn(console, 'log').mockImplementation(() => {});
  });

  describe('createError', () => {
    it('应该创建基本的应用错误对象', () => {
      const error = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '测试错误消息'
      );

      expect(error).toMatchObject({
        type: ErrorType.API_ERROR,
        message: '测试错误消息',
        timestamp: expect.any(Number),
        stack: expect.any(String),
      });
    });

    it('应该包含错误详情', () => {
      const details = { endpoint: '/api/test', status: 500 };
      const error = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '测试错误',
        details
      );

      expect(error.details).toEqual(details);
    });
  });

  describe('createApiError', () => {
    it('应该创建 API 错误', () => {
      const details = {
        endpoint: '/api/chat',
        method: 'POST',
        status: 400,
        statusText: 'Bad Request',
      };

      const error = ErrorHandler.createApiError('API 调用失败', details);

      expect(error.type).toBe(ErrorType.API_ERROR);
      expect(error.message).toBe('API 调用失败');
      expect(error.details).toEqual(details);
    });
  });

  describe('createNetworkError', () => {
    it('应该创建网络错误', () => {
      const details = {
        url: 'http://localhost:8080/api/chat',
        timeout: 30000,
      };

      const error = ErrorHandler.createNetworkError('网络连接失败', details);

      expect(error.type).toBe(ErrorType.NETWORK_ERROR);
      expect(error.message).toBe('网络连接失败');
      expect(error.details).toEqual(details);
    });
  });

  describe('createFileError', () => {
    it('应该创建文件错误', () => {
      const details = {
        filename: 'test.txt',
        size: 1024,
        type: 'text/plain',
        operation: 'upload' as const,
      };

      const error = ErrorHandler.createFileError('文件上传失败', details);

      expect(error.type).toBe(ErrorType.FILE_ERROR);
      expect(error.message).toBe('文件上传失败');
      expect(error.details).toEqual(details);
    });
  });

  describe('createValidationError', () => {
    it('应该创建验证错误', () => {
      const details = {
        field: 'message',
        value: '',
        rule: 'required',
      };

      const error = ErrorHandler.createValidationError('字段验证失败', details);

      expect(error.type).toBe(ErrorType.VALIDATION_ERROR);
      expect(error.message).toBe('字段验证失败');
      expect(error.details).toEqual(details);
    });
  });

  describe('handle', () => {
    it('应该处理错误并显示通知', async () => {
      const { notification } = await import('antd');
      const error: AppError = {
        name: 'AppError',
        type: ErrorType.API_ERROR,
        message: '测试错误',
        timestamp: Date.now(),
      };

      ErrorHandler.handle(error);

      expect(notification.error).toHaveBeenCalledWith({
        message: 'API 调用失败',
        description: '测试错误',
        duration: 4.5,
        placement: 'topRight',
      });
    });

    it('应该根据选项控制行为', async () => {
      const { notification } = await import('antd');
      const error: AppError = {
        name: 'AppError',
        type: ErrorType.NETWORK_ERROR,
        message: '网络错误',
        timestamp: Date.now(),
      };

      ErrorHandler.handle(error, {
        showNotification: false,
        logToConsole: false,
      });

      expect(notification.error).not.toHaveBeenCalled();
      expect(console.error).not.toHaveBeenCalled();
    });
  });

  describe('fromHttpResponse', () => {
    it('应该从 HTTP 响应创建错误', async () => {
      const mockResponse = {
        status: 400,
        statusText: 'Bad Request',
        json: vi.fn().mockResolvedValue({
          error_message: 'API 错误消息',
        }),
      } as unknown as Response;

      const error = await ErrorHandler.fromHttpResponse(
        mockResponse,
        '/api/chat',
        'POST'
      );

      expect(error.type).toBe(ErrorType.API_ERROR);
      expect(error.message).toBe('API 错误消息');
      expect(error.details).toMatchObject({
        endpoint: '/api/chat',
        method: 'POST',
        status: 400,
        statusText: 'Bad Request',
      });
    });

    it('应该处理非 JSON 响应', async () => {
      const mockResponse = {
        status: 500,
        statusText: 'Internal Server Error',
        json: vi.fn().mockRejectedValue(new Error('Not JSON')),
      } as unknown as Response;

      const error = await ErrorHandler.fromHttpResponse(
        mockResponse,
        '/api/chat',
        'POST'
      );

      expect(error.type).toBe(ErrorType.API_ERROR);
      expect(error.message).toBe('HTTP 500: Internal Server Error');
    });
  });

  describe('fromJavaScriptError', () => {
    it('应该从 JavaScript 错误创建应用错误', () => {
      const jsError = new Error('JavaScript 错误');
      const error = ErrorHandler.fromJavaScriptError(jsError, ErrorType.VALIDATION_ERROR);

      expect(error.type).toBe(ErrorType.VALIDATION_ERROR);
      expect(error.message).toBe('JavaScript 错误');
      expect(error.stack).toBe(jsError.stack);
    });

    it('应该使用默认错误类型', () => {
      const jsError = new Error('未知错误');
      const error = ErrorHandler.fromJavaScriptError(jsError);

      expect(error.type).toBe(ErrorType.UNKNOWN_ERROR);
    });
  });
});