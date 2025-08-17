import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ConfigProvider } from 'antd';
import FileManager from '../FileManager';
import { useSessionStore, useChatStore } from '@/stores';

// 模拟 stores
vi.mock('@/stores', () => ({
  useSessionStore: vi.fn(),
  useChatStore: vi.fn(),
}));

// 模拟 API 客户端
vi.mock('@/services/apiClient', () => ({
  apiClient: {
    listFiles: vi.fn(),
    uploadFile: vi.fn(),
    downloadFile: vi.fn(),
  },
}));

// 模拟配置
vi.mock('@/config', () => ({
  formatFileSize: vi.fn((size: number) => {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }),
}));

// 测试包装器
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ConfigProvider>
    {children}
  </ConfigProvider>
);

describe('FileManager', () => {
  const mockSessionStore = {
    sessions: [
      {
        id: 'session-1',
        name: '测试会话1',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 5,
        status: 'active',
      },
      {
        id: 'session-2',
        name: '测试会话2',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 3,
        status: 'active',
      },
    ],
    activeSessionId: 'session-1',
  };

  const mockChatStore = {
    currentSessionId: 'session-1',
  };

  const mockFiles = [
    {
      name: 'document.txt',
      path: '/files/document.txt',
      size: 1024,
      type: 'text/plain',
      lastModified: Date.now(),
      sessionId: 'session-1',
    },
    {
      name: 'image.jpg',
      path: '/files/image.jpg',
      size: 2048,
      type: 'image/jpeg',
      lastModified: Date.now(),
      sessionId: 'session-1',
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    (useSessionStore as any).mockReturnValue(mockSessionStore);
    (useChatStore as any).mockReturnValue(mockChatStore);
  });

  it('应该渲染文件管理界面', () => {
    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    expect(screen.getByText('文件管理')).toBeInTheDocument();
    expect(screen.getByText('上传文件')).toBeInTheDocument();
    expect(screen.getByText('刷新')).toBeInTheDocument();
  });

  it('应该显示会话选择器', () => {
    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    expect(screen.getByText('选择会话')).toBeInTheDocument();
    // Ant Design Select 组件的测试需要特殊处理
    expect(screen.getByRole('combobox')).toBeInTheDocument();
  });

  it('应该显示搜索框', () => {
    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    expect(screen.getByText('搜索文件')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('搜索文件名或类型')).toBeInTheDocument();
  });

  it('应该显示文件统计信息', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.listFiles as any).mockResolvedValue(mockFiles);

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/共 \d+ 个文件/)).toBeInTheDocument();
    });
  });

  it('应该能够加载文件列表', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.listFiles as any).mockResolvedValue(mockFiles);

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(apiClient.listFiles).toHaveBeenCalledWith('session-1');
    });
  });

  it('应该能够切换上传区域显示', async () => {
    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    const uploadButton = screen.getByText('上传文件');
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('拖拽文件到此处或点击上传')).toBeInTheDocument();
    });
  });

  it('应该能够刷新文件列表', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.listFiles as any).mockResolvedValue(mockFiles);

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    const refreshButton = screen.getByText('刷新');
    fireEvent.click(refreshButton);

    await waitFor(() => {
      expect(apiClient.listFiles).toHaveBeenCalledTimes(2); // 初始加载 + 手动刷新
    });
  });

  it('应该能够搜索文件', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.listFiles as any).mockResolvedValue(mockFiles);

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    // 等待文件加载
    await waitFor(() => {
      expect(screen.getByText(/共 \d+ 个文件/)).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('搜索文件名或类型');
    fireEvent.change(searchInput, { target: { value: 'document' } });

    // 搜索功能会过滤文件列表
    await waitFor(() => {
      expect(screen.getByText(/共 \d+ 个文件/)).toBeInTheDocument();
    });
  });

  it('应该在没有选择会话时显示提示', () => {
    const emptySessionStore = {
      ...mockSessionStore,
      activeSessionId: null,
    };
    const emptyChatStore = {
      currentSessionId: null,
    };

    (useSessionStore as any).mockReturnValue(emptySessionStore);
    (useChatStore as any).mockReturnValue(emptyChatStore);

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    expect(screen.getByText('请选择一个会话来查看和管理文件')).toBeInTheDocument();
  });

  it('应该在没有会话时禁用操作按钮', () => {
    const emptySessionStore = {
      ...mockSessionStore,
      activeSessionId: null,
    };
    const emptyChatStore = {
      currentSessionId: null,
    };

    (useSessionStore as any).mockReturnValue(emptySessionStore);
    (useChatStore as any).mockReturnValue(emptyChatStore);

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    const uploadButton = screen.getByText('上传文件');
    const refreshButton = screen.getByText('刷新');
    const searchInput = screen.getByPlaceholderText('搜索文件名或类型');

    expect(uploadButton).toBeDisabled();
    expect(refreshButton).toBeDisabled();
    expect(searchInput).toBeDisabled();
  });

  it('应该处理文件加载错误', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.listFiles as any).mockRejectedValue(new Error('加载失败'));

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(apiClient.listFiles).toHaveBeenCalled();
    });

    // 错误处理通过 ErrorHandler.handle 进行，这里主要验证API被调用
  });

  it('应该显示加载状态', async () => {
    const { apiClient } = await import('@/services/apiClient');
    // 模拟延迟响应
    (apiClient.listFiles as any).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve(mockFiles), 100))
    );

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    // 应该显示加载状态
    expect(screen.getByText('加载文件列表中...')).toBeInTheDocument();

    // 等待加载完成
    await waitFor(() => {
      expect(screen.queryByText('加载文件列表中...')).not.toBeInTheDocument();
    });
  });

  it('应该能够处理文件上传', async () => {
    const { apiClient } = await import('@/services/apiClient');
    (apiClient.listFiles as any).mockResolvedValue([]);
    (apiClient.uploadFile as any).mockResolvedValue({ success: true });

    render(
      <TestWrapper>
        <FileManager />
      </TestWrapper>
    );

    // 打开上传区域
    const uploadButton = screen.getByText('上传文件');
    fireEvent.click(uploadButton);

    await waitFor(() => {
      expect(screen.getByText('拖拽文件到此处或点击上传')).toBeInTheDocument();
    });

    // 文件上传的具体测试在 FileUploadArea 组件中进行
  });
});