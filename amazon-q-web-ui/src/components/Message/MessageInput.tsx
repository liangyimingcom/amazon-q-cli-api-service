import React, { useState, useRef } from 'react';
import type { KeyboardEvent } from 'react';
import { Input, Button, Space, Tooltip, Upload } from 'antd';
import {
  SendOutlined,
  PaperClipOutlined,
  LoadingOutlined,
} from '@ant-design/icons';

const { TextArea } = Input;

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: (message: string) => void;
  onFileUpload?: (files: File[]) => void;
  disabled?: boolean;
  loading?: boolean;
  placeholder?: string;
  maxLength?: number;
  showFileUpload?: boolean;
}

/**
 * 消息输入组件
 */
const MessageInput: React.FC<MessageInputProps> = ({
  value,
  onChange,
  onSend,
  onFileUpload,
  disabled = false,
  loading = false,
  placeholder = '输入消息...',
  maxLength = 2000,
  showFileUpload = true,
}) => {
  const [rows, setRows] = useState(1);
  const textAreaRef = useRef<any>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    onChange(newValue);

    // 自动调整行数
    const lines = newValue.split('\n').length;
    setRows(Math.min(Math.max(lines, 1), 6));
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = () => {
    const trimmedValue = value.trim();
    if (trimmedValue && !disabled && !loading) {
      onSend(trimmedValue);
      onChange('');
      setRows(1);
      
      // 重新聚焦输入框
      setTimeout(() => {
        textAreaRef.current?.focus();
      }, 0);
    }
  };

  const handleFileChange = (info: any) => {
    const { fileList } = info;
    if (onFileUpload && fileList.length > 0) {
      const files = fileList.map((file: any) => file.originFileObj).filter(Boolean);
      onFileUpload(files);
    }
  };

  const canSend = value.trim().length > 0 && !disabled && !loading;

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <TextArea
            ref={textAreaRef}
            value={value}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            maxLength={maxLength}
            rows={rows}
            autoSize={{ minRows: 1, maxRows: 6 }}
            className="resize-none"
            style={{
              borderRadius: '8px',
            }}
          />
          
          <div className="flex justify-between items-center mt-2">
            <Space>
              {showFileUpload && (
                <Upload
                  multiple
                  showUploadList={false}
                  beforeUpload={() => false}
                  onChange={handleFileChange}
                  disabled={disabled}
                >
                  <Tooltip title="上传文件">
                    <Button
                      type="text"
                      icon={<PaperClipOutlined />}
                      size="small"
                      disabled={disabled}
                      className="text-gray-500 hover:text-blue-500"
                    />
                  </Tooltip>
                </Upload>
              )}
            </Space>
            
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">
                {value.length}/{maxLength}
              </span>
              
              <Tooltip title={canSend ? '发送消息 (Enter)' : '请输入消息'}>
                <Button
                  type="primary"
                  icon={loading ? <LoadingOutlined /> : <SendOutlined />}
                  onClick={handleSend}
                  disabled={!canSend}
                  loading={loading}
                  size="small"
                  className="min-w-[60px]"
                >
                  发送
                </Button>
              </Tooltip>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageInput;