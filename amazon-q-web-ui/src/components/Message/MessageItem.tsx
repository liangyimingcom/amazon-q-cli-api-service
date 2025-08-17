import React from 'react';
import { Avatar, Card, Typography, Tag } from 'antd';
import { UserOutlined, RobotOutlined, LoadingOutlined } from '@ant-design/icons';
import { Message } from '@/types';

const { Text, Paragraph } = Typography;

interface MessageItemProps {
  message: Message;
  showAvatar?: boolean;
  showTimestamp?: boolean;
}

/**
 * 消息项组件
 */
const MessageItem: React.FC<MessageItemProps> = ({
  message,
  showAvatar = true,
  showTimestamp = true,
}) => {
  const isUser = message.role === 'user';
  const isStreaming = message.streaming;

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      className={`flex gap-3 mb-4 message-slide-in ${
        isUser ? 'flex-row-reverse' : 'flex-row'
      }`}
    >
      {showAvatar && (
        <Avatar
          size={32}
          icon={isUser ? <UserOutlined /> : <RobotOutlined />}
          className={`flex-shrink-0 ${
            isUser
              ? 'bg-blue-500'
              : 'bg-green-500'
          }`}
        />
      )}

      <div className={`flex-1 max-w-[80%] ${isUser ? 'text-right' : 'text-left'}`}>
        <Card
          size="small"
          className={`${
            isUser
              ? 'bg-blue-500 text-white border-blue-500'
              : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600'
          } shadow-sm ${isStreaming ? 'streaming-border' : ''}`}
          styles={{ body: { padding: '12px 16px' } }}
        >
          <div className="space-y-2">
            <div className={isStreaming ? 'streaming-content' : ''}>
              <Paragraph
                className={`mb-0 ${
                  isUser
                    ? 'text-white'
                    : 'text-gray-800 dark:text-gray-200'
                }`}
                style={{ marginBottom: 0 }}
              >
                {message.content}
                {isStreaming && (
                  <LoadingOutlined className="ml-2 typing-indicator" />
                )}
              </Paragraph>
            </div>

            {showTimestamp && (
              <div className="flex items-center justify-between">
                <Text
                  type="secondary"
                  className={`text-xs ${
                    isUser
                      ? 'text-blue-100'
                      : 'text-gray-500 dark:text-gray-400'
                  }`}
                >
                  {formatTime(message.timestamp)}
                </Text>

                {message.metadata && (
                  <div className="flex gap-1">
                    {message.metadata.tokens && (
                      <Tag color="blue">
                        {message.metadata.tokens} tokens
                      </Tag>
                    )}
                    {message.metadata.processingTime && (
                      <Tag color="green">
                        {message.metadata.processingTime}ms
                      </Tag>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default MessageItem;