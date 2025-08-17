import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { UserSettings, SystemStatus } from '@/types';

/**
 * 应用状态接口
 */
interface AppState {
  // 用户设置
  settings: UserSettings;
  
  // 系统状态
  systemStatus: SystemStatus | null;
  isOnline: boolean;
  lastHealthCheck: number;
  
  // UI 状态
  sidebarCollapsed: boolean;
  currentView: 'chat' | 'sessions' | 'files' | 'history' | 'settings';
  
  // 操作
  updateSettings: (updates: Partial<UserSettings>) => void;
  resetSettings: () => void;
  setSystemStatus: (status: SystemStatus | null) => void;
  setOnlineStatus: (isOnline: boolean) => void;
  updateHealthCheck: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setCurrentView: (view: AppState['currentView']) => void;
  
  // 辅助方法
  getTheme: () => 'light' | 'dark';
  isHealthy: () => boolean;
}

/**
 * 默认用户设置
 */
const defaultSettings: UserSettings = {
  theme: 'light', // 修改默认主题为亮色模式，提高字体可读性
  apiEndpoint: 'http://localhost:8080',
  maxFileSize: 10485760, // 10MB
  supportedFileTypes: ['txt', 'md', 'pdf', 'doc', 'docx', 'jpg', 'png', 'json'],
  autoSave: true,
  notifications: true,
};

/**
 * 应用状态管理
 */
export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // 初始状态
      settings: defaultSettings,
      systemStatus: null,
      isOnline: navigator.onLine,
      lastHealthCheck: 0,
      sidebarCollapsed: false,
      currentView: 'chat',

      // 更新设置
      updateSettings: (updates) => {
        set((state) => ({
          settings: { ...state.settings, ...updates },
        }));
      },

      // 重置设置
      resetSettings: () => {
        set({ settings: defaultSettings });
      },

      // 设置系统状态
      setSystemStatus: (status) => {
        set({ systemStatus: status });
      },

      // 设置在线状态
      setOnlineStatus: (isOnline) => {
        set({ isOnline });
      },

      // 更新健康检查时间
      updateHealthCheck: () => {
        set({ lastHealthCheck: Date.now() });
      },

      // 设置侧边栏折叠状态
      setSidebarCollapsed: (collapsed) => {
        set({ sidebarCollapsed: collapsed });
      },

      // 设置当前视图
      setCurrentView: (view) => {
        set({ currentView: view });
      },

      // 获取主题
      getTheme: () => {
        const { settings } = get();
        if (settings.theme === 'auto') {
          return window.matchMedia('(prefers-color-scheme: dark)').matches 
            ? 'dark' 
            : 'light';
        }
        return settings.theme;
      },

      // 检查系统是否健康
      isHealthy: () => {
        const { systemStatus, isOnline } = get();
        return isOnline && systemStatus?.healthy === true;
      },
    }),
    {
      name: 'app-storage',
      storage: createJSONStorage(() => localStorage),
      // 只持久化设置和 UI 状态
      partialize: (state) => ({
        settings: state.settings,
        sidebarCollapsed: state.sidebarCollapsed,
        currentView: state.currentView,
      }),
    }
  )
);

// 监听在线状态变化
window.addEventListener('online', () => {
  useAppStore.getState().setOnlineStatus(true);
});

window.addEventListener('offline', () => {
  useAppStore.getState().setOnlineStatus(false);
});

// 监听系统主题变化
if (window.matchMedia) {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  mediaQuery.addEventListener('change', () => {
    // 如果设置为自动主题，触发重新渲染
    const { settings } = useAppStore.getState();
    if (settings.theme === 'auto') {
      // 可以在这里触发主题更新事件
      window.dispatchEvent(new CustomEvent('theme-change'));
    }
  });
}