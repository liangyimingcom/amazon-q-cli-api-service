import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { MessageItem } from '../Message';
import { Message } from '@/types';

// 模拟 antd 组件
vi.mock('antd', () => ({
  Avatar: ({ children, icon, className }: any) => (
    <div className={`avatar ${className}`} data-testid="avatar">
      {icon || children}
    </div>
  ),
  Card: ({ children, className, bodyStyle }: any) => (
    <div className={`card ${className}`} style={bodyStyle} data-testid="card">
      {children}
    </div>
  ),
  Typography: {
    Text: ({ children, className }: any) => (
      <span className={`text ${className}`}>{children}</span>
    ),
    Paragraph: ({ children, className }: any) => (
      <p className={`paragraph ${className}`}>{children}</p>
    ),
  },
  Tag: ({ children, size, color }: any) => (
    <span className={`tag tag-${size} tag-${color}`}>{children}</span>
  ),
}));

// 模拟图标
vi.mock('@ant-design/icons', () => ({
  UserOutlined: () => <span data-testid="user-icon">UserIcon</span>,
  RobotOutlined: () => <span data-testid="robot-icon">RobotIcon</span>,
  LoadingOutlined: () => <span data-testid="loading-icon">LoadingIcon</span>,
}));

describe('MessageItem', () => {
  const mockUserMessage: Message = {
    id: 'msg-1',
    sessionId: 'session-1',
    role: 'user',
    content: '这是用户消息',
    timestamp: 1640995200000, // 2022-01-01 00:00:00
  };

  const mockAssistantMessage: Message = {
    id: 'msg-2',
    sessionId: 'session-1',
    role: 'assistant',
    content: '这是AI回复',
    timestamp: 1640995260000, // 2022-01-01 00:01:00
    metadata: {
      tokens: 50,
      processingTime: 1500,
    },
  };

  const mockStreamingMessage: Message = {
    id: 'msg-3',
    sessionId: 'session-1',
    role: 'assistant',
    content: '正在流式输出...',
    timestamp: 1640995320000,
    streaming: true,
  };

  it('应该渲染用户消息', () => {
    render(<MessageItem message={mockUserMessage} />);

    expect(screen.getByText('这是用户消息')).toBeInTheDocument();
    expect(screen.getByTestId('user-icon')).toBeInTheDocument();
    expect(screen.getByText('00:00')).toBeInTheDocument();
  });

  it('应该渲染AI消息', () => {
    render(<MessageItem message={mockAssistantMessage} />);

    expect(screen.getByText('这是AI回复')).toBeInTheDocument();
    expect(screen.getByTestId('robot-icon')).toBeInTheDocument();
    expect(screen.getByText('00:01')).toBeInTheDocument();
  });

  it('应该显示消息元数据', () => {
    render(<MessageItem message={mockAssistantMessage} />);

    expect(screen.getByText('50 tokens')).toBeInTheDocument();
    expect(screen.getByText('1500ms')).toBeInTheDocument();
  });

  it('应该显示流式消息指示器', () => {
    render(<MessageItem message={mockStreamingMessage} />);

    expect(screen.getByText('正在流式输出...')).toBeInTheDocument();
    expect(screen.getByTestId('loading-icon')).toBeInTheDocument();
  });

  it('应该隐藏头像当 showAvatar 为 false', () => {
    render(<MessageItem message={mockUserMessage} showAvatar={false} />);

    expect(screen.queryByTestId('avatar')).not.toBeInTheDocument();
  });

  it('应该隐藏时间戳当 showTimestamp 为 false', () => {
    render(<MessageItem message={mockUserMessage} showTimestamp={false} />);

    expect(screen.queryByText('00:00')).not.toBeInTheDocument();
  });

  it('应该为用户消息应用正确的样式类', () => {
    const { container } = render(<MessageItem message={mockUserMessage} />);

    const messageContainer = container.firstChild as HTMLElement;
    expect(messageContainer).toHaveClass('flex-row-reverse');
  });

  it('应该为AI消息应用正确的样式类', () => {
    const { container } = render(<MessageItem message={mockAssistantMessage} />);

    const messageContainer = container.firstChild as HTMLElement;
    expect(messageContainer).toHaveClass('flex-row');
  });
});