
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';
import { getApiUrl } from '@/config';
import {
  APIClient,
  ChatResponse,
  SessionResponse,
  Session,
  FileItem,
  FileUploadResponse,
  HealthStatus,
  SystemStatus,
} from '@/types';

/**
 * API 客户端实现
 */
export class APIClientImpl implements APIClient {
  private baseURL: string;
  private timeout: number;
  private maxRetries: number;

  constructor(
    baseURL: string = getApiUrl(''),
    timeout: number = 650000, // 从30秒增加到650秒（10分50秒）
    maxRetries: number = 3
  ) {
    this.baseURL = baseURL.replace(/\/$/, ''); // 移除末尾斜杠
    this.timeout = timeout;
    this.maxRetries = maxRetries;
  }

  /**
   * 发送 HTTP 请求
   * @param endpoint 端点路径
   * @param options 请求选项
   * @returns 响应数据
   */
  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const {
      method = 'GET',
      headers = {},
      body,
      timeout = this.timeout,
      retries = this.maxRetries,
    } = options;

    const url = `${this.baseURL}${endpoint}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      signal: controller.signal,
    };

    if (body && method !== 'GET') {
      if (body instanceof FormData) {
        // 对于 FormData，移除 Content-Type 让浏览器自动设置
        delete requestHeaders['Content-Type'];
        requestOptions.body = body;
      } else {
        requestOptions.body = JSON.stringify(body);
      }
    }

    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, requestOptions);
        clearTimeout(timeoutId);

        if (!response.ok) {
          const error = await ErrorHandler.fromHttpResponse(
            response,
            endpoint,
            method
          );
          throw error;
        }

        // 处理不同的响应类型
        const contentType = response.headers.get('content-type');
        if (contentType?.includes('application/json')) {
          return await response.json();
        } else if (contentType?.includes('application/octet-stream')) {
          return (await response.blob()) as unknown as T;
        } else {
          return (await response.text()) as unknown as T;
        }
      } catch (error) {
        lastError = error as Error;
        
        // 如果是最后一次尝试或者是非网络错误，直接抛出
        if (attempt === retries || !this.isRetryableError(error as Error)) {
          break;
        }

        // 等待一段时间后重试
        await this.delay(Math.pow(2, attempt) * 1000);
      }
    }

    clearTimeout(timeoutId);

    // 处理不同类型的错误
    if (lastError) {
      if (lastError.name === 'AbortError') {
        throw ErrorHandler.createError(
          ErrorType.TIMEOUT_ERROR,
          `请求超时（${timeout / 1000}秒）- 任务可能需要更长时间处理`,
          { url, timeout }
        );
      } else if (lastError.message.includes('fetch')) {
        throw ErrorHandler.createNetworkError(
          '网络连接失败',
          { url, timeout, retryCount: retries }
        );
      } else {
        throw lastError;
      }
    }

    throw ErrorHandler.createError(ErrorType.UNKNOWN_ERROR, '未知错误');
  }

  /**
   * 判断错误是否可重试
   * @param error 错误对象
   * @returns 是否可重试
   */
  private isRetryableError(error: Error): boolean {
    // 网络错误、超时错误等可以重试
    return (
      error.name === 'TypeError' || // 网络错误
      error.name === 'AbortError' || // 超时错误
      error.message.includes('fetch') ||
      error.message.includes('network')
    );
  }

  /**
   * 延迟函数
   * @param ms 延迟毫秒数
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // 聊天相关方法
  async sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
    return this.request<ChatResponse>('/api/v1/chat', {
      method: 'POST',
      body: { session_id: sessionId, message },
      timeout: 650000, // 长时间任务专用超时时间
    });
  }

  /**
   * 启动流式消息对话
   * @param sessionId 会话ID
   * @param message 消息内容
   * @returns Promise<void>
   */
  

  /**
   * 创建流式消息的 EventSource 连接
   * @param sessionId 会话ID
   * @returns EventSource
   */
  streamMessage(sessionId: string): EventSource {
    const url = new URL(`${this.baseURL}/api/v1/chat/stream`);
    url.searchParams.set('session_id', sessionId);
    
    const eventSource = new EventSource(url.toString(), {
      withCredentials: false,
    });
    
    return eventSource;
  }

  // 会话管理方法
  async createSession(): Promise<SessionResponse> {
    return this.request<SessionResponse>('/api/v1/sessions', {
      method: 'POST',
    });
  }

  async getSession(sessionId: string): Promise<Session> {
    const response = await this.request<any>(`/api/v1/sessions/${sessionId}`);
    
    // 转换后端响应格式到前端格式
    return {
      id: response.session_id,
      name: response.name || `会话 ${response.session_id.slice(0, 8)}`,
      createdAt: response.created_at * 1000, // 转换为毫秒
      lastActivity: response.last_activity * 1000,
      messageCount: response.message_count || 0,
      status: 'active',
      metadata: {
        totalTokens: response.total_tokens,
        fileCount: response.file_count,
      },
    };
  }

  async deleteSession(sessionId: string): Promise<void> {
    await this.request<void>(`/api/v1/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async listSessions(): Promise<Session[]> {
    const response = await this.request<any[]>('/api/v1/sessions');
    
    return response.map(session => ({
      id: session.session_id,
      name: session.name || `会话 ${session.session_id.slice(0, 8)}`,
      createdAt: session.created_at * 1000,
      lastActivity: session.last_activity * 1000,
      messageCount: session.message_count || 0,
      status: 'active' as const,
      metadata: {
        totalTokens: session.total_tokens,
        fileCount: session.file_count,
      },
    }));
  }

  // 文件管理方法
  async uploadFile(sessionId: string, file: File): Promise<FileUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request<FileUploadResponse>(
      `/api/v1/sessions/${sessionId}/files`,
      {
        method: 'POST',
        body: formData,
        headers: {}, // 让浏览器自动设置 Content-Type
      }
    );
  }

  async downloadFile(sessionId: string, filePath: string): Promise<Blob> {
    return this.request<Blob>(
      `/api/v1/sessions/${sessionId}/files/${encodeURIComponent(filePath)}`,
      {
        method: 'GET',
      }
    );
  }

  async listFiles(sessionId: string): Promise<FileItem[]> {
    const response = await this.request<any[]>(
      `/api/v1/sessions/${sessionId}/files`
    );

    return response.map(file => ({
      name: file.name,
      path: file.path,
      size: file.size,
      type: file.type || 'application/octet-stream',
      lastModified: file.last_modified * 1000,
      sessionId,
      metadata: {
        encoding: file.encoding,
        preview: file.preview,
      },
    }));
  }

  // 系统状态方法
  async getHealthStatus(): Promise<HealthStatus> {
    return this.request<HealthStatus>('/health');
  }

  async getSystemStatus(): Promise<SystemStatus> {
    const response = await this.request<any>('/health');
    
    return {
      healthy: response.status === 'healthy',
      activeSessions: response.active_sessions || 0,
      totalRequests: 0, // health端点不提供此信息
      averageResponseTime: 0, // health端点不提供此信息
      uptime: 0, // health端点不提供此信息
      version: response.version || '1.0.0',
    };
  }
}

// 创建默认的 API 客户端实例
export const apiClient = new APIClientImpl();