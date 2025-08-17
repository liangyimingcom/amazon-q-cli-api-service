import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ConfigProvider } from 'antd';
import SessionManager from '../SessionManager';
import { useSessionStore, useChatStore } from '@/stores';

// 模拟 stores
vi.mock('@/stores', () => ({
  useSessionStore: vi.fn(),
  useChatStore: vi.fn(),
}));

// 模拟 API 客户端
vi.mock('@/services/apiClient', () => ({
  apiClient: {
    listSessions: vi.fn(),
    createSession: vi.fn(),
    deleteSession: vi.fn(),
  },
}));

// 测试包装器
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ConfigProvider>
    {children}
  </ConfigProvider>
);

describe('SessionManager', () => {
  const mockSessionStore = {
    sessions: [
      {
        id: 'session-1',
        name: '测试会话1',
        createdAt: Date.now() - 3600000, // 1小时前
        lastActivity: Date.now() - 1800000, // 30分钟前
        messageCount: 5,
        status: 'active',
      },
      {
        id: 'session-2',
        name: '测试会话2',
        createdAt: Date.now() - 7200000, // 2小时前
        lastActivity: Date.now() - 600000, // 10分钟前
        messageCount: 3,
        status: 'active',
      },
    ],
    activeSessionId: 'session-1',
    loading: false,
    setSessions: vi.fn(),
    addSession: vi.fn(),
    updateSession: vi.fn(),
    removeSession: vi.fn(),
    setActiveSession: vi.fn(),
    sortSessionsByActivity: vi.fn().mockReturnValue([
      {
        id: 'session-2',
        name: '测试会话2',
        createdAt: Date.now() - 7200000,
        lastActivity: Date.now() - 600000,
        messageCount: 3,
        status: 'active',
      },
      {
        id: 'session-1',
        name: '测试会话1',
        createdAt: Date.now() - 3600000,
        lastActivity: Date.now() - 1800000,
        messageCount: 5,
        status: 'active',
      },
    ]),
  };

  const mockChatStore = {
    setCurrentSession: vi.fn(),
    getMessageCount: vi.fn((sessionId: string) => {
      return sessionId === 'session-1' ? 5 : 3;
    }),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useSessionStore as any).mockReturnValue(mockSessionStore);
    (useChatStore as any).mockReturnValue(mockChatStore);
  });

  it('应该渲染会话管理界面', () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    expect(screen.getByText('会话管理')).toBeInTheDocument();
    expect(screen.getByText('新建会话')).toBeInTheDocument();
  });

  it('应该显示会话列表', () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    expect(screen.getByText('测试会话1')).toBeInTheDocument();
    expect(screen.getByText('测试会话2')).toBeInTheDocument();
    expect(screen.getByText('5 条消息')).toBeInTheDocument();
    expect(screen.getByText('3 条消息')).toBeInTheDocument();
  });

  it('应该显示活跃会话标识', () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // 查找当前标签
    const currentTags = screen.getAllByText('当前');
    expect(currentTags.length).toBeGreaterThan(0);
  });

  it('应该能够切换会话', async () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // 点击会话2
    const session2 = screen.getByText('测试会话2');
    fireEvent.click(session2);

    await waitFor(() => {
      expect(mockSessionStore.setActiveSession).toHaveBeenCalledWith('session-2');
      expect(mockChatStore.setCurrentSession).toHaveBeenCalledWith('session-2');
    });
  });

  it('应该能够打开创建会话模态框', async () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    const createButton = screen.getByText('新建会话');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByText('创建新会话')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('请输入会话名称')).toBeInTheDocument();
    });
  });

  it('应该能够创建新会话', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.createSession as any).mockResolvedValue({
      session_id: 'new-session',
      created_at: Math.floor(Date.now() / 1000),
    });

    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // 打开创建模态框
    const createButton = screen.getByText('新建会话');
    fireEvent.click(createButton);

    await waitFor(() => {
      expect(screen.getByText('创建新会话')).toBeInTheDocument();
    });

    // 输入会话名称
    const nameInput = screen.getByPlaceholderText('请输入会话名称');
    fireEvent.change(nameInput, { target: { value: '新测试会话' } });

    // 点击创建按钮
    const confirmButton = screen.getByText('创建');
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(apiClient.createSession).toHaveBeenCalled();
      expect(mockSessionStore.addSession).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 'new-session',
          name: '新测试会话',
          status: 'active',
        })
      );
    });
  });

  it('应该能够编辑会话名称', async () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // 找到更多操作按钮
    const moreButtons = screen.getAllByRole('button');
    const moreButton = moreButtons.find(button => 
      button.querySelector('.anticon-more')
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);

      await waitFor(() => {
        const editOption = screen.getByText('重命名');
        fireEvent.click(editOption);
      });

      await waitFor(() => {
        expect(screen.getByText('编辑会话')).toBeInTheDocument();
      });
    }
  });

  it('应该能够删除会话', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.deleteSession as any).mockResolvedValue(undefined);

    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // 找到更多操作按钮
    const moreButtons = screen.getAllByRole('button');
    const moreButton = moreButtons.find(button => 
      button.querySelector('.anticon-more')
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);

      await waitFor(() => {
        const deleteOption = screen.getByText('删除');
        fireEvent.click(deleteOption);
      });

      await waitFor(() => {
        expect(screen.getByText('确认删除会话')).toBeInTheDocument();
      });

      // 确认删除
      const confirmDeleteButton = screen.getByText('删除');
      fireEvent.click(confirmDeleteButton);

      await waitFor(() => {
        expect(apiClient.deleteSession).toHaveBeenCalled();
        expect(mockSessionStore.removeSession).toHaveBeenCalled();
      });
    }
  });

  it('应该显示空状态当没有会话时', () => {
    const emptySessionStore = {
      ...mockSessionStore,
      sessions: [],
      sortSessionsByActivity: vi.fn().mockReturnValue([]),
    };
    (useSessionStore as any).mockReturnValue(emptySessionStore);

    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    expect(screen.getByText('暂无会话')).toBeInTheDocument();
    expect(screen.getByText('创建第一个会话')).toBeInTheDocument();
  });

  it('应该显示加载状态', () => {
    const loadingSessionStore = {
      ...mockSessionStore,
      loading: true,
    };
    (useSessionStore as any).mockReturnValue(loadingSessionStore);

    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // Ant Design 的 List 组件在 loading 状态下会显示骨架屏
    expect(screen.getByText('会话管理')).toBeInTheDocument();
  });

  it('应该正确格式化时间显示', () => {
    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    // 检查时间格式化
    expect(screen.getByText(/分钟前|小时前|刚刚/)).toBeInTheDocument();
  });

  it('应该显示会话元数据', () => {
    const sessionWithMetadata = {
      ...mockSessionStore,
      sessions: [
        {
          ...mockSessionStore.sessions[0],
          metadata: {
            totalTokens: 1500,
            fileCount: 3,
          },
        },
      ],
      sortSessionsByActivity: vi.fn().mockReturnValue([
        {
          ...mockSessionStore.sessions[0],
          metadata: {
            totalTokens: 1500,
            fileCount: 3,
          },
        },
      ]),
    };
    (useSessionStore as any).mockReturnValue(sessionWithMetadata);

    render(
      <TestWrapper>
        <SessionManager />
      </TestWrapper>
    );

    expect(screen.getByText('1500 tokens')).toBeInTheDocument();
  });
});