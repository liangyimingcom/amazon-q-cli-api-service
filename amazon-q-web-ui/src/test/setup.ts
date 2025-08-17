import '@testing-library/jest-dom';
import { vi } from 'vitest';

// 模拟环境变量
Object.defineProperty(import.meta, 'env', {
  value: {
    VITE_API_BASE_URL: 'http://localhost:8080',
    VITE_WS_BASE_URL: 'ws://localhost:8080',
    VITE_MAX_FILE_SIZE: '10485760',
    VITE_SUPPORTED_FILE_TYPES: 'txt,md,pdf,doc,docx,jpg,png,json',
    VITE_THEME: 'auto',
    VITE_DEBUG: 'true',
  },
  writable: true,
});

// 模拟 antd 组件
vi.mock('antd', async (importOriginal) => {
  const actual = await importOriginal<typeof import('antd')>();
  return {
    ...actual,
    message: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    },
    notification: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn(),
    },
  };
});

// 模拟 react-router-dom
vi.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => children,
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: '/' }),
}));

// 模拟 matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});