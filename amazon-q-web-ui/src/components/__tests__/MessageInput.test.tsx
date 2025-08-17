import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MessageInput } from '../Message';

// 模拟 antd 组件
vi.mock('antd', () => ({
  Input: {
    TextArea: ({ value, onChange, onKeyPress, placeholder, disabled, maxLength, rows }: any) => (
      <textarea
        value={value}
        onChange={onChange}
        onKeyPress={onKeyPress}
        placeholder={placeholder}
        disabled={disabled}
        maxLength={maxLength}
        rows={rows}
        data-testid="message-textarea"
      />
    ),
  },
  Button: ({ children, onClick, disabled, loading, icon, type, size, className }: any) => (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`btn btn-${type} btn-${size} ${className}`}
      data-testid={children === '发送' ? 'send-button' : 'button'}
    >
      {icon}
      {children}
    </button>
  ),
  Space: ({ children }: any) => <div className="space">{children}</div>,
  Tooltip: ({ children, title }: any) => (
    <div title={title} data-testid="tooltip">
      {children}
    </div>
  ),
  Upload: ({ children, onChange, disabled }: any) => (
    <div className="upload" data-testid="upload">
      <input
        type="file"
        onChange={(e) => onChange?.({ fileList: Array.from(e.target.files || []).map(file => ({ originFileObj: file })) })}
        disabled={disabled}
        data-testid="file-input"
      />
      {children}
    </div>
  ),
}));

// 模拟图标
vi.mock('@ant-design/icons', () => ({
  SendOutlined: () => <span data-testid="send-icon">SendIcon</span>,
  PaperClipOutlined: () => <span data-testid="paperclip-icon">PaperClipIcon</span>,
  LoadingOutlined: () => <span data-testid="loading-icon">LoadingIcon</span>,
}));

describe('MessageInput', () => {
  const mockProps = {
    value: '',
    onChange: vi.fn(),
    onSend: vi.fn(),
    onFileUpload: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('应该渲染输入框和发送按钮', () => {
    render(<MessageInput {...mockProps} />);

    expect(screen.getByTestId('message-textarea')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('输入消息...')).toBeInTheDocument();
  });

  it('应该调用 onChange 当输入内容改变', () => {
    render(<MessageInput {...mockProps} />);

    const textarea = screen.getByTestId('message-textarea');
    fireEvent.change(textarea, { target: { value: '测试消息' } });

    expect(mockProps.onChange).toHaveBeenCalledWith('测试消息');
  });

  it('应该调用 onSend 当点击发送按钮', () => {
    render(<MessageInput {...mockProps} value="测试消息" />);

    const sendButton = screen.getByTestId('send-button');
    fireEvent.click(sendButton);

    expect(mockProps.onSend).toHaveBeenCalledWith('测试消息');
  });

  it('应该调用 onSend 当按下 Enter 键', () => {
    render(<MessageInput {...mockProps} value="测试消息" />);

    const textarea = screen.getByTestId('message-textarea');
    fireEvent.keyPress(textarea, { key: 'Enter', shiftKey: false });

    expect(mockProps.onSend).toHaveBeenCalledWith('测试消息');
  });

  it('不应该调用 onSend 当按下 Shift+Enter', () => {
    render(<MessageInput {...mockProps} value="测试消息" />);

    const textarea = screen.getByTestId('message-textarea');
    fireEvent.keyPress(textarea, { key: 'Enter', shiftKey: true });

    expect(mockProps.onSend).not.toHaveBeenCalled();
  });

  it('应该禁用发送按钮当输入为空', () => {
    render(<MessageInput {...mockProps} value="" />);

    const sendButton = screen.getByTestId('send-button');
    expect(sendButton).toBeDisabled();
  });

  it('应该禁用发送按钮当只有空格', () => {
    render(<MessageInput {...mockProps} value="   " />);

    const sendButton = screen.getByTestId('send-button');
    expect(sendButton).toBeDisabled();
  });

  it('应该启用发送按钮当有有效输入', () => {
    render(<MessageInput {...mockProps} value="测试消息" />);

    const sendButton = screen.getByTestId('send-button');
    expect(sendButton).not.toBeDisabled();
  });

  it('应该显示加载状态', () => {
    render(<MessageInput {...mockProps} loading={true} />);

    expect(screen.getByTestId('loading-icon')).toBeInTheDocument();
    expect(screen.getByTestId('send-button')).toBeDisabled();
  });

  it('应该禁用所有控件当 disabled 为 true', () => {
    render(<MessageInput {...mockProps} disabled={true} />);

    expect(screen.getByTestId('message-textarea')).toBeDisabled();
    expect(screen.getByTestId('send-button')).toBeDisabled();
    expect(screen.getByTestId('file-input')).toBeDisabled();
  });

  it('应该显示字符计数', () => {
    render(<MessageInput {...mockProps} value="测试" maxLength={100} />);

    expect(screen.getByText('2/100')).toBeInTheDocument();
  });

  it('应该隐藏文件上传当 showFileUpload 为 false', () => {
    render(<MessageInput {...mockProps} showFileUpload={false} />);

    expect(screen.queryByTestId('upload')).not.toBeInTheDocument();
  });

  it('应该调用 onFileUpload 当选择文件', () => {
    render(<MessageInput {...mockProps} />);

    const fileInput = screen.getByTestId('file-input');
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    
    Object.defineProperty(fileInput, 'files', {
      value: [file],
      writable: false,
    });

    fireEvent.change(fileInput);

    expect(mockProps.onFileUpload).toHaveBeenCalledWith([file]);
  });

  it('应该使用自定义占位符', () => {
    render(<MessageInput {...mockProps} placeholder="自定义占位符" />);

    expect(screen.getByPlaceholderText('自定义占位符')).toBeInTheDocument();
  });
});