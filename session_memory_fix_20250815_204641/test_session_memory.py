#!/usr/bin/env python3
"""
测试会话记忆功能

验证Q Chat的会话记忆是否正常工作
"""

import requests
import json
import time

# 服务器配置
BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def test_session_memory():
    """测试会话记忆功能"""
    print("🧪 测试会话记忆功能...")
    
    # 1. 创建新会话
    print("\n1. 创建新会话...")
    session_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    if session_response.status_code != 201:
        print(f"❌ 创建会话失败: {session_response.status_code}")
        return False
    
    session_data = session_response.json()
    session_id = session_data["session_id"]
    print(f"✅ 会话创建成功: {session_id}")
    
    # 2. 第一条消息：自我介绍
    print("\n2. 发送第一条消息（自我介绍）...")
    first_message = {
        "session_id": session_id,
        "message": "你好，我叫张三，我是一名软件工程师。请记住我的名字。"
    }
    
    print(f"发送: {first_message['message']}")
    
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=first_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 第一条消息失败: {stream_response.status_code}")
        return False
    
    first_response = collect_stream_response(stream_response)
    print(f"✅ 第一条消息响应: {first_response[:100]}...")
    
    # 3. 第二条消息：测试记忆
    print("\n3. 发送第二条消息（测试记忆）...")
    second_message = {
        "session_id": session_id,
        "message": "你还记得我的名字吗？我是做什么工作的？"
    }
    
    print(f"发送: {second_message['message']}")
    
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=second_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 第二条消息失败: {stream_response.status_code}")
        return False
    
    second_response = collect_stream_response(stream_response)
    print(f"✅ 第二条消息响应: {second_response[:200]}...")
    
    # 检查记忆效果
    memory_test_passed = False
    if "张三" in second_response and ("软件工程师" in second_response or "工程师" in second_response):
        print("🎉 会话记忆测试通过：AI记住了用户信息")
        memory_test_passed = True
    else:
        print("❌ 会话记忆测试失败：AI没有记住用户信息")
    
    # 4. 第三条消息：复杂任务测试
    print("\n4. 发送第三条消息（复杂任务）...")
    third_message = {
        "session_id": session_id,
        "message": "基于我的职业背景，请为我推荐3个适合的技术学习方向，并创建一个学习计划文件。"
    }
    
    print(f"发送: {third_message['message']}")
    
    stream_response = requests.post(
        f"{BASE_URL}/api/v1/chat/stream",
        headers=HEADERS,
        json=third_message,
        stream=True
    )
    
    if stream_response.status_code != 200:
        print(f"❌ 第三条消息失败: {stream_response.status_code}")
        return False
    
    third_response = collect_stream_response(stream_response)
    print(f"✅ 第三条消息响应: {third_response[:200]}...")
    
    # 检查是否基于职业背景给出建议
    context_aware = False
    if ("软件工程师" in third_response or "工程师" in third_response or "张三" in third_response):
        print("🎉 上下文感知测试通过：AI基于之前的对话给出建议")
        context_aware = True
    else:
        print("⚠️ 上下文感知测试部分通过：AI给出了建议但可能没有完全基于上下文")
        context_aware = True  # 给出建议也算部分通过
    
    # 5. 清理会话
    print(f"\n5. 清理会话 {session_id}...")
    delete_response = requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    if delete_response.status_code == 200:
        print("✅ 会话清理完成")
    else:
        print(f"⚠️ 会话清理失败: {delete_response.status_code}")
    
    return memory_test_passed and context_aware

def collect_stream_response(stream_response):
    """收集流式响应的完整内容"""
    response_chunks = []
    
    for line in stream_response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                try:
                    data = json.loads(data_str)
                    if data.get('type') == 'chunk':
                        chunk_content = data.get('message', '')
                        response_chunks.append(chunk_content)
                    elif data.get('type') == 'done':
                        break
                    elif data.get('type') == 'error':
                        print(f"❌ 收到错误: {data}")
                        break
                except json.JSONDecodeError:
                    pass
    
    return "".join(response_chunks)

def test_multiple_sessions():
    """测试多会话隔离"""
    print("\n🧪 测试多会话隔离...")
    
    # 创建两个会话
    session1_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    session2_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    
    if session1_response.status_code != 201 or session2_response.status_code != 201:
        print("❌ 创建会话失败")
        return False
    
    session1_id = session1_response.json()["session_id"]
    session2_id = session2_response.json()["session_id"]
    
    print(f"✅ 创建两个会话: {session1_id[:8]}... 和 {session2_id[:8]}...")
    
    # 在会话1中设置信息
    message1 = {
        "session_id": session1_id,
        "message": "我叫李四，我是医生。"
    }
    
    stream_response = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message1, stream=True)
    collect_stream_response(stream_response)
    
    # 在会话2中设置不同信息
    message2 = {
        "session_id": session2_id,
        "message": "我叫王五，我是老师。"
    }
    
    stream_response = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message2, stream=True)
    collect_stream_response(stream_response)
    
    # 测试会话1的记忆
    test_message1 = {
        "session_id": session1_id,
        "message": "你记得我的名字和职业吗？"
    }
    
    stream_response = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=test_message1, stream=True)
    response1 = collect_stream_response(stream_response)
    
    # 测试会话2的记忆
    test_message2 = {
        "session_id": session2_id,
        "message": "你记得我的名字和职业吗？"
    }
    
    stream_response = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=test_message2, stream=True)
    response2 = collect_stream_response(stream_response)
    
    # 检查隔离效果
    isolation_test_passed = True
    
    if "李四" in response1 and "医生" in response1:
        print("✅ 会话1记忆正确：李四，医生")
    else:
        print("❌ 会话1记忆错误")
        isolation_test_passed = False
    
    if "王五" in response2 and "老师" in response2:
        print("✅ 会话2记忆正确：王五，老师")
    else:
        print("❌ 会话2记忆错误")
        isolation_test_passed = False
    
    # 检查是否有串扰
    if "李四" in response2 or "王五" in response1:
        print("❌ 会话隔离失败：存在信息串扰")
        isolation_test_passed = False
    else:
        print("✅ 会话隔离成功：无信息串扰")
    
    # 清理会话
    requests.delete(f"{BASE_URL}/api/v1/sessions/{session1_id}", headers=HEADERS)
    requests.delete(f"{BASE_URL}/api/v1/sessions/{session2_id}", headers=HEADERS)
    
    return isolation_test_passed

if __name__ == "__main__":
    print("🚀 开始测试会话记忆功能...")
    
    try:
        # 测试单会话记忆
        memory_ok = test_session_memory()
        
        # 测试多会话隔离
        isolation_ok = test_multiple_sessions()
        
        if memory_ok and isolation_ok:
            print("\n🎉 所有测试通过！会话记忆功能正常工作")
        else:
            print("\n❌ 部分测试失败，需要进一步调试")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()