import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Button,
  Modal,
  Input,
  Space,
  Typography,
  Tag,
  Dropdown,
  message,
  Empty,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  MessageOutlined,
  DeleteOutlined,
  EditOutlined,
  MoreOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useSessionStore, useChatStore } from '@/stores';
import { apiClient } from '@/services/apiClient';
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';
import { Session } from '@/types';

const { Title, Text } = Typography;
const { confirm } = Modal;

interface SessionManagerProps {
  className?: string;
}

/**
 * 会话管理组件
 */
const SessionManager: React.FC<SessionManagerProps> = ({ className }) => {
  const [loading, setLoading] = useState(false);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [editingSession, setEditingSession] = useState<Session | null>(null);

  const {
    sessions,
    activeSessionId,
    loading: sessionLoading,
    setSessions,
    addSession,
    updateSession,
    removeSession,
    setActiveSession,
    sortSessionsByActivity,
  } = useSessionStore();

  const { setCurrentSession, getMessageCount } = useChatStore();

  // 加载会话列表
  const loadSessions = async () => {
    try {
      setLoading(true);
      const sessionList = await apiClient.listSessions();
      setSessions(sessionList);
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '加载会话列表失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setLoading(false);
    }
  };

  // 创建新会话
  const handleCreateSession = async () => {
    if (!newSessionName.trim()) {
      message.warning('请输入会话名称');
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.createSession();
      
      const newSession: Session = {
        id: response.session_id,
        name: newSessionName.trim(),
        createdAt: response.created_at * 1000,
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      addSession(newSession);
      setActiveSession(newSession.id);
      setCurrentSession(newSession.id);
      
      setCreateModalVisible(false);
      setNewSessionName('');
      message.success('会话创建成功');
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

  // 切换会话
  const handleSwitchSession = (sessionId: string) => {
    setActiveSession(sessionId);
    setCurrentSession(sessionId);
    message.success('已切换到该会话');
  };

  // 编辑会话名称
  const handleEditSession = (session: Session) => {
    setEditingSession(session);
    setNewSessionName(session.name);
    setEditModalVisible(true);
  };

  // 保存会话编辑
  const handleSaveEdit = async () => {
    if (!editingSession || !newSessionName.trim()) {
      message.warning('请输入会话名称');
      return;
    }

    try {
      setLoading(true);
      
      updateSession(editingSession.id, {
        name: newSessionName.trim(),
      });

      setEditModalVisible(false);
      setEditingSession(null);
      setNewSessionName('');
      message.success('会话名称更新成功');
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '更新会话失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setLoading(false);
    }
  };

  // 删除会话
  const handleDeleteSession = (session: Session) => {
    confirm({
      title: '确认删除会话',
      content: `确定要删除会话"${session.name}"吗？此操作不可撤销。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          setLoading(true);
          await apiClient.deleteSession(session.id);
          removeSession(session.id);
          message.success('会话删除成功');
        } catch (error) {
          const appError = ErrorHandler.createError(
            ErrorType.API_ERROR,
            '删除会话失败',
            error
          );
          ErrorHandler.handle(appError);
        } finally {
          setLoading(false);
        }
      },
    });
  };

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

  // 获取会话操作菜单
  const getSessionActions = (session: Session) => [
    {
      key: 'edit',
      label: '重命名',
      icon: <EditOutlined />,
      onClick: () => handleEditSession(session),
    },
    {
      key: 'delete',
      label: '删除',
      icon: <DeleteOutlined />,
      danger: true,
      onClick: () => handleDeleteSession(session),
    },
  ];

  // 组件挂载时加载会话列表
  useEffect(() => {
    loadSessions();
  }, []);

  // 排序后的会话列表
  const sortedSessions = sortSessionsByActivity();

  return (
    <div className={className}>
      <Card
        title={
          <div className="flex items-center justify-between">
            <Title level={4} className="m-0">
              会话管理
            </Title>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCreateModalVisible(true)}
              loading={loading}
            >
              新建会话
            </Button>
          </div>
        }
        className="h-full"
        styles={{ body: { padding: 0, height: 'calc(100% - 57px)', overflow: 'hidden' } }}
      >
        <div className="h-full overflow-y-auto">
          {sortedSessions.length === 0 ? (
            <Empty
              description="暂无会话"
              className="mt-8"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setCreateModalVisible(true)}
              >
                创建第一个会话
              </Button>
            </Empty>
          ) : (
            <List
              dataSource={sortedSessions}
              loading={sessionLoading || loading}
              renderItem={(session) => (
                <List.Item
                  className={`cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                    session.id === activeSessionId
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500'
                      : ''
                  }`}
                  onClick={() => handleSwitchSession(session.id)}
                  actions={[
                    <Dropdown
                      menu={{
                        items: getSessionActions(session),
                      }}
                      trigger={['click']}
                      key="actions"
                    >
                      <Button
                        type="text"
                        icon={<MoreOutlined />}
                        size="small"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Dropdown>,
                  ]}
                >
                  <List.Item.Meta
                    title={
                      <div className="flex items-center justify-between">
                        <Text
                          strong={session.id === activeSessionId}
                          className="text-gray-800 dark:text-gray-200"
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
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </Card>

      {/* 创建会话模态框 */}
      <Modal
        title="创建新会话"
        open={createModalVisible}
        onOk={handleCreateSession}
        onCancel={() => {
          setCreateModalVisible(false);
          setNewSessionName('');
        }}
        confirmLoading={loading}
        okText="创建"
        cancelText="取消"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              会话名称
            </label>
            <Input
              placeholder="请输入会话名称"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              onPressEnter={handleCreateSession}
              maxLength={50}
              showCount
            />
          </div>
        </div>
      </Modal>

      {/* 编辑会话模态框 */}
      <Modal
        title="编辑会话"
        open={editModalVisible}
        onOk={handleSaveEdit}
        onCancel={() => {
          setEditModalVisible(false);
          setEditingSession(null);
          setNewSessionName('');
        }}
        confirmLoading={loading}
        okText="保存"
        cancelText="取消"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              会话名称
            </label>
            <Input
              placeholder="请输入会话名称"
              value={newSessionName}
              onChange={(e) => setNewSessionName(e.target.value)}
              onPressEnter={handleSaveEdit}
              maxLength={50}
              showCount
            />
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default SessionManager;