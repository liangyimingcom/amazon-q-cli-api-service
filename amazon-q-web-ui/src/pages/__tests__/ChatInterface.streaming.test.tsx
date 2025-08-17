import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ConfigProvider } from 'antd';
import { BrowserRouter } from 'react-router-dom';
import ChatInterface from '../ChatInterface';
import { useChatStore, useSessionStore } from '@/stores';

// 模拟 stores
vi.mock('@/stores', () => ({
  useChatStore: vi.fn(),
  useSessionStore: vi.fn(),
}));

// 模拟 API 客户端
vi.mock('@/services/apiClient', () => ({
  apiClient: {
    createSession: vi.fn(),
    sendMessage: vi.fn(),
    startStreamMessage: vi.fn(),
  },
}));

// 模拟 SSE 客户端
vi.mock('@/services/sseClient', () => ({
  SSEClient: vi.fn().mockImplementation(() => ({
    startStream: vi.fn(),
    stop: vi.fn(),
    isConnected: vi.fn().mockReturnValue(false),
    getReadyState: vi.fn().mockReturnValue(2),
  })),
}));

// 测试包装器
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <ConfigProvider>
      {children}
    </ConfigProvider>
  </BrowserRouter>
);

describe('ChatInterface - 流式对话功能', () => {
  const mockChatStore = {
    currentSessionId: 'test-session',
    isStreaming: false,
    setCurrentSession: vi.fn(),
    addMessage: vi.fn(),
    updateStreamingMessage: vi.fn(),
    completeStreamingMessage: vi.fn(),
    setStreaming: vi.fn(),
    getCurrentMessages: vi.fn().mockReturnValue([]),
  };

  const mockSessionStore = {
    activeSessionId: 'test-session',
    getActiveSession: vi.fn().mockReturnValue({
      id: 'test-session',
      name: '测试会话',
      createdAt: Date.now(),
      lastActivity: Date.now(),
      messageCount: 0,
      status: 'active',
    }),
    addSession: vi.fn(),
    setActiveSession: vi.fn(),
    updateSession: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useChatStore as any).mockReturnValue(mockChatStore);
    (useSessionStore as any).mockReturnValue(mockSessionStore);
  });

  it('应该显示流式模式开关', () => {
    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    expect(screen.getByText('流式模式')).toBeInTheDocument();
    expect(screen.getByRole('switch')).toBeInTheDocument();
  });

  it('应该能够切换流式模式', () => {
    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    const streamSwitch = screen.getByRole('switch');
    expect(streamSwitch).toBeChecked(); // 默认开启

    fireEvent.click(streamSwitch);
    expect(streamSwitch).not.toBeChecked();
  });

  it('流式模式下应该禁用开关当正在流式传输时', () => {
    const streamingChatStore = {
      ...mockChatStore,
      isStreaming: true,
    };
    (useChatStore as any).mockReturnValue(streamingChatStore);

    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    const streamSwitch = screen.getByRole('switch');
    expect(streamSwitch).toBeDisabled();
  });

  it('应该在流式模式下发送消息', async () => {
    const { SSEClient } = await import('@/services/sseClient');
    const mockSSEInstance = {
      startStream: vi.fn(),
      stop: vi.fn(),
      isConnected: vi.fn().mockReturnValue(false),
      getReadyState: vi.fn().mockReturnValue(2),
    };
    (SSEClient as any).mockImplementation(() => mockSSEInstance);

    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    // 找到输入框和发送按钮
    const input = screen.getByPlaceholderText('输入消息...');
    const sendButton = screen.getByText('发送');

    // 输入消息
    fireEvent.change(input, { target: { value: '测试流式消息' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockChatStore.addMessage).toHaveBeenCalledWith(
        'test-session',
        expect.objectContaining({
          role: 'user',
          content: '测试流式消息',
        })
      );
    });

    // 验证 SSE 客户端被调用
    expect(mockSSEInstance.startStream).toHaveBeenCalledWith(
      'test-session',
      '测试流式消息',
      expect.any(Function), // onData
      expect.any(Function), // onComplete
      expect.any(Function)  // onError
    );
  });

  it('应该处理流式消息数据更新', async () => {
    const { SSEClient } = await import('@/services/sseClient');
    let onDataCallback: (content: string) => void;
    
    const mockSSEInstance = {
      startStream: vi.fn((sessionId, message, onData, onComplete, onError) => {
        onDataCallback = onData;
      }),
      stop: vi.fn(),
      isConnected: vi.fn().mockReturnValue(true),
      getReadyState: vi.fn().mockReturnValue(1),
    };
    (SSEClient as any).mockImplementation(() => mockSSEInstance);

    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    // 发送消息
    const input = screen.getByPlaceholderText('输入消息...');
    const sendButton = screen.getByText('发送');

    fireEvent.change(input, { target: { value: '测试消息' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockSSEInstance.startStream).toHaveBeenCalled();
    });

    // 模拟流式数据更新
    onDataCallback!('流式回复内容');

    expect(mockChatStore.updateStreamingMessage).toHaveBeenCalledWith(
      'test-session',
      expect.any(String),
      '流式回复内容'
    );
  });

  it('应该处理流式消息完成', async () => {
    const { SSEClient } = await import('@/services/sseClient');
    let onCompleteCallback: () => void;
    
    const mockSSEInstance = {
      startStream: vi.fn((sessionId, message, onData, onComplete, onError) => {
        onCompleteCallback = onComplete;
      }),
      stop: vi.fn(),
      isConnected: vi.fn().mockReturnValue(true),
      getReadyState: vi.fn().mockReturnValue(1),
    };
    (SSEClient as any).mockImplementation(() => mockSSEInstance);

    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    // 发送消息
    const input = screen.getByPlaceholderText('输入消息...');
    const sendButton = screen.getByText('发送');

    fireEvent.change(input, { target: { value: '测试消息' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockSSEInstance.startStream).toHaveBeenCalled();
    });

    // 模拟流式完成
    onCompleteCallback!();

    expect(mockChatStore.completeStreamingMessage).toHaveBeenCalledWith(
      'test-session',
      expect.any(String)
    );
    expect(mockChatStore.setStreaming).toHaveBeenCalledWith(false);
  });

  it('应该处理流式消息错误', async () => {
    const { SSEClient } = await import('@/services/sseClient');
    let onErrorCallback: (error: Error) => void;
    
    const mockSSEInstance = {
      startStream: vi.fn((sessionId, message, onData, onComplete, onError) => {
        onErrorCallback = onError;
      }),
      stop: vi.fn(),
      isConnected: vi.fn().mockReturnValue(true),
      getReadyState: vi.fn().mockReturnValue(1),
    };
    (SSEClient as any).mockImplementation(() => mockSSEInstance);

    render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    // 发送消息
    const input = screen.getByPlaceholderText('输入消息...');
    const sendButton = screen.getByText('发送');

    fireEvent.change(input, { target: { value: '测试消息' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(mockSSEInstance.startStream).toHaveBeenCalled();
    });

    // 模拟流式错误
    onErrorCallback!(new Error('流式连接失败'));

    expect(mockChatStore.setStreaming).toHaveBeenCalledWith(false);
    expect(mockChatStore.updateStreamingMessage).toHaveBeenCalledWith(
      'test-session',
      expect.any(String),
      '抱歉，流式对话出现错误，请重试。'
    );
  });

  it('应该在会话切换时停止流式连接', () => {
    const streamingChatStore = {
      ...mockChatStore,
      isStreaming: true,
      currentSessionId: 'new-session',
    };

    const { rerender } = render(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    // 切换会话
    (useChatStore as any).mockReturnValue(streamingChatStore);
    
    rerender(
      <TestWrapper>
        <ChatInterface />
      </TestWrapper>
    );

    // 验证流式状态被重置
    expect(mockChatStore.setStreaming).toHaveBeenCalledWith(false);
  });
});