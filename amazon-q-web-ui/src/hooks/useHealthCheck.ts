import { useEffect, useRef } from 'react';
import { useAppStore } from '@/stores';
import { apiClient } from '@/services/apiClient';

/**
 * 健康检查Hook
 * 负责定期检查系统状态
 */
export const useHealthCheck = () => {
  const { setSystemStatus, setOnlineStatus } = useAppStore();
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const checkHealth = async () => {
    try {
      // 检查网络状态
      setOnlineStatus(navigator.onLine);
      
      // 检查系统状态
      const systemStatus = await apiClient.getSystemStatus();
      setSystemStatus(systemStatus);
      
      console.log('健康检查成功:', systemStatus);
    } catch (error) {
      console.error('健康检查失败:', error);
      setSystemStatus({
        healthy: false,
        activeSessions: 0,
        totalRequests: 0,
        averageResponseTime: 0,
        uptime: 0,
        version: '1.0.0',
      });
    }
  };

  useEffect(() => {
    // 立即执行一次健康检查
    checkHealth();
    
    // 设置定期检查（每30秒）
    intervalRef.current = setInterval(checkHealth, 30000);
    
    // 监听网络状态变化
    const handleOnline = () => {
      setOnlineStatus(true);
      checkHealth(); // 网络恢复时立即检查
    };
    
    const handleOffline = () => {
      setOnlineStatus(false);
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // 清理函数
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [setSystemStatus, setOnlineStatus]);

  return { checkHealth };
};
