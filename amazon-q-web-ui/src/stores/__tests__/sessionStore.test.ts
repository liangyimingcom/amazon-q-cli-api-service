import { describe, it, expect, beforeEach } from 'vitest';
import { useSessionStore } from '../sessionStore';
import { Session } from '@/types';

// 模拟 localStorage
const localStorageMock = {
  getItem: () => null,
  setItem: () => {},
  removeItem: () => {},
  clear: () => {},
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

describe('SessionStore', () => {
  beforeEach(() => {
    // 重置 store 状态
    useSessionStore.setState({
      sessions: [],
      activeSessionId: null,
      loading: false,
      error: null,
    });
  });

  describe('基本状态管理', () => {
    it('应该设置会话列表', () => {
      const { setSessions } = useSessionStore.getState();
      const sessions: Session[] = [
        {
          id: 'session-1',
          name: '会话1',
          createdAt: Date.now(),
          lastActivity: Date.now(),
          messageCount: 5,
          status: 'active',
        },
        {
          id: 'session-2',
          name: '会话2',
          createdAt: Date.now(),
          lastActivity: Date.now(),
          messageCount: 3,
          status: 'active',
        },
      ];

      setSessions(sessions);

      const { sessions: storeSessions } = useSessionStore.getState();
      expect(storeSessions).toHaveLength(2);
      expect(storeSessions).toEqual(sessions);
    });

    it('应该添加会话', () => {
      const { addSession } = useSessionStore.getState();
      const session: Session = {
        id: 'session-1',
        name: '新会话',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      addSession(session);

      const { sessions } = useSessionStore.getState();
      expect(sessions).toHaveLength(1);
      expect(sessions[0]).toEqual(session);
    });

    it('应该更新会话', async () => {
      const { addSession, updateSession } = useSessionStore.getState();
      const originalTime = Date.now();
      const session: Session = {
        id: 'session-1',
        name: '原始名称',
        createdAt: originalTime,
        lastActivity: originalTime,
        messageCount: 0,
        status: 'active',
      };

      addSession(session);
      
      // 等待一毫秒确保时间戳不同
      await new Promise(resolve => setTimeout(resolve, 1));
      
      updateSession('session-1', { name: '更新后的名称', messageCount: 5 });

      const { sessions } = useSessionStore.getState();
      expect(sessions[0].name).toBe('更新后的名称');
      expect(sessions[0].messageCount).toBe(5);
      expect(sessions[0].lastActivity).toBeGreaterThan(originalTime);
    });

    it('应该移除会话', () => {
      const { addSession, removeSession, setActiveSession } = useSessionStore.getState();
      const session: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      addSession(session);
      setActiveSession('session-1');
      removeSession('session-1');

      const { sessions, activeSessionId } = useSessionStore.getState();
      expect(sessions).toHaveLength(0);
      expect(activeSessionId).toBe(null);
    });
  });

  describe('活跃会话管理', () => {
    it('应该设置活跃会话', () => {
      const { addSession, setActiveSession } = useSessionStore.getState();
      const session: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      addSession(session);
      setActiveSession('session-1');

      const { activeSessionId } = useSessionStore.getState();
      expect(activeSessionId).toBe('session-1');
    });

    it('设置活跃会话时应该更新最后活动时间', () => {
      const { addSession, setActiveSession } = useSessionStore.getState();
      const originalTime = Date.now() - 10000; // 10秒前
      const session: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: originalTime,
        lastActivity: originalTime,
        messageCount: 0,
        status: 'active',
      };

      addSession(session);
      setActiveSession('session-1');

      const { sessions } = useSessionStore.getState();
      expect(sessions[0].lastActivity).toBeGreaterThan(originalTime);
    });
  });

  describe('状态管理', () => {
    it('应该设置加载状态', () => {
      const { setLoading } = useSessionStore.getState();

      setLoading(true);
      expect(useSessionStore.getState().loading).toBe(true);

      setLoading(false);
      expect(useSessionStore.getState().loading).toBe(false);
    });

    it('应该设置错误状态', () => {
      const { setError } = useSessionStore.getState();

      setError('测试错误');
      expect(useSessionStore.getState().error).toBe('测试错误');

      setError(null);
      expect(useSessionStore.getState().error).toBe(null);
    });
  });

  describe('辅助方法', () => {
    it('应该获取指定会话', () => {
      const { addSession, getSession } = useSessionStore.getState();
      const session: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      addSession(session);

      expect(getSession('session-1')).toEqual(session);
      expect(getSession('session-2')).toBe(null);
    });

    it('应该获取活跃会话', () => {
      const { addSession, setActiveSession, getActiveSession } = useSessionStore.getState();
      const session: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      addSession(session);
      setActiveSession('session-1');

      expect(getActiveSession()).toEqual(session);
    });

    it('应该获取会话数量', () => {
      const { addSession, getSessionCount } = useSessionStore.getState();
      const session1: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };
      const session2: Session = {
        id: 'session-2',
        name: '会话2',
        createdAt: Date.now(),
        lastActivity: Date.now(),
        messageCount: 0,
        status: 'active',
      };

      expect(getSessionCount()).toBe(0);

      addSession(session1);
      expect(getSessionCount()).toBe(1);

      addSession(session2);
      expect(getSessionCount()).toBe(2);
    });

    it('应该按活动时间排序会话', () => {
      const { addSession, sortSessionsByActivity } = useSessionStore.getState();
      const now = Date.now();
      const session1: Session = {
        id: 'session-1',
        name: '会话1',
        createdAt: now,
        lastActivity: now - 2000, // 2秒前
        messageCount: 0,
        status: 'active',
      };
      const session2: Session = {
        id: 'session-2',
        name: '会话2',
        createdAt: now,
        lastActivity: now - 1000, // 1秒前
        messageCount: 0,
        status: 'active',
      };
      const session3: Session = {
        id: 'session-3',
        name: '会话3',
        createdAt: now,
        lastActivity: now, // 现在
        messageCount: 0,
        status: 'active',
      };

      addSession(session1);
      addSession(session2);
      addSession(session3);

      const sortedSessions = sortSessionsByActivity();
      expect(sortedSessions[0].id).toBe('session-3'); // 最新的
      expect(sortedSessions[1].id).toBe('session-2');
      expect(sortedSessions[2].id).toBe('session-1'); // 最旧的
    });
  });
});