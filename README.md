# 项目介绍

## 概述
这是一个基于Flask的RESTful API服务项目，提供Amazon Q CLI集成功能。

## 主要功能
- 🤖 AI对话处理
- 🔄 流式回复支持
- 💬 上下文保持
- 🔧 会话管理
- 📁 会话隔离
- 🛡️ 安全防护

## 技术栈
- Python 3.8+
- Flask框架
- Amazon Q CLI

## 快速开始
1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务：`python app.py`
3. 访问：`http://localhost:8080`

## API接口
- `/health` - 健康检查
- `/api/v1/sessions` - 会话管理
- `/api/v1/chat` - 标准聊天
- `/api/v1/chat/stream` - 流式聊天

更多详细信息请查看完整的README.md文档。
