import React from 'react';
import { ConfigProvider, theme } from 'antd';
import { BrowserRouter as Router } from 'react-router-dom';
import { AppLayout, ErrorBoundary, SessionManager, FileManager } from '@/components';
import { useAppStore } from '@/stores';
import { useHealthCheck } from '@/hooks';
import ChatInterface from '@/pages/ChatInterface';
import zhCN from 'antd/locale/zh_CN';

/**
 * 主应用组件
 */
const App: React.FC = () => {
  // 启用健康检查
  useHealthCheck();
  const { getTheme, currentView } = useAppStore();
  const currentTheme = getTheme();

  // 根据当前视图渲染不同的内容
  const renderContent = () => {
    switch (currentView) {
      case 'chat':
        return <ChatInterface />;
      case 'sessions':
        return <SessionManager />;
      case 'files':
        return <FileManager />;
      case 'history':
        return <div className="p-8 text-center text-gray-500">历史记录功能开发中...</div>;
      case 'settings':
        return <div className="p-8 text-center text-gray-500">设置功能开发中...</div>;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <ErrorBoundary>
      <ConfigProvider
        locale={zhCN}
        theme={{
          algorithm: currentTheme === 'dark' 
            ? theme.darkAlgorithm 
            : theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1677ff',
            borderRadius: 8,
          },
        }}
      >
        <Router>
          <div className={currentTheme === 'dark' ? 'dark' : ''}>
            <AppLayout>
              {renderContent()}
            </AppLayout>
          </div>
        </Router>
      </ConfigProvider>
    </ErrorBoundary>
  );
};

export default App;
