#!/usr/bin/env python3
"""
详细测试会话记忆功能
"""

import requests
import json

BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def detailed_test():
    """详细测试"""
    print("🧪 详细测试会话记忆...")
    
    # 创建会话
    session_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    session_id = session_response.json()["session_id"]
    print(f"✅ 创建会话: {session_id}")
    
    # 第一条消息
    message1 = {
        "session_id": session_id,
        "message": "你好，我叫张三"
    }
    
    print("\n📤 发送第一条消息: 你好，我叫张三")
    response1 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message1, stream=True)
    
    chunks1 = []
    for line in response1.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            print(f"📥 收到数据: {line_str}")
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    if data.get('type') == 'chunk':
                        chunks1.append(data.get('message', ''))
                    elif data.get('type') == 'done':
                        break
                except Exception as e:
                    print(f"⚠️ JSON解析错误: {e}")
    
    response1_text = "".join(chunks1)
    print(f"\n📋 第一条完整响应:\n{response1_text}")
    
    # 第二条消息
    message2 = {
        "session_id": session_id,
        "message": "你记得我的名字吗？"
    }
    
    print(f"\n📤 发送第二条消息: 你记得我的名字吗？")
    response2 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message2, stream=True)
    
    chunks2 = []
    for line in response2.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            print(f"📥 收到数据: {line_str}")
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    if data.get('type') == 'chunk':
                        chunks2.append(data.get('message', ''))
                    elif data.get('type') == 'done':
                        break
                except Exception as e:
                    print(f"⚠️ JSON解析错误: {e}")
    
    response2_text = "".join(chunks2)
    print(f"\n📋 第二条完整响应:\n{response2_text}")
    
    # 检查记忆
    if "张三" in response2_text:
        print("\n🎉 会话记忆测试通过！AI记住了名字")
    else:
        print("\n❌ 会话记忆测试失败：AI没有记住名字")
        print("可能的原因：")
        print("1. Q Chat进程没有正确维护会话状态")
        print("2. 每次请求都创建了新的Q Chat进程")
        print("3. 消息格式问题")
    
    # 清理
    requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    print("\n✅ 会话已清理")

if __name__ == "__main__":
    detailed_test()