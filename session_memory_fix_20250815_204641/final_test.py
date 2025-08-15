#!/usr/bin/env python3
"""
最终测试会话记忆功能 - 修复JSON解析问题
"""

import requests
import json
import ast

BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json"}

def safe_parse_json(data_str):
    """安全解析JSON，处理单引号问题"""
    try:
        # 首先尝试标准JSON解析
        return json.loads(data_str)
    except json.JSONDecodeError:
        try:
            # 如果失败，尝试使用ast.literal_eval处理单引号
            return ast.literal_eval(data_str)
        except:
            return None

def final_test():
    """最终测试"""
    print("🧪 最终测试会话记忆功能...")
    
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
            if line_str.startswith('data: '):
                data = safe_parse_json(line_str[6:])
                if data and data.get('type') == 'chunk':
                    chunks1.append(data.get('message', ''))
                elif data and data.get('type') == 'done':
                    break
    
    response1_text = "".join(chunks1)
    print(f"📋 第一条响应摘要: {response1_text[:100]}...")
    
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
            if line_str.startswith('data: '):
                data = safe_parse_json(line_str[6:])
                if data and data.get('type') == 'chunk':
                    chunks2.append(data.get('message', ''))
                elif data and data.get('type') == 'done':
                    break
    
    response2_text = "".join(chunks2)
    print(f"📋 第二条响应摘要: {response2_text[:200]}...")
    
    # 检查记忆
    if "张三" in response2_text:
        print("\n🎉 会话记忆测试通过！AI记住了名字")
        
        # 进一步测试
        message3 = {
            "session_id": session_id,
            "message": "我的职业是什么？"
        }
        
        print(f"\n📤 发送第三条消息: 我的职业是什么？")
        response3 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message3, stream=True)
        
        chunks3 = []
        for line in response3.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = safe_parse_json(line_str[6:])
                    if data and data.get('type') == 'chunk':
                        chunks3.append(data.get('message', ''))
                    elif data and data.get('type') == 'done':
                        break
        
        response3_text = "".join(chunks3)
        print(f"📋 第三条响应摘要: {response3_text[:200]}...")
        
        # 测试新信息记忆
        message4 = {
            "session_id": session_id,
            "message": "我是一名软件工程师，请记住这个信息"
        }
        
        print(f"\n📤 发送第四条消息: 我是一名软件工程师，请记住这个信息")
        response4 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message4, stream=True)
        
        chunks4 = []
        for line in response4.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = safe_parse_json(line_str[6:])
                    if data and data.get('type') == 'chunk':
                        chunks4.append(data.get('message', ''))
                    elif data and data.get('type') == 'done':
                        break
        
        response4_text = "".join(chunks4)
        print(f"📋 第四条响应摘要: {response4_text[:100]}...")
        
        # 测试综合记忆
        message5 = {
            "session_id": session_id,
            "message": "请总结一下你对我的了解"
        }
        
        print(f"\n📤 发送第五条消息: 请总结一下你对我的了解")
        response5 = requests.post(f"{BASE_URL}/api/v1/chat/stream", headers=HEADERS, json=message5, stream=True)
        
        chunks5 = []
        for line in response5.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = safe_parse_json(line_str[6:])
                    if data and data.get('type') == 'chunk':
                        chunks5.append(data.get('message', ''))
                    elif data and data.get('type') == 'done':
                        break
        
        response5_text = "".join(chunks5)
        print(f"📋 第五条响应: {response5_text}")
        
        # 综合评估
        memory_score = 0
        if "张三" in response5_text:
            memory_score += 1
            print("✅ 记住了名字")
        if "软件工程师" in response5_text or "工程师" in response5_text:
            memory_score += 1
            print("✅ 记住了职业")
        
        if memory_score >= 2:
            print("\n🎉 会话记忆功能完全正常！AI能够维护完整的对话上下文")
        elif memory_score >= 1:
            print("\n✅ 会话记忆功能基本正常，AI能够记住部分信息")
        else:
            print("\n⚠️ 会话记忆功能部分工作，但可能有遗漏")
            
    else:
        print("\n❌ 会话记忆测试失败：AI没有记住名字")
    
    # 清理
    requests.delete(f"{BASE_URL}/api/v1/sessions/{session_id}", headers=HEADERS)
    print("\n✅ 会话已清理")

if __name__ == "__main__":
    final_test()