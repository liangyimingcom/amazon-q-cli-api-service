#!/usr/bin/env python3
"""
流式对话调试测试脚本
用于测试和调试AI回复内容显示问题
"""

import requests
import json
import time
import threading
from datetime import datetime

def test_standard_chat():
    """测试标准聊天功能"""
    print("🔍 测试标准聊天功能...")
    
    # 创建会话
    session_response = requests.post('http://localhost:8080/api/v1/sessions')
    if session_response.status_code != 201:
        print(f"❌ 创建会话失败: {session_response.status_code}")
        return False
    
    session_data = session_response.json()
    session_id = session_data['session_id']
    print(f"✅ 会话创建成功: {session_id}")
    
    # 发送消息
    chat_data = {
        'session_id': session_id,
        'message': '你好，请简单介绍一下你自己'
    }
    
    chat_response = requests.post('http://localhost:8080/api/v1/chat', json=chat_data)
    if chat_response.status_code != 200:
        print(f"❌ 聊天请求失败: {chat_response.status_code}")
        print(f"响应内容: {chat_response.text}")
        return False
    
    response_data = chat_response.json()
    print(f"✅ 标准聊天成功")
    print(f"📝 AI回复: {response_data.get('response', '无回复内容')}")
    print(f"🔧 响应字段: {list(response_data.keys())}")
    
    return True

def test_stream_chat():
    """测试流式聊天功能"""
    print("\n🔍 测试流式聊天功能...")
    
    # 创建会话
    session_response = requests.post('http://localhost:8080/api/v1/sessions')
    if session_response.status_code != 201:
        print(f"❌ 创建会话失败: {session_response.status_code}")
        return False
    
    session_data = session_response.json()
    session_id = session_data['session_id']
    print(f"✅ 会话创建成功: {session_id}")
    
    # 发送流式消息
    chat_data = {
        'session_id': session_id,
        'message': '请用一段话介绍Amazon Q的主要功能'
    }
    
    print("📡 开始流式请求...")
    response = requests.post(
        'http://localhost:8080/api/v1/chat/stream',
        json=chat_data,
        stream=True,
        headers={'Accept': 'text/event-stream'}
    )
    
    if response.status_code != 200:
        print(f"❌ 流式请求失败: {response.status_code}")
        print(f"响应内容: {response.text}")
        return False
    
    print("✅ 流式连接建立成功")
    print("📥 接收流式数据:")
    
    full_content = []
    chunk_count = 0
    
    try:
        for line in response.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                data_str = line[6:]  # 移除 'data: ' 前缀
                
                if data_str.strip() == '':
                    continue
                
                try:
                    data = json.loads(data_str)
                    chunk_count += 1
                    
                    print(f"  📦 数据块 {chunk_count}: {data}")
                    
                    if data.get('type') == 'session':
                        print(f"    🆔 会话ID: {data.get('session_id')}")
                    elif data.get('type') == 'chunk':
                        message = data.get('message', '')
                        full_content.append(message)
                        print(f"    💬 消息内容: {message}")
                    elif data.get('type') == 'done':
                        print(f"    ✅ 流式传输完成")
                        break
                    elif data.get('type') == 'error':
                        print(f"    ❌ 错误: {data.get('error')}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"    ⚠️  JSON解析失败: {e}")
                    print(f"    原始数据: {data_str}")
                    # 如果不是JSON，直接作为文本处理
                    full_content.append(data_str)
                    
    except Exception as e:
        print(f"❌ 流式数据处理异常: {e}")
        return False
    
    print(f"\n📊 流式测试结果:")
    print(f"  数据块数量: {chunk_count}")
    print(f"  完整内容长度: {len(''.join(full_content))}")
    print(f"  完整内容: {''.join(full_content)}")
    
    return True

def test_frontend_simulation():
    """模拟前端处理逻辑"""
    print("\n🎭 模拟前端处理逻辑...")
    
    # 模拟前端的updateStreamingMessage函数
    streaming_content = ""
    
    def update_streaming_message(session_id, message_id, content):
        nonlocal streaming_content
        streaming_content = content  # 这里可能是问题所在
        print(f"    🔄 更新流式消息: {content}")
    
    # 模拟接收流式数据
    mock_stream_data = [
        {'type': 'session', 'session_id': 'test-session'},
        {'type': 'chunk', 'message': 'Amazon Q 是'},
        {'type': 'chunk', 'message': '一个强大的'},
        {'type': 'chunk', 'message': 'AI助手工具'},
        {'type': 'done'}
    ]
    
    session_id = 'test-session'
    message_id = 'test-message'
    
    for data in mock_stream_data:
        if data.get('type') == 'chunk':
            message = data.get('message', '')
            # 这里是关键：应该累积内容而不是替换
            streaming_content += message
            update_streaming_message(session_id, message_id, streaming_content)
    
    print(f"📝 最终内容: {streaming_content}")
    return True

def main():
    """主测试函数"""
    print("🚀 开始AI回复内容显示问题调试测试")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查后端服务
    try:
        health_response = requests.get('http://localhost:8080/health', timeout=5)
        if health_response.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print(f"⚠️  后端服务状态异常: {health_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接后端服务: {e}")
        print("请确保后端服务在 http://localhost:8080 运行")
        return
    
    # 运行测试
    tests = [
        ("标准聊天", test_standard_chat),
        ("流式聊天", test_stream_chat),
        ("前端模拟", test_frontend_simulation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = False
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    # 分析问题
    print("\n🔍 问题分析:")
    if results.get("标准聊天", False):
        print("  ✅ 标准聊天功能正常，后端API响应正确")
    else:
        print("  ❌ 标准聊天功能异常，需要检查后端API")
    
    if results.get("流式聊天", False):
        print("  ✅ 流式聊天后端功能正常，数据格式正确")
    else:
        print("  ❌ 流式聊天后端功能异常，需要检查流式API")
    
    if results.get("前端模拟", False):
        print("  ✅ 前端处理逻辑模拟正常")
        print("  💡 问题可能在于前端的updateStreamingMessage实现")
        print("     需要检查是否正确累积流式内容而不是替换")
    
    print("\n🎯 修复建议:")
    print("  1. 检查前端updateStreamingMessage函数是否正确累积内容")
    print("  2. 确认前端SSE客户端正确解析message字段")
    print("  3. 验证前端状态管理是否正确更新UI")

if __name__ == "__main__":
    main()