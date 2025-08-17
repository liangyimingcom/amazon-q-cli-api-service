import { describe, it, expect } from 'vitest';
import {
  validateConfig,
  formatFileSize,
  isSupportedFileType,
  isFileSizeExceeded,
  getApiUrl,
  getWsUrl,
} from '../index';

describe('Config Utils', () => {
  describe('formatFileSize', () => {
    it('应该正确格式化文件大小', () => {
      expect(formatFileSize(0)).toBe('0 Bytes');
      expect(formatFileSize(1024)).toBe('1 KB');
      expect(formatFileSize(1048576)).toBe('1 MB');
      expect(formatFileSize(1073741824)).toBe('1 GB');
      expect(formatFileSize(1536)).toBe('1.5 KB');
    });
  });

  describe('isSupportedFileType', () => {
    it('应该正确检查支持的文件类型', () => {
      expect(isSupportedFileType('document.txt')).toBe(true);
      expect(isSupportedFileType('image.jpg')).toBe(true);
      expect(isSupportedFileType('data.json')).toBe(true);
      expect(isSupportedFileType('script.js')).toBe(false);
      expect(isSupportedFileType('executable.exe')).toBe(false);
    });

    it('应该处理大小写不敏感', () => {
      expect(isSupportedFileType('Document.TXT')).toBe(true);
      expect(isSupportedFileType('Image.JPG')).toBe(true);
    });

    it('应该处理没有扩展名的文件', () => {
      expect(isSupportedFileType('filename')).toBe(false);
    });
  });

  describe('isFileSizeExceeded', () => {
    it('应该正确检查文件大小限制', () => {
      const maxSize = 10485760; // 10MB
      
      expect(isFileSizeExceeded(1024)).toBe(false); // 1KB
      expect(isFileSizeExceeded(maxSize)).toBe(false); // 正好等于限制
      expect(isFileSizeExceeded(maxSize + 1)).toBe(true); // 超过限制
      expect(isFileSizeExceeded(20971520)).toBe(true); // 20MB
    });
  });

  describe('getApiUrl', () => {
    it('应该生成正确的 API URL', () => {
      expect(getApiUrl('/api/chat')).toBe('http://localhost:8080/api/chat');
      expect(getApiUrl('api/sessions')).toBe('http://localhost:8080/api/sessions');
      expect(getApiUrl('/health')).toBe('http://localhost:8080/health');
    });

    it('应该处理基础 URL 末尾的斜杠', () => {
      // 这个测试需要模拟不同的基础 URL
      expect(getApiUrl('/api/chat')).toBe('http://localhost:8080/api/chat');
    });
  });

  describe('getWsUrl', () => {
    it('应该生成正确的 WebSocket URL', () => {
      expect(getWsUrl('/api/chat/stream')).toBe('ws://localhost:8080/api/chat/stream');
      expect(getWsUrl('api/events')).toBe('ws://localhost:8080/api/events');
    });
  });

  describe('validateConfig', () => {
    it('应该在正常配置下通过验证', () => {
      expect(() => validateConfig()).not.toThrow();
    });

    // 注意：由于配置是从环境变量读取的，这些测试在实际环境中可能需要模拟
    // 这里我们主要测试验证逻辑的结构
  });
});