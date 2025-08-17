import React, { useState, useRef } from 'react';
import { Upload, Button, Progress, message, Card, Typography, Space } from 'antd';
import {
  UploadOutlined,
  InboxOutlined,
  DeleteOutlined,
  FileOutlined,
} from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { getApiUrl, isSupportedFileType, isFileSizeExceeded, formatFileSize } from '@/config';
import { ErrorHandler, ErrorType } from '@/utils/errorHandler';

const { Dragger } = Upload;
const { Text, Title } = Typography;

interface FileUploadAreaProps {
  sessionId?: string;
  onUpload?: (files: File[]) => Promise<void>;
  onUploadProgress?: (progress: number) => void;
  onUploadComplete?: (files: File[]) => void;
  onUploadError?: (error: Error) => void;
  uploading?: boolean;
  disabled?: boolean;
  multiple?: boolean;
  maxFiles?: number;
  className?: string;
  showFileList?: boolean;
  accept?: string;
}

/**
 * 文件上传区域组件
 */
const FileUploadArea: React.FC<FileUploadAreaProps> = ({
  sessionId,
  onUpload,
  onUploadProgress,
  onUploadComplete,
  onUploadError,
  uploading = false,
  disabled = false,
  multiple = true,
  maxFiles = 10,
  className,
  showFileList = true,
  accept,
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 验证文件
  const validateFile = (file: File): boolean => {
    // 检查文件类型
    if (!isSupportedFileType(file.name)) {
      message.error(`不支持的文件类型：${file.name}`);
      return false;
    }

    // 检查文件大小
    if (isFileSizeExceeded(file.size)) {
      message.error(`文件大小超过限制：${file.name} (${formatFileSize(file.size)})`);
      return false;
    }

    return true;
  };

  // 处理文件选择
  const handleFileChange: UploadProps['onChange'] = ({ fileList: newFileList }) => {
    // 过滤有效文件
    const validFiles = newFileList.filter(file => {
      if (file.originFileObj) {
        return validateFile(file.originFileObj);
      }
      return true;
    });

    // 限制文件数量
    if (validFiles.length > maxFiles) {
      message.warning(`最多只能上传 ${maxFiles} 个文件`);
      setFileList(validFiles.slice(0, maxFiles));
      return;
    }

    setFileList(validFiles);
  };

  // 上传前验证
  const beforeUpload = (file: File, fileList: File[]) => {
    // 验证单个文件
    if (!validateFile(file)) {
      return false;
    }

    // 检查总文件数量
    if (fileList.length > maxFiles) {
      message.warning(`最多只能上传 ${maxFiles} 个文件`);
      return false;
    }

    return false; // 阻止自动上传，手动处理
  };

  // 手动上传文件
  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('请先选择文件');
      return;
    }

    if (!sessionId && !onUpload) {
      message.error('缺少会话ID或上传处理函数');
      return;
    }

    try {
      const files = fileList
        .filter(file => file.originFileObj)
        .map(file => file.originFileObj as File);

      if (files.length === 0) {
        message.warning('没有有效的文件可上传');
        return;
      }

      setUploadProgress(0);

      if (onUpload) {
        // 使用自定义上传函数
        await onUpload(files);
      } else if (sessionId) {
        // 使用默认上传逻辑
        await uploadFilesToSession(files);
      }

      // 上传成功
      setFileList([]);
      setUploadProgress(100);
      onUploadComplete?.(files);
      message.success(`成功上传 ${files.length} 个文件`);
    } catch (error) {
      const appError = ErrorHandler.createError(
        ErrorType.FILE_ERROR,
        '文件上传失败',
        error
      );
      ErrorHandler.handle(appError);
      onUploadError?.(appError);
    } finally {
      setUploadProgress(0);
    }
  };

  // 上传文件到会话
  const uploadFilesToSession = async (files: File[]) => {
    if (!sessionId) return;

    const uploadUrl = getApiUrl(`/api/v1/sessions/${sessionId}/files`);
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`上传文件 ${file.name} 失败: ${response.statusText}`);
      }

      // 更新进度
      const progress = Math.round(((i + 1) / files.length) * 100);
      setUploadProgress(progress);
      onUploadProgress?.(progress);
    }
  };

  // 移除文件
  const handleRemove = (file: UploadFile) => {
    setFileList(fileList.filter(item => item.uid !== file.uid));
  };

  // 清空文件列表
  const handleClear = () => {
    setFileList([]);
    setUploadProgress(0);
  };

  // 拖拽上传属性
  const draggerProps: UploadProps = {
    name: 'file',
    multiple,
    fileList,
    onChange: handleFileChange,
    beforeUpload,
    onRemove: handleRemove,
    disabled: disabled || uploading,
    accept,
    showUploadList: showFileList,
  };

  return (
    <div className={className}>
      <Card className="upload-area">
        <Dragger {...draggerProps} className="upload-dragger">
          <div className="p-8 text-center">
            <div className="mb-4">
              <InboxOutlined className="text-4xl text-blue-500" />
            </div>
            <Title level={4} className="mb-2">
              {multiple ? '拖拽文件到此处或点击上传' : '拖拽文件到此处或点击上传'}
            </Title>
            <Text type="secondary" className="block mb-4">
              支持的文件类型：txt, md, pdf, doc, docx, jpg, png, json
              <br />
              单个文件大小不超过 10MB
              {multiple && `, 最多 ${maxFiles} 个文件`}
            </Text>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              disabled={disabled || uploading}
            >
              选择文件
            </Button>
          </div>
        </Dragger>

        {/* 文件列表 */}
        {showFileList && fileList.length > 0 && (
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <Text strong>已选择文件 ({fileList.length})</Text>
              <Space>
                <Button
                  type="primary"
                  onClick={handleUpload}
                  loading={uploading}
                  disabled={disabled || fileList.length === 0}
                >
                  上传文件
                </Button>
                <Button
                  type="default"
                  icon={<DeleteOutlined />}
                  onClick={handleClear}
                  disabled={disabled || uploading}
                >
                  清空
                </Button>
              </Space>
            </div>

            {/* 上传进度 */}
            {uploading && uploadProgress > 0 && (
              <div className="mb-4">
                <Progress
                  percent={uploadProgress}
                  status={uploadProgress === 100 ? 'success' : 'active'}
                  showInfo
                />
              </div>
            )}

            {/* 文件预览列表 */}
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {fileList.map((file) => (
                <div
                  key={file.uid}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <FileOutlined className="text-blue-500" />
                    <div>
                      <div className="font-medium text-gray-800 dark:text-gray-200">
                        {file.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        {file.size ? formatFileSize(file.size) : ''}
                      </div>
                    </div>
                  </div>
                  <Button
                    type="text"
                    icon={<DeleteOutlined />}
                    onClick={() => handleRemove(file)}
                    disabled={disabled || uploading}
                    className="text-red-500 hover:text-red-600"
                  />
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default FileUploadArea;