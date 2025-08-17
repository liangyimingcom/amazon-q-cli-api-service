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
if lsof -ti:8081 > /dev/null; then
    echo "终止占用8081端口的进程..."
    kill -9 $(lsof -ti:8081)
    sleep 2
fi


# 检查端口是否被占用，如果是则终止占用进程
if lsof -ti:3001 > /dev/null; then
    echo "终止占用3001端口的进程..."
    kill -9 $(lsof -ti:3001)
    sleep 2
fi
