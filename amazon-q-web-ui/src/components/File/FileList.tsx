import React from 'react';
import {
  List,
  Card,
  Button,
  Space,
  Typography,
  Tag,
  Tooltip,
  Empty,
  Avatar,
} from 'antd';
import {
  FileOutlined,
  DownloadOutlined,
  EyeOutlined,
  DeleteOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FilePptOutlined,
  FileZipOutlined,
} from '@ant-design/icons';
import { FileItem } from '@/types';
import { formatFileSize } from '@/config';

const { Text } = Typography;

interface FileListProps {
  files: FileItem[];
  loading?: boolean;
  onDownload?: (file: FileItem) => void;
  onPreview?: (file: FileItem) => void;
  onDelete?: (file: FileItem) => void;
  emptyText?: string;
  showActions?: boolean;
}

/**
 * 文件列表组件
 */
const FileList: React.FC<FileListProps> = ({
  files,
  loading = false,
  onDownload,
  onPreview,
  onDelete,
  emptyText = '暂无文件',
  showActions = true,
}) => {
  // 获取文件图标
  const getFileIcon = (file: FileItem) => {
    const { name, type } = file;
    const extension = name.split('.').pop()?.toLowerCase();

    // 根据文件类型返回对应图标
    if (type.startsWith('image/')) {
      return <FileImageOutlined className="text-green-500" />;
    }
    
    if (type.includes('pdf')) {
      return <FilePdfOutlined className="text-red-500" />;
    }
    
    if (type.includes('word') || extension === 'doc' || extension === 'docx') {
      return <FileWordOutlined className="text-blue-500" />;
    }
    
    if (type.includes('excel') || extension === 'xls' || extension === 'xlsx') {
      return <FileExcelOutlined className="text-green-600" />;
    }
    
    if (type.includes('powerpoint') || extension === 'ppt' || extension === 'pptx') {
      return <FilePptOutlined className="text-orange-500" />;
    }
    
    if (type.includes('zip') || type.includes('rar') || type.includes('7z')) {
      return <FileZipOutlined className="text-purple-500" />;
    }
    
    if (type.startsWith('text/') || extension === 'md' || extension === 'json') {
      return <FileTextOutlined className="text-gray-600" />;
    }
    
    return <FileOutlined className="text-gray-500" />;
  };

  // 获取文件类型标签颜色
  const getFileTypeColor = (file: FileItem) => {
    const { type } = file;
    
    if (type.startsWith('image/')) return 'green';
    if (type.includes('pdf')) return 'red';
    if (type.includes('word')) return 'blue';
    if (type.includes('excel')) return 'green';
    if (type.includes('powerpoint')) return 'orange';
    if (type.startsWith('text/')) return 'default';
    
    return 'default';
  };

  // 格式化时间
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleString('zh-CN');
  };

  // 判断文件是否可预览
  const canPreview = (file: FileItem) => {
    const { type, name } = file;
    return (
      type.startsWith('text/') ||
      type.startsWith('image/') ||
      name.endsWith('.md') ||
      name.endsWith('.json')
    );
  };

  // 渲染文件操作按钮
  const renderActions = (file: FileItem) => {
    if (!showActions) return [];

    const actions = [];

    // 预览按钮
    if (canPreview(file) && onPreview) {
      actions.push(
        <Tooltip title="预览文件" key="preview">
          <Button
            type="text"
            size="small"
            icon={<EyeOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              onPreview(file);
            }}
          />
        </Tooltip>
      );
    }

    // 下载按钮
    if (onDownload) {
      actions.push(
        <Tooltip title="下载文件" key="download">
          <Button
            type="text"
            size="small"
            icon={<DownloadOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              onDownload(file);
            }}
          />
        </Tooltip>
      );
    }

    // 删除按钮
    if (onDelete) {
      actions.push(
        <Tooltip title="删除文件" key="delete">
          <Button
            type="text"
            size="small"
            icon={<DeleteOutlined />}
            danger
            onClick={(e) => {
              e.stopPropagation();
              onDelete(file);
            }}
          />
        </Tooltip>
      );
    }

    return actions;
  };

  if (files.length === 0 && !loading) {
    return (
      <Empty
        description={emptyText}
        image={Empty.PRESENTED_IMAGE_SIMPLE}
      />
    );
  }

  return (
    <List
      loading={loading}
      dataSource={files}
      renderItem={(file) => (
        <List.Item
          className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
          actions={renderActions(file)}
          onClick={() => onPreview?.(file)}
        >
          <List.Item.Meta
            avatar={
              <Avatar
                size={48}
                icon={getFileIcon(file)}
                className="bg-gray-100 dark:bg-gray-600"
              />
            }
            title={
              <div className="flex items-center space-x-2">
                <Text
                  strong
                  className="text-gray-800 dark:text-gray-200"
                  ellipsis={{ tooltip: file.name }}
                >
                  {file.name}
                </Text>
                <Tag color={getFileTypeColor(file)}>
                  {file.name.split('.').pop()?.toUpperCase() || 'FILE'}
                </Tag>
              </div>
            }
            description={
              <div className="space-y-1">
                <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                  <span>大小: {formatFileSize(file.size)}</span>
                  <span>修改时间: {formatTime(file.lastModified)}</span>
                </div>
                
                {file.metadata?.preview && (
                  <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    预览: {file.metadata.preview.substring(0, 100)}
                    {file.metadata.preview.length > 100 && '...'}
                  </div>
                )}
                
                <div className="flex items-center space-x-2 mt-2">
                  <Tag color="blue">
                    {file.type}
                  </Tag>
                  
                  {file.metadata?.encoding && (
                    <Tag color="default">
                      {file.metadata.encoding}
                    </Tag>
                  )}
                  
                  {canPreview(file) && (
                    <Tag color="green">
                      可预览
                    </Tag>
                  )}
                </div>
              </div>
            }
          />
        </List.Item>
      )}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        showQuickJumper: true,
        showTotal: (total, range) =>
          `第 ${range[0]}-${range[1]} 项，共 ${total} 个文件`,
      }}
    />
  );
};

export default FileList;