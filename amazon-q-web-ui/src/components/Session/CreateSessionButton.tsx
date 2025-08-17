import React, { useState } from 'react';
import { Button, Modal, Input, Upload, message, Space } from 'antd';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons';
import type { UploadFile } from 'antd';

interface CreateSessionButtonProps {
  loading?: boolean;
  onCreateSession: (name: string, files?: File[]) => Promise<void>;
  className?: string;
  size?: 'small' | 'middle' | 'large';
  type?: 'default' | 'primary' | 'dashed' | 'link' | 'text';
}

/**
 * 创建会话按钮组件
 */
const CreateSessionButton: React.FC<CreateSessionButtonProps> = ({
  loading = false,
  onCreateSession,
  className,
  size = 'middle',
  type = 'primary',
}) => {
  const [modalVisible, setModalVisible] = useState(false);
  const [sessionName, setSessionName] = useState('');
  const [uploading, setUploading] = useState(false);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  // 处理创建会话
  const handleCreate = async () => {
    if (!sessionName.trim()) {
      message.warning('请输入会话名称');
      return;
    }

    try {
      setUploading(true);
      
      // 获取实际的文件对象
      const files = fileList
        .filter(file => file.originFileObj)
        .map(file => file.originFileObj as File);

      await onCreateSession(sessionName.trim(), files);
      
      // 重置状态
      setModalVisible(false);
      setSessionName('');
      setFileList([]);
    } catch (error) {
      // 错误处理由父组件负责
    } finally {
      setUploading(false);
    }
  };

  // 处理文件上传
  const handleFileChange = ({ fileList: newFileList }: { fileList: UploadFile[] }) => {
    setFileList(newFileList);
  };

  // 文件上传前的验证
  const beforeUpload = (file: File) => {
    const isValidSize = file.size / 1024 / 1024 < 10; // 10MB
    if (!isValidSize) {
      message.error('文件大小不能超过 10MB');
      return false;
    }

    const isValidType = [
      'text/plain',
      'text/markdown',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/png',
      'application/json',
    ].includes(file.type);

    if (!isValidType) {
      message.error('不支持的文件类型');
      return false;
    }

    return false; // 阻止自动上传，我们手动处理
  };

  return (
    <>
      <Button
        type={type}
        size={size}
        icon={<PlusOutlined />}
        onClick={() => setModalVisible(true)}
        loading={loading}
        className={className}
      >
        新建会话
      </Button>

      <Modal
        title="创建新会话"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => {
          setModalVisible(false);
          setSessionName('');
          setFileList([]);
        }}
        confirmLoading={uploading}
        okText="创建"
        cancelText="取消"
        width={600}
      >
        <div className="space-y-6">
          {/* 会话名称 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              会话名称 <span className="text-red-500">*</span>
            </label>
            <Input
              placeholder="请输入会话名称"
              value={sessionName}
              onChange={(e) => setSessionName(e.target.value)}
              onPressEnter={handleCreate}
              maxLength={50}
              showCount
            />
          </div>

          {/* 初始文件上传 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              初始文件（可选）
            </label>
            <Upload
              multiple
              fileList={fileList}
              onChange={handleFileChange}
              beforeUpload={beforeUpload}
              onRemove={(file) => {
                setFileList(fileList.filter(item => item.uid !== file.uid));
              }}
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
            <div className="text-xs text-gray-500 mt-2">
              支持的文件类型：txt, md, pdf, doc, docx, jpg, png, json
              <br />
              单个文件大小不超过 10MB
            </div>
          </div>

          {/* 文件列表预览 */}
          {fileList.length > 0 && (
            <div>
              <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                已选择文件 ({fileList.length})
              </div>
              <div className="space-y-1">
                {fileList.map((file) => (
                  <div
                    key={file.uid}
                    className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
                  >
                    <span className="text-sm text-gray-600 dark:text-gray-300">
                      {file.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {file.size ? `${(file.size / 1024).toFixed(1)} KB` : ''}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Modal>
    </>
  );
};

export default CreateSessionButton;