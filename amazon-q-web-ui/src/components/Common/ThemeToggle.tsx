import React from 'react';
import { Button, Tooltip } from 'antd';
import { SunOutlined, MoonOutlined, DesktopOutlined } from '@ant-design/icons';
import { useAppStore } from '@/stores';

/**
 * 主题切换组件
 */
const ThemeToggle: React.FC = () => {
  const { settings, updateSettings, getTheme } = useAppStore();
  const currentTheme = getTheme();

  // 主题切换逻辑
  const handleThemeChange = () => {
    const themeOrder: Array<'light' | 'dark' | 'auto'> = ['light', 'dark', 'auto'];
    const currentIndex = themeOrder.indexOf(settings.theme);
    const nextIndex = (currentIndex + 1) % themeOrder.length;
    const nextTheme = themeOrder[nextIndex];
    
    updateSettings({ theme: nextTheme });
  };

  // 获取当前主题图标
  const getThemeIcon = () => {
    switch (settings.theme) {
      case 'light':
        return <SunOutlined />;
      case 'dark':
        return <MoonOutlined />;
      case 'auto':
        return <DesktopOutlined />;
      default:
        return <SunOutlined />;
    }
  };

  // 获取主题描述
  const getThemeDescription = () => {
    switch (settings.theme) {
      case 'light':
        return '亮色模式';
      case 'dark':
        return '暗色模式';
      case 'auto':
        return `自动模式 (当前: ${currentTheme === 'dark' ? '暗色' : '亮色'})`;
      default:
        return '亮色模式';
    }
  };

  return (
    <Tooltip title={`切换主题 - ${getThemeDescription()}`}>
      <Button
        type="text"
        icon={getThemeIcon()}
        onClick={handleThemeChange}
        className="text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
      />
    </Tooltip>
  );
};

export default ThemeToggle;