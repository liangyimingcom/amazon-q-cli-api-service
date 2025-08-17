import React from 'react';
import { Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';

interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  tip?: string;
  spinning?: boolean;
  children?: React.ReactNode;
  className?: string;
}

/**
 * 加载指示器组件
 */
const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  tip,
  spinning = true,
  children,
  className = '',
}) => {
  const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

  if (children) {
    return (
      <Spin
        spinning={spinning}
        indicator={antIcon}
        tip={tip}
        size={size}
        className={className}
      >
        {children}
      </Spin>
    );
  }

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Spin
        indicator={antIcon}
        tip={tip}
        size={size}
      />
    </div>
  );
};

export default LoadingSpinner;