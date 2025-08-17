import { ErrorHandler, ErrorType } from '@/utils/errorHandler';
import { getApiUrl } from '@/config';

/**
 * SSE 事件类型
 */
export interface SSEEvent {
  type: 'data' | 'complete' | 'error';
  content: string;
  metadata?: any;
}

/**
 * SSE 客户端选项
 */
export interface SSEClientOptions {
  timeout?: number;
  retryInterval?: number;
  maxRetries?: number;
}

/**
 * SSE 客户端类 - 修复版本
 * 直接处理POST请求的流式响应
 */
export class SSEClient {
  private abortController: AbortController | null = null;
  private options: Required<SSEClientOptions>;
  private retryCount = 0;

  constructor(options: SSEClientOptions = {}) {
    this.options = {
      timeout: options.timeout || 650000, // 从60秒增加到650秒（10分50秒）
      retryInterval: options.retryInterval || 3000,
      maxRetries: options.maxRetries || 3,
    };
  }

  /**
   * 开始流式对话
   * @param sessionId 会话ID
   * @param message 消息内容
   * @param onData 数据回调
   * @param onComplete 完成回调
   * @param onError 错误回调
   */
  startStream(
    sessionId: string,
    message: string,
    onData: (content: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): void {
    this.cleanup();
    this.abortController = new AbortController();

    this.processStreamingResponse(sessionId, message, onData, onComplete, onError);
  }

  /**
   * 处理流式响应
   * @param sessionId 会话ID
   * @param message 消息内容
   * @param onData 数据回调
   * @param onComplete 完成回调
   * @param onError 错误回调
   */
  private async processStreamingResponse(
    sessionId: string,
    message: string,
    onData: (content: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
  ): Promise<void> {
    try {
      const response = await fetch(getApiUrl('/api/v1/chat/stream'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: message,
        }),
        signal: this.abortController?.signal,
      });

      if (!response.ok) {
        const error = await ErrorHandler.fromHttpResponse(
          response,
          '/api/v1/chat/stream',
          'POST'
        );
        onError(error);
        return;
      }

      // 检查响应是否是流式的
      if (!response.body) {
        onError(new Error('响应体为空'));
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) {
            break;
          }

          // 解码数据块
          const chunk = decoder.decode(value, { stream: true });
          buffer += chunk;

          // 处理完整的SSE消息
          const lines = buffer.split('\n');
          buffer = lines.pop() || ''; // 保留不完整的行

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6); // 移除 'data: ' 前缀
              
              if (data.trim() === '') {
                continue; // 跳过空数据行
              }

              try {
                const parsed = JSON.parse(data);
                
                if (parsed.type === 'session') {
                  // 会话信息，可以忽略或记录
                  continue;
                } else if (parsed.type === 'chunk') {
                  // 数据块 - 确保正确提取消息内容
                  const message = parsed.message || parsed.content || '';
                  if (message) {
                    onData(message);
                  }
                } else if (parsed.type === 'done') {
                  // 完成
                  onComplete();
                  return;
                } else if (parsed.type === 'error') {
                  // 错误
                  onError(new Error(parsed.error || '流式对话出现错误'));
                  return;
                }
              } catch (parseError) {
                // 如果不是JSON，直接作为文本处理
                onData(data);
              }
            }
          }
        }

        // 如果循环正常结束，表示流完成
        onComplete();

      } catch (readError) {
        if (readError.name === 'AbortError') {
          // 用户取消，不报错
          return;
        }
        onError(readError as Error);
      } finally {
        reader.releaseLock();
      }

    } catch (error) {
      if (error.name === 'AbortError') {
        // 用户取消，不报错
        return;
      }
      
      // 重试逻辑
      if (this.retryCount < this.options.maxRetries) {
        this.retryCount++;
        setTimeout(() => {
          this.processStreamingResponse(sessionId, message, onData, onComplete, onError);
        }, this.options.retryInterval);
      } else {
        onError(error as Error);
      }
    }
  }

  /**
   * 停止流式连接
   */
  stop(): void {
    this.cleanup();
  }

  /**
   * 清理资源
   */
  private cleanup(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  /**
   * 检查是否正在连接
   */
  isConnected(): boolean {
    return this.abortController !== null;
  }

  /**
   * 获取连接状态
   */
  getReadyState(): number {
    return this.abortController ? 1 : 0; // 1: OPEN, 0: CLOSED
  }
}
