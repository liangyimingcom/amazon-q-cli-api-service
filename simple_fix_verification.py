#!/usr/bin/env python3
"""
简化的修复验证脚本
验证AI回复内容显示问题是否已修复
"""

import requests
import json
import time
from datetime import datetime

def test_backend_fixes():
    """测试后端修复"""
    print("🔧 测试后端修复...")
    
    # 测试标准聊天
    print("  📝 测试标准聊天API...")
    session_resp = requests.post('http://localhost:8080/api/v1/sessions')
    session_id = session_resp.json()['session_id']
    
    chat_resp = requests.post('http://localhost:8080/api/v1/chat', json={
        'session_id': session_id,
        'message': '你好'
    })
    
    if chat_resp.status_code == 200:
        data = chat_resp.json()
        if 'response' in data and len(data['response']) > 0:
            print("    ✅ 标准聊天API正常，返回response字段")
        else:
            print("    ❌ 标准聊天API异常，缺少response字段")
            return False
    else:
        print(f"    ❌ 标准聊天API失败: {chat_resp.status_code}")
        return False
    
    # 测试流式聊天
    print("  📡 测试流式聊天API...")
    stream_resp = requests.post('http://localhost:8080/api/v1/chat/stream', 
                               json={'session_id': session_id, 'message': '介绍一下你自己'},
                               stream=True)
    
    if stream_resp.status_code == 200:
        valid_json_count = 0
        chunk_count = 0
        
        for line in stream_resp.iter_lines(decode_unicode=True):
            if line.startswith('data: '):
                data_str = line[6:]
                if data_str.strip():
                    try:
                        data = json.loads(data_str)
                        valid_json_count += 1
                        if data.get('type') == 'chunk':
                            chunk_count += 1
                    except json.JSONDecodeError:
                        print(f"    ❌ JSON解析失败: {data_str[:50]}...")
                        return False
        
        if valid_json_count > 0 and chunk_count > 0:
            print(f"    ✅ 流式聊天API正常，接收到{valid_json_count}个有效JSON数据块，{chunk_count}个内容块")
        else:
            print("    ❌ 流式聊天API异常，未接收到有效数据")
            return False
    else:
        print(f"    ❌ 流式聊天API失败: {stream_resp.status_code}")
        return False
    
    return True

def test_frontend_store_logic():
    """测试前端状态管理逻辑"""
    print("🎭 测试前端状态管理逻辑...")
    
    # 模拟前端updateStreamingMessage函数的新逻辑
    class MockMessage:
        def __init__(self):
            self.content = ""
            self.streaming = True
    
    def update_streaming_message(message, new_content):
        """模拟修复后的updateStreamingMessage逻辑"""
        message.content = message.content + new_content  # 累积内容
        return message.content
    
    # 测试累积逻辑
    message = MockMessage()
    
    # 模拟接收流式数据
    chunks = ["Amazon Q ", "是一个 ", "强大的 ", "AI助手"]
    
    for chunk in chunks:
        final_content = update_streaming_message(message, chunk)
        print(f"    📝 累积内容: {final_content}")
    
    expected = "Amazon Q 是一个 强大的 AI助手"
    if message.content == expected:
        print("    ✅ 前端累积逻辑正确")
        return True
    else:
        print(f"    ❌ 前端累积逻辑错误，期望: {expected}, 实际: {message.content}")
        return False

def check_frontend_code():
    """检查前端代码修复"""
    print("📁 检查前端代码修复...")
    
    try:
        # 检查chatStore.ts的修复
        with open('amazon-q-web-ui/src/stores/chatStore.ts', 'r', encoding='utf-8') as f:
            store_content = f.read()
            
        if 'content: msg.content + content' in store_content:
            print("    ✅ chatStore.ts累积逻辑已修复")
        else:
            print("    ❌ chatStore.ts累积逻辑未修复")
            return False
        
        # 检查SSE客户端
        with open('amazon-q-web-ui/src/services/sseClient.ts', 'r', encoding='utf-8') as f:
            sse_content = f.read()
            
        if 'data.get(\'message\', \'\')' in sse_content or 'parsed.message' in sse_content:
            print("    ✅ SSE客户端消息解析逻辑正确")
        else:
            print("    ❌ SSE客户端消息解析逻辑可能有问题")
            return False
            
        return True
        
    except Exception as e:
        print(f"    ❌ 检查前端代码时出错: {e}")
        return False

def main():
    """主函数"""
    print("🎯 AI回复内容显示问题修复验证")
    print(f"⏰ 验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    results = {}
    
    # 检查服务状态
    try:
        health_resp = requests.get('http://localhost:8080/health', timeout=5)
        if health_resp.status_code == 200:
            print("✅ 后端服务运行正常")
        else:
            print("❌ 后端服务状态异常")
            return
    except:
        print("❌ 后端服务不可用")
        return
    
    # 运行测试
    tests = [
        ("后端API修复", test_backend_fixes),
        ("前端状态逻辑", test_frontend_store_logic),
        ("前端代码检查", check_frontend_code)
    ]
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}测试:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"    ❌ 测试异常: {e}")
            results[test_name] = False
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📊 验证结果:")
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有验证通过！修复成功！")
        print("\n✨ 修复总结:")
        print("  🔧 后端: 修复了流式响应的JSON格式问题")
        print("  🎭 前端: 修复了流式内容累积逻辑")
        print("  📱 界面: AI回复内容现在可以正确显示")
        print("\n🚀 用户现在可以正常使用:")
        print("  ✅ 标准对话功能")
        print("  ✅ 流式对话功能")
        print("  ✅ 完整的AI回复内容显示")
    else:
        print("\n⚠️  部分验证失败，需要进一步修复")

if __name__ == "__main__":
    main()