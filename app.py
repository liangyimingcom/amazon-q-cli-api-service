#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amazon Q CLI API服务主入口 - 核心版本

启动Flask应用服务器。
"""

import logging
import sys
import os
from qcli_api_service.config import config
from qcli_api_service.app import create_app

# 设置环境编码
os.environ['PYTHONIOENCODING'] = 'utf-8'


def main():
    """主函数"""
    try:
        # 验证配置
        config.validate()
        
        # 设置基本日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)
        
        logger.info(f"启动Amazon Q CLI API服务...")
        logger.info(f"配置: HOST={config.HOST}, PORT={config.PORT}, DEBUG={config.DEBUG}")
        
        # 创建Flask应用
        app = create_app()
        
        # 启动服务
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
        
    except Exception as e:
        print(f"启动服务失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()