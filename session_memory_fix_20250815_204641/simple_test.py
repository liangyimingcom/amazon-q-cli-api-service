#!/usr/bin/env python3
"""
简单测试会话记忆功能
"""

import requests
import json

BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def simple_test():
    """简单测试"""
    print("🧪 简单测试会话记忆...")
    
    # 创建会话
    session_response = requests.post(f"{BASE_URL}/api/v1/sessions", headers=HEADERS)
    session_id = session_response.json()["session_id"]
    print(f"✅ 创建会话: {session_id}")
    
    # 第一条消息
    message1 = {
        "session_id": session_id,
        "message": "你好，我叫张三"
    }
    
    print("发送第一条消息...")
    response1 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message1, stream=True)
    
    chunks1 = []
    for line in response1.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    if data.get('type') == 'chunk':
                        chunks1.append(data.get('message', ''))
                    elif data.get('type') == 'done':
                        break
                except:
                    pass
    
    response1_text = "".join(chunks1)
    print(f"第一条响应: {response1_text[:100]}...")
    
    # 第二条消息
    message2 = {
        "session_id": session_id,
        "message": "你记得我的名字吗？"
    }
    
    print("发送第二条消息...")
    response2 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message2, stream=True)
    
    chunks2 = []
    for line in response2.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                try:
                    data = json.loads(line_str[6:])
                    if data.get('type') == 'chunk':
                        chunks2.append(data.get('message', ''))
                    elif data.get('type') == 'done':
                        break
                except:
                    pass
    
    response2_text = "".join(chunks2)
    print(f"第二条响应: {response2_text[:200]}...")
    
    # 检查记忆
    if "张三" in response2_text:
        print("🎉 会话记忆测试通过！")
    else:
        print("❌ 会话记忆测试失败")
    
    # 清理
    requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    print("✅ 会话已清理")

if __name__ == "__main__":
    simple_test()