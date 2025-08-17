import React from 'react';
import { List, Tag, Typography, Button, Tooltip } from 'antd';
import {
  MessageOutlined,
  ClockCircleOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import { Session } from '@/types';

const { Text } = Typography;

interface SessionListProps {
  sessions: Session[];
  activeSessionId: string | null;
  loading?: boolean;
  onSessionClick: (sessionId: string) => void;
  onSessionAction: (session: Session, action: string) => void;
  getMessageCount: (sessionId: string) => number;
}

/**
 * 会话列表组件
 */
const SessionList: React.FC<SessionListProps> = ({
  sessions,
  activeSessionId,
  loading = false,
  onSessionClick,
  onSessionAction,
  getMessageCount,
}) => {
  // 格式化时间
  const formatTime = (timestamp: number) => {
    const now = Date.now();
    const diff = now - timestamp;
    
    if (diff < 60 * 1000) {
      return '刚刚';
    } else if (diff < 60 * 60 * 1000) {
      return `${Math.floor(diff / (60 * 1000))}分钟前`;
    } else if (diff < 24 * 60 * 60 * 1000) {
      return `${Math.floor(diff / (60 * 60 * 1000))}小时前`;
    } else {
      return new Date(timestamp).toLocaleDateString('zh-CN');
    }
  };

  return (
    <List
      dataSource={sessions}
      loading={loading}
      renderItem={(session) => (
        <List.Item
          className={`cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
            session.id === activeSessionId
              ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500'
              : ''
          }`}
          onClick={() => onSessionClick(session.id)}
          actions={[
            <Button
              type="text"
              icon={<MoreOutlined />}
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onSessionAction(session, 'more');
              }}
              key="actions"
            />,
          ]}
        >
          <List.Item.Meta
            title={
              <div className="flex items-center justify-between">
                <Text
                  strong={session.id === activeSessionId}
                  className="text-gray-800 dark:text-gray-200"
                  ellipsis={{ tooltip: session.name }}
                >
                  {session.name}
                </Text>
                {session.id === activeSessionId && (
                  <Tag color="blue">
                    当前
                  </Tag>
                )}
              </div>
            }
            description={
              <div className="space-y-1">
                <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                  <span className="flex items-center">
                    <MessageOutlined className="mr-1" />
                    {getMessageCount(session.id)} 条消息
                  </span>
                  <span className="flex items-center">
                    <ClockCircleOutlined className="mr-1" />
                    {formatTime(session.lastActivity)}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Tag
                    color={session.status === 'active' ? 'green' : 'default'}
                  >
                    {session.status === 'active' ? '活跃' : '非活跃'}
                  </Tag>
                  {session.metadata?.totalTokens && (
                    <Tooltip title="总消耗 Token 数">
                      <Tag color="orange">
                        {session.metadata.totalTokens} tokens
                      </Tag>
                    </Tooltip>
                  )}
                  {session.metadata?.fileCount && session.metadata.fileCount > 0 && (
                    <Tooltip title="文件数量">
                      <Tag color="purple">
                        {session.metadata.fileCount} 文件
                      </Tag>
                    </Tooltip>
                  )}
                </div>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
};

export default SessionList;