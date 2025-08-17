import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Session } from '@/types';

/**
 * 会话状态接口
 */
interface SessionState {
  // 状态
  sessions: Session[];
  activeSessionId: string | null;
  loading: boolean;
  error: string | null;
  
  // 操作
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  updateSession: (sessionId: string, updates: Partial<Session>) => void;
  removeSession: (sessionId: string) => void;
  setActiveSession: (sessionId: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // 辅助方法
  getSession: (sessionId: string) => Session | null;
  getActiveSession: () => Session | null;
  getSessionCount: () => number;
  sortSessionsByActivity: () => Session[];
}

/**
 * 会话状态管理
 */
export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      // 初始状态
      sessions: [],
      activeSessionId: null,
      loading: false,
      error: null,

      // 设置会话列表
      setSessions: (sessions) => {
        set({ sessions, error: null });
      },

      // 添加会话
      addSession: (session) => {
        set((state) => ({
          sessions: [session, ...state.sessions],
          error: null,
        }));
      },

      // 更新会话
      updateSession: (sessionId, updates) => {
        set((state) => ({
          sessions: state.sessions.map((session) =>
            session.id === sessionId 
              ? { ...session, ...updates, lastActivity: Date.now() }
              : session
          ),
        }));
      },

      // 移除会话
      removeSession: (sessionId) => {
        set((state) => ({
          sessions: state.sessions.filter((session) => session.id !== sessionId),
          activeSessionId: state.activeSessionId === sessionId 
            ? null 
            : state.activeSessionId,
        }));
      },

      // 设置活跃会话
      setActiveSession: (sessionId) => {
        set({ activeSessionId: sessionId });
        
        // 更新会话的最后活动时间
        if (sessionId) {
          const { updateSession } = get();
          updateSession(sessionId, { lastActivity: Date.now() });
        }
      },

      // 设置加载状态
      setLoading: (loading) => {
        set({ loading });
      },

      // 设置错误状态
      setError: (error) => {
        set({ error });
      },

      // 获取指定会话
      getSession: (sessionId) => {
        const { sessions } = get();
        return sessions.find((session) => session.id === sessionId) || null;
      },

      // 获取活跃会话
      getActiveSession: () => {
        const { activeSessionId, getSession } = get();
        return activeSessionId ? getSession(activeSessionId) : null;
      },

      // 获取会话数量
      getSessionCount: () => {
        const { sessions } = get();
        return sessions.length;
      },

      // 按活动时间排序会话
      sortSessionsByActivity: () => {
        const { sessions } = get();
        return [...sessions].sort((a, b) => b.lastActivity - a.lastActivity);
      },
    }),
    {
      name: 'session-storage',
      storage: createJSONStorage(() => localStorage),
      // 不持久化加载和错误状态
      partialize: (state) => ({
        sessions: state.sessions,
        activeSessionId: state.activeSessionId,
      }),
    }
  )
);