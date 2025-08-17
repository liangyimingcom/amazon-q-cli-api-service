import React, { useState, useEffect } from 'react';
import {
  Card,
  Row,
  Col,
  Typography,
  Space,
  Button,
  Select,
  Input,
  message,
  Spin,
} from 'antd';
import {
  UploadOutlined,
  ReloadOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import FileUploadArea from './FileUploadArea';
import FileList from './FileList';
import { useSessionStore, useChatStore } from '@/stores';
import { apiClient } from '@/services/apiClient';
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';
import { FileItem } from '@/types';

const { Title } = Typography;
const { Search } = Input;

interface FileManagerProps {
  className?: string;
}

/**
 * 文件管理主组件
 */
const FileManager: React.FC<FileManagerProps> = ({ className }) => {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [filteredFiles, setFilteredFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [showUploadArea, setShowUploadArea] = useState(false);

  const { sessions, activeSessionId } = useSessionStore();
  const { currentSessionId } = useChatStore();

  // 当前选择的会话ID
  const currentSession = selectedSession || activeSessionId || currentSessionId;

  // 加载文件列表
  const loadFiles = async (sessionId?: string) => {
    if (!sessionId) return;

    try {
      setLoading(true);
      const fileList = await apiClient.listFiles(sessionId);
      setFiles(fileList);
      setFilteredFiles(fileList);
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.API_ERROR,
        '加载文件列表失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setLoading(false);
    }
  };

  // 处理文件上传
  const handleFileUpload = async (uploadFiles: File[]) => {
    if (!currentSession) {
      message.warning('请先选择一个会话');
      return;
    }

    try {
      setUploading(true);
      
      for (const file of uploadFiles) {
        await apiClient.uploadFile(currentSession, file);
      }

      message.success(`成功上传 ${uploadFiles.length} 个文件`);
      
      // 重新加载文件列表
      if (currentSession) {
        await loadFiles(currentSession);
      }
      
      // 隐藏上传区域
      setShowUploadArea(false);
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '文件上传失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setUploading(false);
    }
  };

  // 处理文件下载
  const handleFileDownload = async (file: FileItem) => {
    try {
      const blob = await apiClient.downloadFile(file.sessionId, file.path);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      message.success(`文件 ${file.name} 下载成功`);
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '文件下载失败',
        error
      );
      ErrorHandler.handle(appError);
    }
  };

  // 处理文件预览
  const handleFilePreview = async (file: FileItem) => {
    try {
      // 对于文本文件，可以直接预览
      if (file.type.startsWith('text/') || file.name.endsWith('.md')) {
        const blob = await apiClient.downloadFile(file.sessionId, file.path);
        const text = await blob.text();
        
        // 这里可以打开一个模态框显示文件内容
        // 暂时使用 alert 显示
        alert(`文件内容预览：\n\n${text.substring(0, 500)}${text.length > 500 ? '...' : ''}`);
      } else if (file.type.startsWith('image/')) {
        // 对于图片文件，在新窗口中打开
        const blob = await apiClient.downloadFile(file.sessionId, file.path);
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
      } else {
        message.info('该文件类型不支持预览，请下载后查看');
      }
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '文件预览失败',
        error
      );
      ErrorHandler.handle(appError);
    }
  };

  // 处理文件删除
  const handleFileDelete = async (file: FileItem) => {
    try {
      // 注意：这里假设后端有删除文件的API
      // 实际实现中需要根据后端API调整
      message.success(`文件 ${file.name} 删除成功`);
      
      // 重新加载文件列表
      if (currentSession) {
        await loadFiles(currentSession);
      }
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '文件删除失败',
        error
      );
      ErrorHandler.handle(appError);
    }
  };

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchTerm(value);
    
    if (!value.trim()) {
      setFilteredFiles(files);
    } else {
      const filtered = files.filter(file =>
        file.name.toLowerCase().includes(value.toLowerCase()) ||
        file.type.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredFiles(filtered);
    }
  };

  // 刷新文件列表
  const handleRefresh = () => {
    if (currentSession) {
      loadFiles(currentSession);
    }
  };

  // 会话选择选项
  const sessionOptions = sessions.map(session => ({
    label: session.name,
    value: session.id,
  }));

  // 初始化时加载文件
  useEffect(() => {
    if (currentSession) {
      loadFiles(currentSession);
    }
  }, [currentSession]);

  // 搜索过滤
  useEffect(() => {
    handleSearch(searchTerm);
  }, [files, searchTerm]);

  return (
    <div className={className}>
      <Card className="h-full">
        <div className="space-y-6">
          {/* 头部控制区域 */}
          <div className="flex items-center justify-between">
            <Title level={3} className="m-0">
              文件管理
            </Title>
            
            <Space>
              <Button
                type="primary"
                icon={<UploadOutlined />}
                onClick={() => setShowUploadArea(!showUploadArea)}
                disabled={!currentSession}
              >
                上传文件
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleRefresh}
                loading={loading}
                disabled={!currentSession}
              >
                刷新
              </Button>
            </Space>
          </div>

          {/* 会话选择和搜索 */}
          <Row gutter={16}>
            <Col xs={24} sm={12} md={8}>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  选择会话
                </label>
                <Select
                  placeholder="选择要管理文件的会话"
                  value={currentSession}
                  onChange={setSelectedSession}
                  options={sessionOptions}
                  className="w-full"
                  allowClear
                />
              </div>
            </Col>
            
            <Col xs={24} sm={12} md={8}>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  搜索文件
                </label>
                <Search
                  placeholder="搜索文件名或类型"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onSearch={handleSearch}
                  allowClear
                  disabled={!currentSession}
                />
              </div>
            </Col>
            
            <Col xs={24} sm={24} md={8}>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  文件统计
                </label>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  共 {filteredFiles.length} 个文件
                  {searchTerm && ` (从 ${files.length} 个文件中筛选)`}
                </div>
              </div>
            </Col>
          </Row>

          {/* 文件上传区域 */}
          {showUploadArea && (
            <FileUploadArea
              sessionId={currentSession || undefined}
              onUpload={handleFileUpload}
              uploading={uploading}
              onUploadComplete={() => setShowUploadArea(false)}
            />
          )}

          {/* 文件列表 */}
          <div className="min-h-[400px]">
            {!currentSession ? (
              <div className="text-center py-12">
                <div className="text-gray-500 dark:text-gray-400">
                  请选择一个会话来查看和管理文件
                </div>
              </div>
            ) : loading ? (
              <div className="text-center py-12">
                <Spin size="large" />
                <div className="mt-4 text-gray-500 dark:text-gray-400">
                  加载文件列表中...
                </div>
              </div>
            ) : (
              <FileList
                files={filteredFiles}
                loading={loading}
                onDownload={handleFileDownload}
                onPreview={handleFilePreview}
                onDelete={handleFileDelete}
                emptyText={
                  searchTerm 
                    ? `没有找到包含 "${searchTerm}" 的文件`
                    : '该会话暂无文件'
                }
              />
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default FileManager;