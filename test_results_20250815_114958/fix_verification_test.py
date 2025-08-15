#!/usr/bin/env python3
"""
修复验证测试脚本

验证应用的修复是否有效。
"""

import requests
import time
import json

BASE_URL = "http://localhost:8080"

def test_fix_1_timeout():
    """测试修复1: 带会话聊天超时"""
    print("测试修复1: 带会话聊天超时优化")
    
    # 先创建一个会话并进行对话
    response = requests.post(f"{BASE_URL}/api/v1/chat", 
                           json={"message": "你好，我想了解AWS服务"}, 
                           timeout=60)
    
    if response.status_code != 200:
        print(f"❌ 初始对话失败: {response.status_code}")
        return False
    
    session_id = response.json().get("session_id")
    print(f"✅ 创建会话: {session_id}")
    
    # 进行带会话的对话（应该包含更多上下文）
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/chat", 
                           json={
                               "message": "基于我们刚才的对话，请详细解释一下Amazon EC2的主要功能和使用场景", 
                               "session_id": session_id
                           }, 
                           timeout=90)  # 给更长的超时时间
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"带会话对话耗时: {duration:.2f}秒")
    
    if response.status_code == 200:
        print("✅ 修复1验证成功 - 带会话聊天正常工作")
        return True
    elif response.status_code == 408:
        print(f"❌ 修复1验证失败 - 仍然超时 ({duration:.2f}秒)")
        return False
    else:
        print(f"❌ 修复1验证失败 - 意外错误: {response.status_code}")
        return False

def test_fix_2_special_characters():
    """测试修复2: 特殊字符处理"""
    print("测试修复2: 特殊字符处理优化")
    
    test_cases = [
        {
            "name": "代码标签",
            "message": "请解释这段代码: <code>print('Hello World')</code>",
            "should_pass": True
        },
        {
            "name": "预格式化标签",
            "message": "这是一个示例: <pre>function test() { return true; }</pre>",
            "should_pass": True
        },
        {
            "name": "粗体标签",
            "message": "这是<b>重要</b>的信息",
            "should_pass": True
        },
        {
            "name": "恶意脚本（应该被拒绝）",
            "message": "<script>alert('xss')</script>",
            "should_pass": False
        },
        {
            "name": "事件处理器（应该被拒绝）",
            "message": "<div onclick='alert(1)'>点击</div>",
            "should_pass": False
        }
    ]
    
    results = []
    for test_case in test_cases:
        response = requests.post(f"{BASE_URL}/api/v1/chat", 
                               json={"message": test_case["message"]}, 
                               timeout=30)
        
        success = response.status_code == 200
        expected = test_case["should_pass"]
        
        if success == expected:
            print(f"✅ {test_case['name']}: 预期{'通过' if expected else '拒绝'}, 实际{'通过' if success else '拒绝'}")
            results.append(True)
        else:
            print(f"❌ {test_case['name']}: 预期{'通过' if expected else '拒绝'}, 实际{'通过' if success else '拒绝'}")
            results.append(False)
    
    success_rate = sum(results) / len(results)
    print(f"修复2验证结果: {sum(results)}/{len(results)} ({success_rate*100:.1f}%)")
    
    return success_rate >= 0.8  # 80%以上通过率认为成功

def main():
    """主函数"""
    print("开始修复验证测试")
    print("=" * 50)
    
    # 检查服务器可用性
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器不可用")
            return
    except:
        print("❌ 无法连接到服务器")
        return
    
    print("✅ 服务器连接正常")
    
    # 执行修复验证测试
    results = []
    
    # 测试修复1
    results.append(test_fix_1_timeout())
    
    print()
    
    # 测试修复2
    results.append(test_fix_2_special_characters())
    
    # 汇总结果
    print("=" * 50)
    print("修复验证结果汇总:")
    print(f"修复1 (超时优化): {'✅ 通过' if results[0] else '❌ 失败'}")
    print(f"修复2 (特殊字符): {'✅ 通过' if results[1] else '❌ 失败'}")
    
    overall_success = all(results)
    print(f"整体验证结果: {'✅ 成功' if overall_success else '❌ 失败'}")
    
    if overall_success:
        print("🎉 所有修复验证通过，可以部署到生产环境")
    else:
        print("⚠️ 部分修复验证失败，需要进一步调试")

if __name__ == "__main__":
    main()