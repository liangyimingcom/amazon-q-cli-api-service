import { AppConfig } from '@/types';

/**
 * 应用配置
 * 从环境变量中读取配置信息
 */
const config: AppConfig = {
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  WS_BASE_URL: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8080',
  MAX_FILE_SIZE: parseInt(import.meta.env.VITE_MAX_FILE_SIZE || '10485760'), // 10MB
  SUPPORTED_FILE_TYPES: (
    import.meta.env.VITE_SUPPORTED_FILE_TYPES || 
    'txt,md,pdf,doc,docx,jpg,png,json'
  ).split(','),
  THEME: (import.meta.env.VITE_THEME as 'light' | 'dark' | 'auto') || 'auto',
  DEBUG: import.meta.env.VITE_DEBUG === 'true',
};

/**
 * 验证配置
 */
export function validateConfig(): void {
  const requiredFields: (keyof AppConfig)[] = ['API_BASE_URL', 'WS_BASE_URL'];
  
  for (const field of requiredFields) {
    if (!config[field]) {
      throw new Error(`配置项 ${String(field)} 不能为空`);
    }
  }

  // 验证文件大小限制
  if (config.MAX_FILE_SIZE <= 0) {
    throw new Error('MAX_FILE_SIZE 必须大于 0');
  }

  // 验证支持的文件类型
  if (config.SUPPORTED_FILE_TYPES.length === 0) {
    throw new Error('SUPPORTED_FILE_TYPES 不能为空');
  }

  // 验证主题设置
  if (!['light', 'dark', 'auto'].includes(config.THEME)) {
    throw new Error('THEME 必须是 light、dark 或 auto');
  }
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 检查文件类型是否支持
 * @param filename 文件名
 * @returns 是否支持该文件类型
 */
export function isSupportedFileType(filename: string): boolean {
  const extension = filename.split('.').pop()?.toLowerCase();
  return extension ? config.SUPPORTED_FILE_TYPES.includes(extension) : false;
}

/**
 * 检查文件大小是否超限
 * @param size 文件大小（字节）
 * @returns 是否超过大小限制
 */
export function isFileSizeExceeded(size: number): boolean {
  return size > config.MAX_FILE_SIZE;
}

/**
 * 获取 API 完整 URL
 * @param path API 路径
 * @returns 完整的 API URL
 */
export function getApiUrl(path: string): string {
  const baseUrl = config.API_BASE_URL.replace(/\/$/, '');
  const apiPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${apiPath}`;
}

/**
 * 获取 WebSocket 完整 URL
 * @param path WebSocket 路径
 * @returns 完整的 WebSocket URL
 */
export function getWsUrl(path: string): string {
  const baseUrl = config.WS_BASE_URL.replace(/\/$/, '');
  const wsPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${wsPath}`;
}

// 在开发环境下验证配置
if (config.DEBUG) {
  try {
    validateConfig();
    console.log('✅ 配置验证通过:', config);
  } catch (error) {
    console.error('❌ 配置验证失败:', error);
  }
}

export default config;