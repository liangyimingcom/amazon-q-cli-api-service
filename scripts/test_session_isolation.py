#!/usr/bin/env python3
"""
会话隔离功能测试脚本

测试会话隔离功能是否正常工作。
"""

import sys
import os
import requests
import json
import time
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 服务基础URL
BASE_URL = "http://localhost:8080"


def test_api_call(method: str, url: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
    """测试API调用"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data)
        elif method.upper() == 'DELETE':
            response = requests.delete(url)
        else:
            raise ValueError(f"不支持的HTTP方法: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ API调用失败: {e}")
        return None


def test_service_health():
    """测试服务健康状态"""
    print("🔍 测试服务健康状态...")
    
    result = test_api_call('GET', f"{BASE_URL}/health")
    if result and result.get('status') == 'healthy':
        print("✅ 服务健康状态正常")
        return True
    else:
        print("❌ 服务健康状态异常")
        return False


def test_session_creation():
    """测试会话创建"""
    print("\n🔍 测试会话创建...")
    
    result = test_api_call('POST', f"{BASE_URL}/api/v1/sessions")
    if result and 'session_id' in result:
        session_id = result['session_id']
        print(f"✅ 会话创建成功: {session_id}")
        return session_id
    else:
        print("❌ 会话创建失败")
        return None


def test_session_info(session_id: str):
    """测试获取会话信息"""
    print(f"\n🔍 测试获取会话信息: {session_id}")
    
    result = test_api_call('GET', f"{BASE_URL}/api/v1/sessions/{session_id}")
    if result and 'work_directory' in result:
        work_dir = result['work_directory']
        abs_work_dir = result['absolute_work_directory']
        print(f"✅ 会话信息获取成功")
        print(f"   工作目录: {work_dir}")
        print(f"   绝对路径: {abs_work_dir}")
        return work_dir, abs_work_dir
    else:
        print("❌ 获取会话信息失败")
        return None, None


def test_session_files(session_id: str):
    """测试获取会话文件列表"""
    print(f"\n🔍 测试获取会话文件列表: {session_id}")
    
    result = test_api_call('GET', f"{BASE_URL}/api/v1/sessions/{session_id}/files")
    if result is not None:
        file_count = result.get('file_count', 0)
        files = result.get('files', [])
        print(f"✅ 会话文件列表获取成功")
        print(f"   文件数量: {file_count}")
        if files:
            print("   文件列表:")
            for file_info in files:
                print(f"     - {file_info['name']} ({file_info['size']} bytes)")
        return True
    else:
        print("❌ 获取会话文件列表失败")
        return False


def test_chat_with_file_creation(session_id: str):
    """测试在会话中创建文件"""
    print(f"\n🔍 测试在会话中创建文件: {session_id}")
    
    # 发送创建文件的消息
    chat_data = {
        "session_id": session_id,
        "message": "请创建一个名为test.txt的文件，内容为'Hello from session isolation test!'"
    }
    
    result = test_api_call('POST', f"{BASE_URL}/api/v1/chat", chat_data)
    if result and 'message' in result:
        print("✅ 聊天请求成功")
        print(f"   AI回复: {result['message'][:100]}...")
        return True
    else:
        print("❌ 聊天请求失败")
        return False


def test_directory_isolation():
    """测试目录隔离"""
    print("\n🔍 测试目录隔离功能...")
    
    # 创建两个会话
    session1 = test_session_creation()
    if not session1:
        return False
    
    time.sleep(1)  # 稍等一下
    
    session2 = test_session_creation()
    if not session2:
        return False
    
    # 获取两个会话的工作目录
    work_dir1, abs_work_dir1 = test_session_info(session1)
    work_dir2, abs_work_dir2 = test_session_info(session2)
    
    if not work_dir1 or not work_dir2:
        return False
    
    # 验证目录不同
    if work_dir1 != work_dir2:
        print("✅ 会话目录隔离正常")
        print(f"   会话1目录: {work_dir1}")
        print(f"   会话2目录: {work_dir2}")
    else:
        print("❌ 会话目录隔离失败 - 目录相同")
        return False
    
    # 验证目录实际存在
    if os.path.exists(abs_work_dir1) and os.path.exists(abs_work_dir2):
        print("✅ 会话目录物理存在")
    else:
        print("❌ 会话目录物理不存在")
        return False
    
    return True


def test_session_cleanup(session_id: str):
    """测试会话清理"""
    print(f"\n🔍 测试会话清理: {session_id}")
    
    # 获取会话信息
    work_dir, abs_work_dir = test_session_info(session_id)
    if not abs_work_dir:
        return False
    
    # 删除会话
    result = test_api_call('DELETE', f"{BASE_URL}/api/v1/sessions/{session_id}")
    if result and 'message' in result:
        print("✅ 会话删除成功")
        
        # 检查目录是否被清理
        time.sleep(1)  # 等待清理完成
        if not os.path.exists(abs_work_dir):
            print("✅ 会话目录清理成功")
            return True
        else:
            print("❌ 会话目录清理失败 - 目录仍然存在")
            return False
    else:
        print("❌ 会话删除失败")
        return False


def main():
    """主测试函数"""
    print("🚀 开始会话隔离功能测试")
    print("=" * 50)
    
    # 测试服务健康状态
    if not test_service_health():
        print("\n❌ 服务不可用，测试终止")
        sys.exit(1)
    
    # 测试会话创建
    session_id = test_session_creation()
    if not session_id:
        print("\n❌ 会话创建失败，测试终止")
        sys.exit(1)
    
    # 测试会话信息获取
    work_dir, abs_work_dir = test_session_info(session_id)
    if not work_dir:
        print("\n❌ 会话信息获取失败，测试终止")
        sys.exit(1)
    
    # 测试会话文件列表（初始为空）
    test_session_files(session_id)
    
    # 测试在会话中创建文件
    test_chat_with_file_creation(session_id)
    
    # 再次检查文件列表
    time.sleep(2)  # 等待文件创建
    test_session_files(session_id)
    
    # 测试目录隔离
    test_directory_isolation()
    
    # 测试会话清理
    test_session_cleanup(session_id)
    
    print("\n" + "=" * 50)
    print("🎉 会话隔离功能测试完成")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)