import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ConfigProvider } from 'antd';
import FileUploadArea from '../FileUploadArea';

// 模拟配置工具
vi.mock('@/config', () => ({
  getApiUrl: vi.fn((path: string) => `http://localhost:8080${path}`),
  isSupportedFileType: vi.fn((filename: string) => {
    const supportedTypes = ['.txt', '.md', '.pdf', '.doc', '.docx', '.jpg', '.png', '.json'];
    return supportedTypes.some(type => filename.toLowerCase().endsWith(type));
  }),
  isFileSizeExceeded: vi.fn((size: number) => size > 10 * 1024 * 1024), // 10MB
  formatFileSize: vi.fn((size: number) => {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  }),
}));

// 模拟错误处理
vi.mock('@/utils/errorHandler', () => ({
  ErrorHandler: {
    createError: vi.fn((type, message, details) => ({ type, message, details })),
    handle: vi.fn(),
  },
  ErrorType: {
    FILE_ERROR: 'FILE_ERROR',
  },
}));

// 模拟 fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// 测试包装器
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ConfigProvider>
    {children}
  </ConfigProvider>
);

describe('FileUploadArea', () => {
  const mockOnUpload = vi.fn();
  const mockOnUploadProgress = vi.fn();
  const mockOnUploadComplete = vi.fn();
  const mockOnUploadError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
  });

  it('应该渲染文件上传区域', () => {
    render(
      <TestWrapper>
        <FileUploadArea />
      </TestWrapper>
    );

    expect(screen.getByText('拖拽文件到此处或点击上传')).toBeInTheDocument();
    expect(screen.getByText('选择文件')).toBeInTheDocument();
    expect(screen.getByText(/支持的文件类型/)).toBeInTheDocument();
  });

  it('应该显示文件类型和大小限制信息', () => {
    render(
      <TestWrapper>
        <FileUploadArea />
      </TestWrapper>
    );

    expect(screen.getByText(/txt, md, pdf, doc, docx, jpg, png, json/)).toBeInTheDocument();
    expect(screen.getByText(/单个文件大小不超过 10MB/)).toBeInTheDocument();
  });

  it('应该支持多文件上传', () => {
    render(
      <TestWrapper>
        <FileUploadArea multiple maxFiles={5} />
      </TestWrapper>
    );

    expect(screen.getByText(/最多 5 个文件/)).toBeInTheDocument();
  });

  it('应该在禁用状态下禁用上传', () => {
    render(
      <TestWrapper>
        <FileUploadArea disabled />
      </TestWrapper>
    );

    const uploadButton = screen.getByText('选择文件');
    expect(uploadButton.closest('button')).toBeDisabled();
  });

  it('应该在上传状态下显示加载状态', () => {
    render(
      <TestWrapper>
        <FileUploadArea uploading />
      </TestWrapper>
    );

    const uploadButton = screen.getByText('选择文件');
    expect(uploadButton.closest('button')).toBeDisabled();
  });

  it('应该调用自定义上传函数', async () => {
    render(
      <TestWrapper>
        <FileUploadArea onUpload={mockOnUpload} />
      </TestWrapper>
    );

    // 模拟文件选择
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);

      // 等待文件列表更新
      await waitFor(() => {
        expect(screen.getByText('已选择文件 (1)')).toBeInTheDocument();
      });

      // 点击上传按钮
      const uploadButton = screen.getByText('上传文件');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(mockOnUpload).toHaveBeenCalledWith([file]);
      });
    }
  });

  it('应该处理文件验证', async () => {
    const { isSupportedFileType, isFileSizeExceeded } = await import('@/config');
    
    // 模拟不支持的文件类型
    (isSupportedFileType as any).mockReturnValue(false);

    render(
      <TestWrapper>
        <FileUploadArea />
      </TestWrapper>
    );

    const file = new File(['test'], 'test.exe', { type: 'application/exe' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);

      // 应该显示错误消息（通过 message.error）
      // 注意：这里我们无法直接测试 message.error，但可以验证文件没有被添加到列表
      await waitFor(() => {
        expect(screen.queryByText('已选择文件')).not.toBeInTheDocument();
      });
    }

    // 重置 mock
    (isSupportedFileType as any).mockReturnValue(true);
  });

  it('应该限制文件数量', async () => {
    render(
      <TestWrapper>
        <FileUploadArea maxFiles={2} />
      </TestWrapper>
    );

    // 模拟选择3个文件
    const files = [
      new File(['1'], 'file1.txt', { type: 'text/plain' }),
      new File(['2'], 'file2.txt', { type: 'text/plain' }),
      new File(['3'], 'file3.txt', { type: 'text/plain' }),
    ];

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: files,
        writable: false,
      });
      
      fireEvent.change(input);

      // 应该只显示前2个文件
      await waitFor(() => {
        expect(screen.getByText('已选择文件 (2)')).toBeInTheDocument();
      });
    }
  });

  it('应该能够移除文件', async () => {
    render(
      <TestWrapper>
        <FileUploadArea />
      </TestWrapper>
    );

    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);

      await waitFor(() => {
        expect(screen.getByText('已选择文件 (1)')).toBeInTheDocument();
      });

      // 点击删除按钮
      const deleteButtons = screen.getAllByRole('button');
      const deleteButton = deleteButtons.find(button => 
        button.querySelector('.anticon-delete')
      );
      
      if (deleteButton) {
        fireEvent.click(deleteButton);

        await waitFor(() => {
          expect(screen.queryByText('已选择文件')).not.toBeInTheDocument();
        });
      }
    }
  });

  it('应该能够清空文件列表', async () => {
    render(
      <TestWrapper>
        <FileUploadArea />
      </TestWrapper>
    );

    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);

      await waitFor(() => {
        expect(screen.getByText('已选择文件 (1)')).toBeInTheDocument();
      });

      // 点击清空按钮
      const clearButton = screen.getByText('清空');
      fireEvent.click(clearButton);

      await waitFor(() => {
        expect(screen.queryByText('已选择文件')).not.toBeInTheDocument();
      });
    }
  });

  it('应该处理上传错误', async () => {
    mockFetch.mockRejectedValue(new Error('Upload failed'));

    render(
      <TestWrapper>
        <FileUploadArea 
          sessionId="test-session"
          onUploadError={mockOnUploadError}
        />
      </TestWrapper>
    );

    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);

      await waitFor(() => {
        expect(screen.getByText('已选择文件 (1)')).toBeInTheDocument();
      });

      const uploadButton = screen.getByText('上传文件');
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(mockOnUploadError).toHaveBeenCalled();
      });
    }
  });

  it('应该显示文件信息', async () => {
    const { formatFileSize } = await import('@/config');
    (formatFileSize as any).mockReturnValue('1.0 KB');

    render(
      <TestWrapper>
        <FileUploadArea />
      </TestWrapper>
    );

    const file = new File(['test content'], 'test-document.txt', { type: 'text/plain' });
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    
    if (input) {
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      
      fireEvent.change(input);

      await waitFor(() => {
        expect(screen.getByText('test-document.txt')).toBeInTheDocument();
        expect(screen.getByText('1.0 KB')).toBeInTheDocument();
      });
    }
  });

  it('应该支持自定义接受的文件类型', () => {
    render(
      <TestWrapper>
        <FileUploadArea accept=".pdf,.doc" />
      </TestWrapper>
    );

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    expect(input?.accept).toBe('.pdf,.doc');
  });

  it('应该在单文件模式下工作', () => {
    render(
      <TestWrapper>
        <FileUploadArea multiple={false} />
      </TestWrapper>
    );

    expect(screen.getByText('拖拽文件到此处或点击上传')).toBeInTheDocument();
    expect(screen.queryByText(/最多/)).not.toBeInTheDocument();
  });
});