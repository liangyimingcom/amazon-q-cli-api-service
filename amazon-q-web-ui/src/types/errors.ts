// 错误类型常量
export const ErrorType = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  API_ERROR: 'API_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  FILE_ERROR: 'FILE_ERROR',
  STREAM_ERROR: 'STREAM_ERROR',
  SESSION_ERROR: 'SESSION_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR',
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const;

export type ErrorType = typeof ErrorType[keyof typeof ErrorType];

// 应用错误接口
export interface AppError extends Error {
  type: ErrorType;
  message: string;
  code?: string;
  details?: any;
  timestamp: number;
  stack?: string;
}

// 错误处理选项
export interface ErrorHandlerOptions {
  showNotification?: boolean;
  logToConsole?: boolean;
  reportToService?: boolean;
  retryable?: boolean;
}

// API 错误详情
export interface ApiErrorDetails {
  endpoint: string;
  method: string;
  status: number;
  statusText: string;
  data?: any;
}

// 文件错误详情
export interface FileErrorDetails {
  filename: string;
  size?: number;
  type?: string;
  operation: 'upload' | 'download' | 'preview' | 'delete';
}

// 网络错误详情
export interface NetworkErrorDetails {
  url: string;
  timeout?: number;
  retryCount?: number;
}

// 验证错误详情
export interface ValidationErrorDetails {
  field: string;
  value: any;
  rule: string;
  expected?: any;
}