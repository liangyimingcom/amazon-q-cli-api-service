// 消息模型
export interface Message {
  id: string;
  sessionId: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  streaming?: boolean;
  metadata?: {
    tokens?: number;
    processingTime?: number;
  };
}

// 会话模型
export interface Session {
  id: string;
  name: string;
  createdAt: number;
  lastActivity: number;
  messageCount: number;
  status: 'active' | 'inactive';
  metadata?: {
    totalTokens?: number;
    fileCount?: number;
  };
}

// 文件模型
export interface FileItem {
  name: string;
  path: string;
  size: number;
  type: string;
  lastModified: number;
  sessionId: string;
  metadata?: {
    encoding?: string;
    preview?: string;
  };
}

// API 响应模型
export interface ChatResponse {
  session_id: string;
  response: string;  // 修改为response字段以匹配后端
  timestamp: number;
  metadata?: {
    processingTime: number;
    tokens: number;
  };
}

export interface StreamChunk {
  type: 'data' | 'complete' | 'error';
  content: string;
  metadata?: any;
}

// 系统状态模型
export interface SystemStatus {
  healthy: boolean;
  activeSessions: number;
  totalRequests: number;
  averageResponseTime: number;
  uptime: number;
  version: string;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy';
  timestamp: number;
  qcli_available: boolean;
  details?: {
    [key: string]: any;
  };
}

// 会话创建响应
export interface SessionResponse {
  session_id: string;
  created_at: number;
  working_directory: string;
}

// 文件上传响应
export interface FileUploadResponse {
  success: boolean;
  filename: string;
  size: number;
  path: string;
  message?: string;
}

// 错误响应
export interface ErrorResponse {
  error_code: string;
  error_message: string;
  http_status: number;
  details?: {
    [key: string]: any;
  };
}

// 用户设置
export interface UserSettings {
  theme: 'light' | 'dark' | 'auto';
  apiEndpoint: string;
  maxFileSize: number;
  supportedFileTypes: string[];
  autoSave: boolean;
  notifications: boolean;
}

// 应用配置
export interface AppConfig {
  API_BASE_URL: string;
  WS_BASE_URL: string;
  MAX_FILE_SIZE: number;
  SUPPORTED_FILE_TYPES: string[];
  THEME: 'light' | 'dark' | 'auto';
  DEBUG: boolean;
}