import React from 'react';
import { Layout } from 'antd';
import { useAppStore } from '@/stores';
import AppHeader from './AppHeader';
import AppSider from './AppSider';

const { Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

/**
 * 应用主布局组件
 */
const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { sidebarCollapsed } = useAppStore();

  return (
    <Layout className="min-h-screen">
      <AppHeader />
      <Layout>
        <AppSider collapsed={sidebarCollapsed} />
        <Layout>
          <Content className="bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
            <div className="h-full p-4">
              {children}
            </div>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default AppLayout;