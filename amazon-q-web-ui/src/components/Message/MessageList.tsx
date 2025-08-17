import React, { useEffect, useRef } from 'react';
import { Empty, Spin } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import { Message } from '@/types';
import MessageItem from './MessageItem';

interface MessageListProps {
  messages: Message[];
  loading?: boolean;
  autoScroll?: boolean;
  showAvatar?: boolean;
  showTimestamp?: boolean;
  emptyText?: string;
}

/**
 * 消息列表组件
 */
const MessageList: React.FC<MessageListProps> = ({
  messages,
  loading = false,
  autoScroll = true,
  showAvatar = true,
  showTimestamp = true,
  emptyText = '暂无消息',
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end',
      });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, autoScroll]);

  // 如果正在加载且没有消息，显示加载状态
  if (loading && messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spin size="large" tip="加载消息中..." />
      </div>
    );
  }

  // 如果没有消息，显示空状态
  if (messages.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <Empty
          image={<MessageOutlined className="text-4xl text-gray-400" />}
          description={
            <span className="text-gray-500 dark:text-gray-400">
              {emptyText}
            </span>
          }
        />
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-2"
      style={{ maxHeight: 'calc(100vh - 200px)' }}
    >
      <div className="space-y-2">
        {messages.map((message) => (
          <MessageItem
            key={message.id}
            message={message}
            showAvatar={showAvatar}
            showTimestamp={showTimestamp}
          />
        ))}
        
        {loading && (
          <div className="flex justify-center py-4">
            <Spin size="small" tip="AI 正在思考..." />
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList;