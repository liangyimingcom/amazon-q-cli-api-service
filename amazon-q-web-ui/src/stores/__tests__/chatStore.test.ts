import { describe, it, expect, beforeEach } from 'vitest';
import { useChatStore } from '../chatStore';
import { Message } from '@/types';

// 模拟 localStorage
const localStorageMock = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {},
  clear: () => {},
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('ChatStore', () => {
  beforeEach(() => {
    // 重置 store 状态
    useChatStore.setState({
      currentSessionId: null,
      messages: {},
      isStreaming: false,
      streamingMessageId: null,
    });
  });

  describe('基本状态管理', () => {
    it('应该设置当前会话', () => {
      const { setCurrentSession } = useChatStore.getState();
      
      setCurrentSession('session-1');
      
      expect(useChatStore.getState().currentSessionId).toBe('session-1');
    });

    it('应该添加消息', () => {
      const { addMessage } = useChatStore.getState();
      const message: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '测试消息',
        timestamp: Date.now(),
      };

      addMessage('session-1', message);

      const { messages } = useChatStore.getState();
      expect(messages['session-1']).toHaveLength(1);
      expect(messages['session-1'][0]).toEqual(message);
    });

    it('应该更新消息', () => {
      const { addMessage, updateMessage } = useChatStore.getState();
      const message: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '原始消息',
        timestamp: Date.now(),
      };

      addMessage('session-1', message);
      updateMessage('session-1', 'msg-1', { content: '更新后的消息' });

      const { messages } = useChatStore.getState();
      expect(messages['session-1'][0].content).toBe('更新后的消息');
    });
  });

  describe('流式消息处理', () => {
    it('应该设置流式状态', () => {
      const { setStreaming } = useChatStore.getState();

      setStreaming(true, 'msg-1');

      const { isStreaming, streamingMessageId } = useChatStore.getState();
      expect(isStreaming).toBe(true);
      expect(streamingMessageId).toBe('msg-1');
    });

    it('应该更新流式消息内容', () => {
      const { addMessage, updateStreamingMessage } = useChatStore.getState();
      const message: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      };

      addMessage('session-1', message);
      updateStreamingMessage('session-1', 'msg-1', '流式内容');

      const { messages } = useChatStore.getState();
      expect(messages['session-1'][0].content).toBe('流式内容');
      expect(messages['session-1'][0].streaming).toBe(true);
    });

    it('应该清除流式状态', () => {
      const { setStreaming } = useChatStore.getState();

      setStreaming(true, 'msg-1');
      setStreaming(false);

      const { isStreaming, streamingMessageId } = useChatStore.getState();
      expect(isStreaming).toBe(false);
      expect(streamingMessageId).toBe(null);
    });
  });

  describe('会话管理', () => {
    it('应该清除会话消息', () => {
      const { addMessage, clearMessages } = useChatStore.getState();
      const message: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '测试消息',
        timestamp: Date.now(),
      };

      addMessage('session-1', message);
      clearMessages('session-1');

      const { messages } = useChatStore.getState();
      expect(messages['session-1']).toBeUndefined();
    });

    it('应该移除会话', () => {
      const { addMessage, removeSession, setCurrentSession } = useChatStore.getState();
      const message: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '测试消息',
        timestamp: Date.now(),
      };

      addMessage('session-1', message);
      setCurrentSession('session-1');
      removeSession('session-1');

      const { messages, currentSessionId } = useChatStore.getState();
      expect(messages['session-1']).toBeUndefined();
      expect(currentSessionId).toBe(null);
    });
  });

  describe('辅助方法', () => {
    it('应该获取当前会话消息', () => {
      const { addMessage, setCurrentSession, getCurrentMessages } = useChatStore.getState();
      const message: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '测试消息',
        timestamp: Date.now(),
      };

      addMessage('session-1', message);
      setCurrentSession('session-1');

      const currentMessages = getCurrentMessages();
      expect(currentMessages).toHaveLength(1);
      expect(currentMessages[0]).toEqual(message);
    });

    it('应该获取消息数量', () => {
      const { addMessage, getMessageCount } = useChatStore.getState();
      const message1: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '消息1',
        timestamp: Date.now(),
      };
      const message2: Message = {
        id: 'msg-2',
        sessionId: 'session-1',
        role: 'assistant',
        content: '消息2',
        timestamp: Date.now(),
      };

      addMessage('session-1', message1);
      addMessage('session-1', message2);

      expect(getMessageCount('session-1')).toBe(2);
      expect(getMessageCount('session-2')).toBe(0);
    });

    it('应该获取最后一条消息', () => {
      const { addMessage, getLastMessage } = useChatStore.getState();
      const message1: Message = {
        id: 'msg-1',
        sessionId: 'session-1',
        role: 'user',
        content: '第一条消息',
        timestamp: Date.now(),
      };
      const message2: Message = {
        id: 'msg-2',
        sessionId: 'session-1',
        role: 'assistant',
        content: '最后一条消息',
        timestamp: Date.now() + 1000,
      };

      addMessage('session-1', message1);
      addMessage('session-1', message2);

      const lastMessage = getLastMessage('session-1');
      expect(lastMessage).toEqual(message2);
      expect(getLastMessage('session-2')).toBe(null);
    });
  });
});