import React from 'react';
import { Layout, Menu } from 'antd';
import {
  MessageOutlined,
  FolderOutlined,
  HistoryOutlined,
  TeamOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useAppStore } from '@/stores';

const { Sider } = Layout;

interface AppSiderProps {
  collapsed: boolean;
}

/**
 * 应用侧边栏组件
 */
const AppSider: React.FC<AppSiderProps> = ({ collapsed }) => {
  const { currentView, setCurrentView } = useAppStore();

  const menuItems = [
    {
      key: 'chat',
      icon: <MessageOutlined />,
      label: '对话',
    },
    {
      key: 'sessions',
      icon: <TeamOutlined />,
      label: '会话管理',
    },
    {
      key: 'files',
      icon: <FolderOutlined />,
      label: '文件管理',
    },
    {
      key: 'history',
      icon: <HistoryOutlined />,
      label: '历史记录',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    setCurrentView(key as any);
  };

  return (
    <Sider
      trigger={null}
      collapsible
      collapsed={collapsed}
      className="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700"
      width={240}
      collapsedWidth={64}
    >
      <div className="h-full">
        <Menu
          mode="inline"
          selectedKeys={[currentView]}
          items={menuItems}
          onClick={handleMenuClick}
          className="border-none bg-transparent"
          style={{
            height: '100%',
            borderRight: 0,
          }}
        />
      </div>
    </Sider>
  );
};

export default AppSider;