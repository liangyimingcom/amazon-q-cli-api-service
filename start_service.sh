#!/bin/bash

# 激活虚拟环境并启动服务
source venv/bin/activate

# 检查端口是否被占用，如果是则终止占用进程
if lsof -ti:8080 > /dev/null; then
    echo "终止占用8080端口的进程..."
    kill -9 $(lsof -ti:8080)
    sleep 2
fi

# 检查端口是否被占用，如果是则终止占用进程
if lsof -ti:3000 > /dev/null; then
    echo "终止占用3000端口的进程..."
    kill -9 $(lsof -ti:3000)
    sleep 2
fi

# 启动服务
echo "启动Amazon Q CLI API服务..."
python app.py &

# 启动服务2
cd amazon-q-web-ui && npm run dev &