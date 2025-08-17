import { create } from 'zustand';
import { FileItem } from '@/types';

/**
 * 文件上传状态
 */
interface FileUploadStatus {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}

/**
 * 文件状态接口
 */
interface FileState {
  // 状态
  files: Record<string, FileItem[]>; // sessionId -> FileItem[]
  uploadQueue: Record<string, FileUploadStatus[]>; // sessionId -> uploads
  loading: boolean;
  error: string | null;
  
  // 操作
  setFiles: (sessionId: string, files: FileItem[]) => void;
  addFile: (sessionId: string, file: FileItem) => void;
  removeFile: (sessionId: string, filePath: string) => void;
  updateFile: (sessionId: string, filePath: string, updates: Partial<FileItem>) => void;
  clearFiles: (sessionId: string) => void;
  
  // 上传队列管理
  addToUploadQueue: (sessionId: string, file: File) => void;
  updateUploadProgress: (sessionId: string, fileName: string, progress: number) => void;
  updateUploadStatus: (
    sessionId: string, 
    fileName: string, 
    status: FileUploadStatus['status'],
    error?: string
  ) => void;
  removeFromUploadQueue: (sessionId: string, fileName: string) => void;
  clearUploadQueue: (sessionId: string) => void;
  
  // 状态管理
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // 辅助方法
  getFiles: (sessionId: string) => FileItem[];
  getFileCount: (sessionId: string) => number;
  getUploadQueue: (sessionId: string) => FileUploadStatus[];
  isUploading: (sessionId: string) => boolean;
}

/**
 * 文件状态管理
 */
export const useFileStore = create<FileState>((set, get) => ({
  // 初始状态
  files: {},
  uploadQueue: {},
  loading: false,
  error: null,

  // 设置文件列表
  setFiles: (sessionId, files) => {
    set((state) => ({
      files: {
        ...state.files,
        [sessionId]: files,
      },
      error: null,
    }));
  },

  // 添加文件
  addFile: (sessionId, file) => {
    set((state) => ({
      files: {
        ...state.files,
        [sessionId]: [...(state.files[sessionId] || []), file],
      },
    }));
  },

  // 移除文件
  removeFile: (sessionId, filePath) => {
    set((state) => ({
      files: {
        ...state.files,
        [sessionId]: (state.files[sessionId] || []).filter(
          (file) => file.path !== filePath
        ),
      },
    }));
  },

  // 更新文件
  updateFile: (sessionId, filePath, updates) => {
    set((state) => ({
      files: {
        ...state.files,
        [sessionId]: (state.files[sessionId] || []).map((file) =>
          file.path === filePath ? { ...file, ...updates } : file
        ),
      },
    }));
  },

  // 清除会话文件
  clearFiles: (sessionId) => {
    set((state) => {
      const newFiles = { ...state.files };
      delete newFiles[sessionId];
      return { files: newFiles };
    });
  },

  // 添加到上传队列
  addToUploadQueue: (sessionId, file) => {
    const uploadStatus: FileUploadStatus = {
      file,
      progress: 0,
      status: 'pending',
    };

    set((state) => ({
      uploadQueue: {
        ...state.uploadQueue,
        [sessionId]: [...(state.uploadQueue[sessionId] || []), uploadStatus],
      },
    }));
  },

  // 更新上传进度
  updateUploadProgress: (sessionId, fileName, progress) => {
    set((state) => ({
      uploadQueue: {
        ...state.uploadQueue,
        [sessionId]: (state.uploadQueue[sessionId] || []).map((upload) =>
          upload.file.name === fileName
            ? { ...upload, progress, status: 'uploading' as const }
            : upload
        ),
      },
    }));
  },

  // 更新上传状态
  updateUploadStatus: (sessionId, fileName, status, error) => {
    set((state) => ({
      uploadQueue: {
        ...state.uploadQueue,
        [sessionId]: (state.uploadQueue[sessionId] || []).map((upload) =>
          upload.file.name === fileName
            ? { ...upload, status, error, progress: status === 'completed' ? 100 : upload.progress }
            : upload
        ),
      },
    }));
  },

  // 从上传队列移除
  removeFromUploadQueue: (sessionId, fileName) => {
    set((state) => ({
      uploadQueue: {
        ...state.uploadQueue,
        [sessionId]: (state.uploadQueue[sessionId] || []).filter(
          (upload) => upload.file.name !== fileName
        ),
      },
    }));
  },

  // 清除上传队列
  clearUploadQueue: (sessionId) => {
    set((state) => {
      const newUploadQueue = { ...state.uploadQueue };
      delete newUploadQueue[sessionId];
      return { uploadQueue: newUploadQueue };
    });
  },

  // 设置加载状态
  setLoading: (loading) => {
    set({ loading });
  },

  // 设置错误状态
  setError: (error) => {
    set({ error });
  },

  // 获取会话文件
  getFiles: (sessionId) => {
    const { files } = get();
    return files[sessionId] || [];
  },

  // 获取文件数量
  getFileCount: (sessionId) => {
    const { files } = get();
    return files[sessionId]?.length || 0;
  },

  // 获取上传队列
  getUploadQueue: (sessionId) => {
    const { uploadQueue } = get();
    return uploadQueue[sessionId] || [];
  },

  // 检查是否正在上传
  isUploading: (sessionId) => {
    const { uploadQueue } = get();
    const queue = uploadQueue[sessionId] || [];
    return queue.some((upload) => 
      upload.status === 'pending' || upload.status === 'uploading'
    );
  },
}));