import React, { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

/**
 * 错误边界组件
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // 记录错误到错误处理系统
    const appError = ErrorHandler.fromJavaScriptError(error, ErrorType.UNKNOWN_ERROR);
    ErrorHandler.handle(appError, {
      showNotification: false, // 不显示通知，因为我们有自定义的错误页面
      logToConsole: true,
      reportToService: true,
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // 如果提供了自定义的 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认的错误页面
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
          <div className="max-w-md w-full">
            <Result
              status="error"
              title="应用程序错误"
              subTitle="抱歉，应用程序遇到了意外错误。您可以尝试刷新页面或重置应用状态。"
              extra={[
                <Button type="primary" key="reload" onClick={this.handleReload}>
                  刷新页面
                </Button>,
                <Button key="reset" onClick={this.handleReset}>
                  重置状态
                </Button>,
              ]}
            />
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-4 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                <summary className="cursor-pointer text-red-700 dark:text-red-300 font-medium">
                  错误详情 (开发模式)
                </summary>
                <pre className="mt-2 text-sm text-red-600 dark:text-red-400 whitespace-pre-wrap">
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;