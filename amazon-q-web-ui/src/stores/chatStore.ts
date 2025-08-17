import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Message } from '@/types';

/**
 * 聊天状态接口
 */
interface ChatState {
  // 状态
  currentSessionId: string | null;
  messages: Record<string, Message[]>;
  isStreaming: boolean;
  streamingMessageId: string | null;
  
  // 操作
  setCurrentSession: (sessionId: string | null) => void;
  addMessage: (sessionId: string, message: Message) => void;
  updateMessage: (sessionId: string, messageId: string, updates: Partial<Message>) => void;
  updateStreamingMessage: (sessionId: string, messageId: string, content: string) => void;
  completeStreamingMessage: (sessionId: string, messageId: string) => void;
  setStreaming: (streaming: boolean, messageId?: string) => void;
  clearMessages: (sessionId: string) => void;
  removeSession: (sessionId: string) => void;
  
  // 辅助方法
  getCurrentMessages: () => Message[];
  getMessageCount: (sessionId: string) => number;
  getLastMessage: (sessionId: string) => Message | null;
}

/**
 * 聊天状态管理
 */
export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // 初始状态
      currentSessionId: null,
      messages: {},
      isStreaming: false,
      streamingMessageId: null,

      // 设置当前会话
      setCurrentSession: (sessionId) => {
        set({ currentSessionId: sessionId });
      },

      // 添加消息
      addMessage: (sessionId, message) => {
        set((state) => ({
          messages: {
            ...state.messages,
            [sessionId]: [...(state.messages[sessionId] || []), message],
          },
        }));
      },

      // 更新消息
      updateMessage: (sessionId, messageId, updates) => {
        set((state) => ({
          messages: {
            ...state.messages,
            [sessionId]: state.messages[sessionId]?.map((msg) =>
              msg.id === messageId ? { ...msg, ...updates } : msg
            ) || [],
          },
        }));
      },

      // 更新流式消息内容 - 累积模式
      updateStreamingMessage: (sessionId, messageId, content) => {
        set((state) => ({
          messages: {
            ...state.messages,
            [sessionId]: state.messages[sessionId]?.map((msg) =>
              msg.id === messageId 
                ? { ...msg, content: msg.content + content, streaming: true }
                : msg
            ) || [],
          },
        }));
      },

      // 设置流式状态
      setStreaming: (streaming, messageId) => {
        set({ 
          isStreaming: streaming,
          streamingMessageId: streaming ? messageId || null : null,
        });
      },

      // 完成流式消息
      completeStreamingMessage: (sessionId, messageId) => {
        set((state) => ({
          messages: {
            ...state.messages,
            [sessionId]: state.messages[sessionId]?.map((msg) =>
              msg.id === messageId 
                ? { ...msg, streaming: false }
                : msg
            ) || [],
          },
        }));
      },

      // 清除会话消息
      clearMessages: (sessionId) => {
        set((state) => {
          const newMessages = { ...state.messages };
          delete newMessages[sessionId];
          return { messages: newMessages };
        });
      },

      // 移除会话
      removeSession: (sessionId) => {
        set((state) => {
          const newMessages = { ...state.messages };
          delete newMessages[sessionId];
          
          return {
            messages: newMessages,
            currentSessionId: state.currentSessionId === sessionId 
              ? null 
              : state.currentSessionId,
          };
        });
      },

      // 获取当前会话的消息
      getCurrentMessages: () => {
        const { currentSessionId, messages } = get();
        return currentSessionId ? messages[currentSessionId] || [] : [];
      },

      // 获取会话消息数量
      getMessageCount: (sessionId) => {
        const { messages } = get();
        return messages[sessionId]?.length || 0;
      },

      // 获取会话最后一条消息
      getLastMessage: (sessionId) => {
        const { messages } = get();
        const sessionMessages = messages[sessionId] || [];
        return sessionMessages.length > 0 
          ? sessionMessages[sessionMessages.length - 1] 
          : null;
      },
    }),
    {
      name: 'chat-storage',
      storage: createJSONStorage(() => localStorage),
      // 只持久化消息数据，不持久化流式状态
      partialize: (state) => ({
        messages: state.messages,
        currentSessionId: state.currentSessionId,
      }),
    }
  )
);