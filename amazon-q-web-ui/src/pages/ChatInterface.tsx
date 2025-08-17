import React, { useEffect, useState, useRef } from 'react';
import { Card, Button, Space, message, Switch } from 'antd';
import { PlusOutlined, SettingOutlined } from '@ant-design/icons';
import { MessageList, MessageInput } from '@/components/Message';
import { LoadingSpinner } from '@/components/Common';
import { useChatStore, useSessionStore } from '@/stores';
import { apiClient } from '@/services/apiClient';
import { SSEClient } from '@/services/sseClient';
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';
import { Message } from '@/types';

/**
 * 聊天界面主组件
 */
const ChatInterface: React.FC = () => {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamMode, setStreamMode] = useState(true);
  const sseClientRef = useRef<SSEClient | null>(null);

  const {
    currentSessionId,
    isStreaming,
    setCurrentSession,
    addMessage,
    updateStreamingMessage,
    completeStreamingMessage,
    setStreaming,
    getCurrentMessages,
  } = useChatStore();

  const {
    activeSessionId,
    getActiveSession,
    addSession,
    setActiveSession,
    updateSession,
  } = useSessionStore();

  // 当前会话的消息
  const currentMessages = getCurrentMessages();

  // 创建新会话
  const handleCreateSession = async (name?: string, files?: File[]) => {
    try {
      setLoading(true);
      const response = await apiClient.createSession();
      
      const newSession = {
        id: response.session_id,
        name: name || `会话 ${response.session_id.slice(0, 8)}`,
        createdAt: response.created_at * 1000,
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active' as const,
      };

      addSession(newSession);
      setActiveSession(newSession.id);
      setCurrentSession(newSession.id);

      // 如果有初始文件，上传它们
      if (files && files.length > 0) {
        try {
          for (const file of files) {
            await apiClient.uploadFile(newSession.id, file);
          }
          message.success(`新会话创建成功，已上传 ${files.length} 个文件`);
        } catch (error) {
          message.warning('会话创建成功，但文件上传失败');
        }
      } else {
        message.success('新会话创建成功');
      }
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '创建会话失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setLoading(false);
    }
  };

  // 发送消息
  const handleSendMessage = async (content: string) => {
    if (!currentSessionId) {
      message.warning('请先创建或选择一个会话');
      return;
    }

    try {
      setLoading(true);

      // 添加用户消息
      const userMessage: Message = {
        id: `msg-${Date.now()}-user`,
        sessionId: currentSessionId,
        role: 'user',
        content,
        timestamp: Date.now(),
      };

      addMessage(currentSessionId, userMessage);

      if (streamMode) {
        // 流式模式
        await handleStreamMessage(content);
      } else {
        // 普通模式
        await handleNormalMessage(content);
      }

      // 更新会话信息
      updateSession(currentSessionId, {
        messageCount: currentMessages.length + 2,
        lastActivity: Date.now(),
      });

      // 清空输入框
      setInputValue('');
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '发送消息失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setLoading(false);
    }
  };

  // 处理普通消息
  const handleNormalMessage = async (content: string) => {
    if (!currentSessionId) return;

    const response = await apiClient.sendMessage(currentSessionId, content);
    
    // 调试日志
    console.log('API响应:', response);
    console.log('AI回复内容:', response.response);

    // 添加 AI 回复
    const assistantMessage: Message = {
      id: `msg-${Date.now()}-assistant`,
      sessionId: currentSessionId,
      role: 'assistant',
      content: response.response,
      timestamp: response.timestamp * 1000,
      metadata: response.metadata,
    };

    addMessage(currentSessionId, assistantMessage);
  };

  // 处理流式消息
  const handleStreamMessage = async (content: string) => {
    if (!currentSessionId) return;

    // 创建空的助手消息用于流式更新
    const assistantMessageId = `msg-${Date.now()}-assistant`;
    const assistantMessage: Message = {
      id: assistantMessageId,
      sessionId: currentSessionId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
      streaming: true,
    };

    addMessage(currentSessionId, assistantMessage);
    setStreaming(true, assistantMessageId);

    // 创建 SSE 客户端
    if (!sseClientRef.current) {
      sseClientRef.current = new SSEClient({
        timeout: 650000, // 650秒超时（10分50秒）
        retryInterval: 3000,
        maxRetries: 3,
      });
    }

    // 开始流式对话
    sseClientRef.current.startStream(
      currentSessionId,
      content,
      // 数据回调
      (streamContent: string) => {
        console.log('流式数据块:', streamContent);
        updateStreamingMessage(currentSessionId, assistantMessageId, streamContent);
      },
      // 完成回调
      () => {
        completeStreamingMessage(currentSessionId, assistantMessageId);
        setStreaming(false);
      },
      // 错误回调
      (error: Error) => {
        setStreaming(false);
        const appError = ErrorHandler.createError(
          ErrorType.STREAM_ERROR,
          '流式对话失败',
          error
        );
        ErrorHandler.handle(appError);
        
        // 更新消息为错误状态
        updateStreamingMessage(
          currentSessionId, 
          assistantMessageId, 
          '抱歉，流式对话出现错误，请重试。'
        );
        completeStreamingMessage(currentSessionId, assistantMessageId);
      }
    );
  };

  // 处理文件上传
  const handleFileUpload = async (files: File[]) => {
    if (!currentSessionId) {
      message.warning('请先创建或选择一个会话');
      return;
    }

    try {
      for (const file of files) {
        await apiClient.uploadFile(currentSessionId, file);
      }
      message.success(`成功上传 ${files.length} 个文件`);
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '文件上传失败',
        error
      );
      ErrorHandler.handle(appError);
    }
  };

  // 初始化时同步会话状态
  useEffect(() => {
    if (activeSessionId && activeSessionId !== currentSessionId) {
      setCurrentSession(activeSessionId);
    }
  }, [activeSessionId, currentSessionId, setCurrentSession]);

  // 组件卸载时清理 SSE 连接
  useEffect(() => {
    return () => {
      if (sseClientRef.current) {
        sseClientRef.current.stop();
        sseClientRef.current = null;
      }
    };
  }, []);

  // 会话切换时停止当前流式连接
  useEffect(() => {
    if (sseClientRef.current && isStreaming) {
      sseClientRef.current.stop();
      setStreaming(false);
    }
  }, [currentSessionId]);

  // 如果没有活跃会话，显示欢迎界面
  if (!currentSessionId) {
    return (
      <div className="h-full flex items-center justify-center">
        <Card className="max-w-md w-full text-center">
          <div className="space-y-4">
            <div className="text-6xl mb-4">🤖</div>
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-gray-200">
              欢迎使用 Amazon Q
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              开始与 AI 助手对话，获得智能帮助和建议
            </p>
            <Space direction="vertical" size="middle" className="w-full">
              <Button
                type="primary"
                size="large"
                icon={<PlusOutlined />}
                onClick={() => handleCreateSession()}
                loading={loading}
                className="w-full"
              >
                创建新会话
              </Button>
              <Button
                type="default"
                size="large"
                icon={<SettingOutlined />}
                className="w-full"
              >
                查看设置
              </Button>
            </Space>
          </div>
        </Card>
      </div>
    );
  }

  const activeSession = getActiveSession();

  return (
    <div className="h-full flex flex-col">
      {/* 会话信息头部 */}
      <div className="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 m-0">
              {activeSession?.name || '当前会话'}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 m-0">
              {currentMessages.length} 条消息
            </p>
          </div>
          <Space>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">流式模式</span>
              <Switch
                checked={streamMode}
                onChange={setStreamMode}
                size="small"
                disabled={loading || isStreaming}
              />
            </div>
            <Button
              type="default"
              icon={<PlusOutlined />}
              onClick={() => handleCreateSession()}
              loading={loading}
            >
              新会话
            </Button>
          </Space>
        </div>
      </div>

      {/* 消息列表 */}
      <div className="flex-1 overflow-hidden">
        {loading && currentMessages.length === 0 ? (
          <LoadingSpinner tip="加载消息中..." className="h-full" />
        ) : (
          <MessageList
            messages={currentMessages}
            loading={loading && isStreaming}
            autoScroll={true}
            showAvatar={true}
            showTimestamp={true}
            emptyText="开始对话吧！"
          />
        )}
      </div>

      {/* 消息输入 */}
      <div className="flex-shrink-0">
        <MessageInput
          value={inputValue}
          onChange={setInputValue}
          onSend={handleSendMessage}
          onFileUpload={handleFileUpload}
          disabled={loading}
          loading={loading}
          placeholder="输入消息..."
          maxLength={2000}
          showFileUpload={true}
        />
      </div>
    </div>
  );
};

export default ChatInterface;