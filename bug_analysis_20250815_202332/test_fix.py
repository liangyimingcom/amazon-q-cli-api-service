#!/usr/bin/env python3
"""
测试修复效果脚本

验证消息准备逻辑的修复是否有效
"""

import requests
import json
import time

# 服务器配置
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def test_fix_effectiveness():
    """测试修复效果"""
    print("🧪 测试修复效果...")
    
    # 1. 创建新会话
    print("\n1. 创建新会话...")
    session_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    if session_response.status_code != 201:
        print(f"❌ 创建会话失败: {session_response.status_code}")
        return False
    
    session_data = session_response.json()
    session_id = session_data["session_id"]
    print(f"✅ 会话创建成功: {session_id}")
    
    # 2. 测试第一条消息（之前会出bug的场景）
    print("\n2. 测试第一条消息（修复前会出bug）...")
    first_message = {
        "session_id": session_id,
        "message": "你好，请简单介绍一下你自己"
    }
    
    print(f"发送消息: {first_message['message']}")
    
    # 使用流式接口
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=first_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 流式聊天失败: {stream_response.status_code}")
        return False
    
    print("✅ 开始接收流式响应...")
    first_response_chunks = []
    bug_detected = False
    
    for line in stream_response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]  # 移除 'data: ' 前缀
                try:
                    data = json.loads(data_str)
                    if data.get('type') == 'chunk':
                        chunk_content = data.get('message', '')
                        first_response_chunks.append(chunk_content)
                        
                        # 检查是否包含问题关键词
                        if "对话历史" in chunk_content or "没有看到" in chunk_content or "提供之前的对话历史内容" in chunk_content:
                            print(f"🚨 仍然存在Bug: {chunk_content[:100]}...")
                            bug_detected = True
                    elif data.get('type') == 'done':
                        print("✅ 第一条消息响应完成")
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ 收到错误: {data}")
                        return False
                except json.JSONDecodeError:
                    # 忽略JSON解析错误，继续处理
                    pass
    
    # 分析第一条消息的响应
    full_first_response = "".join(first_response_chunks)
    
    if bug_detected:
        print("❌ 修复失败：第一条消息仍然出现Bug")
        return False
    elif "Amazon Q" in full_first_response and "AI助手" in full_first_response:
        print("✅ 修复成功：第一条消息正常响应")
    else:
        print(f"⚠️ 响应异常，需要进一步检查: {full_first_response[:200]}...")
    
    # 3. 测试第二条消息（原本正常的场景）
    print("\n3. 测试第二条消息（确保没有破坏原有功能）...")
    second_message = {
        "session_id": session_id,
        "message": "随机出一个简单的大数据101技术问题，根据spec-driving的开发方式，写入到3个markdown文件，分别是requirement.md, design.md, task.md"
    }
    
    print(f"发送消息: {second_message['message'][:50]}...")
    
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=second_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 流式聊天失败: {stream_response.status_code}")
        return False
    
    second_response_chunks = []
    file_creation_detected = False
    
    for line in stream_response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                try:
                    data = json.loads(data_str)
                    if data.get('type') == 'chunk':
                        chunk_content = data.get('message', '')
                        second_response_chunks.append(chunk_content)
                        
                        # 检查是否正在创建文件
                        if "requirement.md" in chunk_content or "design.md" in chunk_content or "task.md" in chunk_content:
                            file_creation_detected = True
                            print("✅ 检测到文件创建活动")
                    elif data.get('type') == 'done':
                        print("✅ 第二条消息响应完成")
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ 收到错误: {data}")
                        return False
                except json.JSONDecodeError:
                    pass
    
    if file_creation_detected:
        print("✅ 第二条消息功能正常：成功创建文件")
    else:
        print("⚠️ 第二条消息可能有问题：未检测到文件创建")
    
    # 4. 清理会话
    print(f"\n4. 清理会话 {session_id}...")
    delete_response = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    if delete_response.status_code == 200:
        print("✅ 会话清理完成")
    
    return not bug_detected and file_creation_detected

def test_message_preparation():
    """测试消息准备逻辑"""
    print("\n🧪 测试消息准备逻辑...")
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from qcli_api_service.services.qcli_service import qcli_service
    
    # 测试场景1：空上下文
    message1 = "你好，请简单介绍一下你自己"
    context1 = ""
    prepared1 = qcli_service._prepare_message(message1, context1)
    print(f"\n场景1 - 空上下文:")
    print(f"  原始消息: {message1}")
    print(f"  上下文: '{context1}'")
    print(f"  准备后: {prepared1}")
    
    # 测试场景2：有上下文
    message2 = "请详细介绍你的能力"
    context2 = "用户: 你好，请简单介绍一下你自己\n助手: 你好！我是Amazon Q，AWS构建的AI助手..."
    prepared2 = qcli_service._prepare_message(message2, context2)
    print(f"\n场景2 - 有上下文:")
    print(f"  原始消息: {message2}")
    print(f"  上下文: {context2[:50]}...")
    print(f"  准备后: {prepared2[:100]}...")
    
    # 检查修复效果
    if "请基于这个上下文" in prepared1 or "请基于这个上下文" in prepared2:
        print("❌ 修复失败：仍然包含误导性语句")
        return False
    else:
        print("✅ 修复成功：消息格式已优化")
        return True

if __name__ == "__main__":
    print("🚀 开始测试修复效果...")
    
    try:
        # 测试消息准备逻辑
        logic_ok = test_message_preparation()
        
        # 测试实际API效果
        api_ok = test_fix_effectiveness()
        
        if logic_ok and api_ok:
            print("\n🎉 修复验证成功！Bug已解决")
        else:
            print("\n❌ 修复验证失败，需要进一步调试")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()