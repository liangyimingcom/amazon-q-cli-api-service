#!/usr/bin/env python3
"""
流式聊天Bug调试脚本

用于调试流式聊天接口中上下文处理的问题
"""

import requests
import json
import time
import sys

# 服务器配置
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def test_stream_chat_debug():
    """调试流式聊天问题"""
    print("🔍 开始调试流式聊天问题...")
    
    # 1. 创建新会话
    print("\n1. 创建新会话...")
    session_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    if session_response.status_code != 201:
        print(f"❌ 创建会话失败: {session_response.status_code}")
        return
    
    session_data = session_response.json()
    session_id = session_data["session_id"]
    print(f"✅ 会话创建成功: {session_id}")
    
    # 2. 检查空会话的上下文
    print("\n2. 检查空会话状态...")
    session_info_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    if session_info_response.status_code == 200:
        session_info = session_info_response.json()
        print(f"✅ 会话信息: 消息数量={session_info['message_count']}")
    
    # 3. 发送第一条消息（简单测试）
    print("\n3. 发送简单测试消息...")
    simple_message = {
        "session_id": session_id,
        "message": "你好，请简单介绍一下你自己"
    }
    
    print(f"发送消息: {simple_message['message']}")
    
    # 使用流式接口
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=simple_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 流式聊天失败: {stream_response.status_code}")
        print(f"错误内容: {stream_response.text}")
        return
    
    print("✅ 开始接收流式响应...")
    response_chunks = []
    
    for line in stream_response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]  # 移除 'data: ' 前缀
                try:
                    data = json.loads(data_str)
                    print(f"📦 收到数据块: type={data.get('type', 'unknown')}")
                    if data.get('type') == 'chunk':
                        chunk_content = data.get('message', '')
                        response_chunks.append(chunk_content)
                        print(f"   内容预览: {chunk_content[:100]}...")
                    elif data.get('type') == 'done':
                        print("✅ 流式响应完成")
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ 收到错误: {data}")
                        return
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON解析失败: {e}, 原始数据: {data_str}")
    
    # 4. 检查会话状态（应该有2条消息）
    print("\n4. 检查会话状态...")
    session_info_response = requests.get(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    if session_info_response.status_code == 200:
        session_info = session_info_response.json()
        print(f"✅ 会话信息: 消息数量={session_info['message_count']}")
    
    # 5. 发送第二条消息（问题消息）
    print("\n5. 发送问题消息...")
    problem_message = {
        "session_id": session_id,
        "message": "随机出一个简单的大数据101技术问题，根据spec-driving的开发凡是，写入到3个markdown文件，分别是requirement.md, design.md, task.md"
    }
    
    print(f"发送消息: {problem_message['message']}")
    
    # 使用流式接口
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=problem_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 流式聊天失败: {stream_response.status_code}")
        print(f"错误内容: {stream_response.text}")
        return
    
    print("✅ 开始接收流式响应...")
    problem_response_chunks = []
    
    for line in stream_response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]  # 移除 'data: ' 前缀
                try:
                    data = json.loads(data_str)
                    print(f"📦 收到数据块: type={data.get('type', 'unknown')}")
                    if data.get('type') == 'chunk':
                        chunk_content = data.get('message', '')
                        problem_response_chunks.append(chunk_content)
                        print(f"   内容预览: {chunk_content[:100]}...")
                        
                        # 检查是否包含问题关键词
                        if "对话历史" in chunk_content or "没有看到" in chunk_content:
                            print(f"🚨 发现问题响应: {chunk_content}")
                    elif data.get('type') == 'done':
                        print("✅ 流式响应完成")
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ 收到错误: {data}")
                        return
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON解析失败: {e}, 原始数据: {data_str}")
    
    # 6. 分析结果
    print("\n6. 分析结果...")
    full_response = "".join(problem_response_chunks)
    
    if "对话历史" in full_response or "没有看到" in full_response:
        print("🚨 确认Bug存在: AI要求提供对话历史，但实际上会话中已有消息")
        print(f"完整响应: {full_response[:500]}...")
    else:
        print("✅ 响应正常，没有发现Bug")
    
    # 7. 清理会话
    print(f"\n7. 清理会话 {session_id}...")
    delete_response = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    if delete_response.status_code == 200:
        print("✅ 会话清理完成")
    else:
        print(f"⚠️ 会话清理失败: {delete_response.status_code}")

def test_context_generation():
    """测试上下文生成逻辑"""
    print("\n🔍 测试上下文生成逻辑...")
    
    # 模拟会话消息
    from qcli_api_service.models.core import Message, Session
    
    # 创建测试会话
    session = Session.create_new("test_sessions")
    
    # 添加测试消息
    user_msg1 = Message.create_user_message("你好，请简单介绍一下你自己")
    assistant_msg1 = Message.create_assistant_message("你好！我是Amazon Q，一个AI助手...")
    user_msg2 = Message.create_user_message("随机出一个简单的大数据101技术问题，根据spec-driving的开发凡是，写入到3个markdown文件，分别是requirement.md, design.md, task.md")
    
    session.add_message(user_msg1)
    session.add_message(assistant_msg1)
    session.add_message(user_msg2)
    
    # 生成上下文
    context = session.get_context(10)
    print(f"生成的上下文:\n{context}")
    print(f"上下文长度: {len(context)} 字符")
    
    # 测试消息准备逻辑
    from qcli_api_service.services.qcli_service import qcli_service
    
    prepared_message = qcli_service._prepare_message(user_msg2.content, context)
    print(f"\n准备发送给Q CLI的消息:\n{prepared_message}")
    print(f"消息长度: {len(prepared_message)} 字符")

if __name__ == "__main__":
    print("🚀 开始Bug调试...")
    
    try:
        # 先测试实际API
        test_stream_chat_debug()
        
        # 如果需要，可以单独测试上下文生成
        # test_context_generation()
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()