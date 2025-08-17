import React, { useState, useEffect } from 'react';
import {
  Modal,
  Spin,
  Typography,
  Image,
  Card,
  Button,
  Space,
  message,
} from 'antd';
import {
  DownloadOutlined,
  CloseOutlined,
  FullscreenOutlined,
} from '@ant-design/icons';
import { FileItem } from '@/types';
import { apiClient } from '@/services/apiClient';
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';

const { Text, Paragraph } = Typography;

interface FilePreviewProps {
  file: FileItem | null;
  visible: boolean;
  onClose: () => void;
  onDownload?: (file: FileItem) => void;
}

/**
 * 文件预览组件
 */
const FilePreview: React.FC<FilePreviewProps> = ({
  file,
  visible,
  onClose,
  onDownload,
}) => {
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState<string>('');
  const [imageUrl, setImageUrl] = useState<string>('');

  // 加载文件内容
  const loadFileContent = async (fileItem: FileItem) => {
    try {
      setLoading(true);
      setContent('');
      setImageUrl('');

      const blob = await apiClient.downloadFile(fileItem.sessionId, fileItem.path);

      if (fileItem.type.startsWith('image/')) {
        // 图片文件
        const url = URL.createObjectURL(blob);
        setImageUrl(url);
      } else if (
        fileItem.type.startsWith('text/') ||
        fileItem.name.endsWith('.md') ||
        fileItem.name.endsWith('.json')
      ) {
        // 文本文件
        const text = await blob.text();
        setContent(text);
      } else {
        message.warning('该文件类型不支持预览');
      }
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '加载文件内容失败',
        error
      );
      ErrorHandler.handle(appError);
    } finally {
      setLoading(false);
    }
  };

  // 处理下载
  const handleDownload = () => {
    if (file && onDownload) {
      onDownload(file);
    }
  };

  // 判断是否可预览
  const canPreview = (fileItem: FileItem) => {
    return (
      fileItem.type.startsWith('text/') ||
      fileItem.type.startsWith('image/') ||
      fileItem.name.endsWith('.md') ||
      fileItem.name.endsWith('.json')
    );
  };

  // 渲染文件内容
  const renderContent = () => {
    if (loading) {
      return (
        <div className="text-center py-12">
          <Spin size="large" />
          <div className="mt-4 text-gray-500">加载文件内容中...</div>
        </div>
      );
    }

    if (!file) {
      return null;
    }

    if (!canPreview(file)) {
      return (
        <div className="text-center py-12">
          <div className="text-gray-500 mb-4">
            该文件类型不支持预览
          </div>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleDownload}
          >
            下载文件
          </Button>
        </div>
      );
    }

    if (file.type.startsWith('image/') && imageUrl) {
      return (
        <div className="text-center">
          <Image
            src={imageUrl}
            alt={file.name}
            style={{ maxWidth: '100%', maxHeight: '70vh' }}
            preview={{
              mask: (
                <div className="flex items-center space-x-2">
                  <FullscreenOutlined />
                  <span>查看大图</span>
                </div>
              ),
            }}
          />
        </div>
      );
    }

    if (content) {
      return (
        <Card className="max-h-[70vh] overflow-y-auto">
          <Paragraph>
            <pre className="whitespace-pre-wrap font-mono text-sm">
              {content}
            </pre>
          </Paragraph>
        </Card>
      );
    }

    return (
      <div className="text-center py-12">
        <div className="text-gray-500">无法加载文件内容</div>
      </div>
    );
  };

  // 当文件改变时加载内容
  useEffect(() => {
    if (visible && file && canPreview(file)) {
      loadFileContent(file);
    }

    // 清理图片URL
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [visible, file]);

  // 清理图片URL
  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  if (!file) {
    return null;
  }

  return (
    <Modal
      title={
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Text strong>{file.name}</Text>
            <Text type="secondary" className="text-sm">
              ({file.type})
            </Text>
          </div>
        </div>
      }
      open={visible}
      onCancel={onClose}
      width="80%"
      style={{ maxWidth: 1200 }}
      footer={
        <Space>
          <Button onClick={onClose}>
            关闭
          </Button>
          {onDownload && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
            >
              下载
            </Button>
          )}
        </Space>
      }
      destroyOnClose
    >
      <div className="space-y-4">
        {/* 文件信息 */}
        <Card size="small" className="bg-gray-50 dark:bg-gray-700">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <Text type="secondary">文件大小</Text>
              <div className="font-medium">
                {(file.size / 1024).toFixed(1)} KB
              </div>
            </div>
            <div>
              <Text type="secondary">文件类型</Text>
              <div className="font-medium">{file.type}</div>
            </div>
            <div>
              <Text type="secondary">修改时间</Text>
              <div className="font-medium">
                {new Date(file.lastModified).toLocaleString('zh-CN')}
              </div>
            </div>
            <div>
              <Text type="secondary">文件路径</Text>
              <div className="font-medium truncate" title={file.path}>
                {file.path}
              </div>
            </div>
          </div>
        </Card>

        {/* 文件内容 */}
        {renderContent()}
      </div>
    </Modal>
  );
};

export default FilePreview;