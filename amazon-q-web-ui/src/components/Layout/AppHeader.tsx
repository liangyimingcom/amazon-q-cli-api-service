import React from 'react';
import { Layout, Button, Space, Badge, Tooltip } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  WifiOutlined,
  DisconnectOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useAppStore } from '@/stores';
import { ThemeToggle } from '@/components/Common';

const { Header } = Layout;

/**
 * 应用头部组件
 */
const AppHeader: React.FC = () => {
  const {
    sidebarCollapsed,
    setSidebarCollapsed,
    isOnline,
    systemStatus,
    setCurrentView,
  } = useAppStore();

  const handleToggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  const handleOpenSettings = () => {
    setCurrentView('settings');
  };

  const isHealthy = isOnline && systemStatus?.healthy;

  return (
    <Header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 flex items-center justify-between shadow-sm">
      <div className="flex items-center space-x-4">
        <Button
          type="text"
          icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
          onClick={handleToggleSidebar}
          className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
        />
        
        <div className="flex items-center space-x-2">
          <h1 className="text-xl font-semibold text-gray-900 dark:text-white m-0">
            Amazon Q Web UI
          </h1>
          <Badge
            status={isHealthy ? 'success' : 'error'}
            text={
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {isHealthy ? '服务正常' : '服务异常'}
              </span>
            }
          />
        </div>
      </div>

      <Space>
        <Tooltip title={isOnline ? '网络连接正常' : '网络连接断开'}>
          <Button
            type="text"
            icon={isOnline ? <WifiOutlined /> : <DisconnectOutlined />}
            className={`${
              isOnline
                ? 'text-green-600 dark:text-green-400'
                : 'text-red-600 dark:text-red-400'
            }`}
          />
        </Tooltip>

        {/* 主题切换按钮 */}
        <ThemeToggle />

        <Tooltip title="设置">
          <Button
            type="text"
            icon={<SettingOutlined />}
            onClick={handleOpenSettings}
            className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
          />
        </Tooltip>
      </Space>
    </Header>
  );
};

export default AppHeader;