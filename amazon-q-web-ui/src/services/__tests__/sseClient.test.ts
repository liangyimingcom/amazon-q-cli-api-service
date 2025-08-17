import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { SSEClient } from '../sseClient';

// 模拟 EventSource
class MockEventSource {
  url: string;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onopen: ((event: Event) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  readyState: number = EventSource.CONNECTING;

  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;

  constructor(url: string) {
    this.url = url;
    // 模拟异步连接
    setTimeout(() => {
      this.readyState = EventSource.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 10);
  }

  close() {
    this.readyState = EventSource.CLOSED;
  }

  // 模拟发送消息的方法
  simulateMessage(data: any) {
    if (this.onmessage) {
      const event = new MessageEvent('message', {
        data: JSON.stringify(data),
      });
      this.onmessage(event);
    }
  }

  // 模拟错误的方法
  simulateError() {
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }
}

// 模拟 fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// 模拟 EventSource
global.EventSource = MockEventSource as any;

describe('SSEClient', () => {
  let sseClient: SSEClient;
  let mockOnData: ReturnType<typeof vi.fn>;
  let mockOnComplete: ReturnType<typeof vi.fn>;
  let mockOnError: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sseClient = new SSEClient({
      timeout: 5000,
      retryInterval: 1000,
      maxRetries: 2,
    });

    mockOnData = vi.fn();
    mockOnComplete = vi.fn();
    mockOnError = vi.fn();

    // 重置 fetch mock
    mockFetch.mockReset();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    });
  });

  afterEach(() => {
    sseClient.stop();
    vi.clearAllTimers();
  });

  describe('流式对话功能', () => {
    it('应该成功启动流式对话', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 验证初始化请求
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: message,
        }),
      });

      // 等待 EventSource 连接
      await new Promise(resolve => setTimeout(resolve, 20));

      expect(sseClient.isConnected()).toBe(true);
    });

    it('应该处理流式数据', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      // 模拟接收数据
      const eventSource = (sseClient as any).eventSource as MockEventSource;
      eventSource.simulateMessage({
        type: 'data',
        content: '你好！',
      });

      expect(mockOnData).toHaveBeenCalledWith('你好！');
    });

    it('应该处理流式完成', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      // 模拟完成
      const eventSource = (sseClient as any).eventSource as MockEventSource;
      eventSource.simulateMessage({
        type: 'complete',
        content: '',
      });

      expect(mockOnComplete).toHaveBeenCalled();
      expect(sseClient.isConnected()).toBe(false);
    });

    it('应该处理流式错误', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      // 模拟错误
      const eventSource = (sseClient as any).eventSource as MockEventSource;
      eventSource.simulateMessage({
        type: 'error',
        content: '服务器错误',
      });

      expect(mockOnError).toHaveBeenCalledWith(new Error('服务器错误'));
      expect(sseClient.isConnected()).toBe(false);
    });

    it('应该处理连接错误和重试', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      // 模拟连接错误
      const eventSource = (sseClient as any).eventSource as MockEventSource;
      eventSource.simulateError();

      // 等待重试
      await new Promise(resolve => setTimeout(resolve, 1100));

      // 验证重试次数不超过最大值
      expect((sseClient as any).retryCount).toBeLessThanOrEqual(2);
    });

    it('应该处理超时', async () => {
      vi.useFakeTimers();

      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await vi.advanceTimersByTimeAsync(20);

      // 触发超时
      await vi.advanceTimersByTimeAsync(5000);

      expect(mockOnError).toHaveBeenCalledWith(new Error('流式连接超时'));

      vi.useRealTimers();
    });
  });

  describe('连接管理', () => {
    it('应该正确停止连接', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      expect(sseClient.isConnected()).toBe(true);

      sseClient.stop();

      expect(sseClient.isConnected()).toBe(false);
    });

    it('应该返回正确的连接状态', async () => {
      expect(sseClient.getReadyState()).toBe(EventSource.CLOSED);

      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      expect(sseClient.getReadyState()).toBe(EventSource.OPEN);
    });
  });

  describe('错误处理', () => {
    it('应该处理初始化请求失败', async () => {
      mockFetch.mockRejectedValue(new Error('网络错误'));

      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待错误处理
      await new Promise(resolve => setTimeout(resolve, 20));

      expect(mockOnError).toHaveBeenCalledWith(new Error('网络错误'));
    });

    it('应该处理无效的消息格式', async () => {
      const sessionId = 'test-session';
      const message = '你好';

      sseClient.startStream(sessionId, message, mockOnData, mockOnComplete, mockOnError);

      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 20));

      // 模拟无效消息
      const eventSource = (sseClient as any).eventSource as MockEventSource;
      if (eventSource.onmessage) {
        const event = new MessageEvent('message', {
          data: 'invalid json',
        });
        eventSource.onmessage(event);
      }

      expect(mockOnError).toHaveBeenCalled();
    });
  });
});