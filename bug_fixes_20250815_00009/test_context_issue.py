#!/usr/bin/env python3
"""
测试上下文问题

验证重复问题是否来自上下文处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qcli_api_service.models.core import Session, Message
from qcli_api_service.services.qcli_service import qcli_service

def test_context_accumulation():
    """测试上下文累积问题"""
    print("=== 测试上下文累积问题 ===")
    
    # 创建一个会话
    session = Session.create_new("test_sessions")
    
    # 模拟第一次对话
    print("\n1. 第一次对话（无上下文）")
    user_msg1 = Message.create_user_message("你好")
    session.add_message(user_msg1)
    
    context1 = session.get_context()
    print(f"上下文1: {repr(context1)}")
    
    # 模拟助手回复（包含重复内容）
    duplicate_response = """你好！我是Amazon Q，很高兴为您服务。我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
请问有什么我可以帮助您的吗？
你好！我是Amazon Q，很高兴为您服务。我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
请问有什么我可以帮助您的吗？"""
    
    assistant_msg1 = Message.create_assistant_message(duplicate_response)
    session.add_message(assistant_msg1)
    
    # 模拟第二次对话
    print("\n2. 第二次对话（有上下文）")
    user_msg2 = Message.create_user_message("介绍Python")
    session.add_message(user_msg2)
    
    context2 = session.get_context()
    print(f"上下文2长度: {len(context2)} 字符")
    print(f"上下文2内容: {repr(context2[:200])}...")
    
    # 检查上下文中是否包含重复内容
    if "你好！我是Amazon Q" in context2:
        duplicate_count = context2.count("你好！我是Amazon Q")
        print(f"上下文中包含重复内容，重复次数: {duplicate_count}")
    
    # 准备发送给Q CLI的消息
    prepared_message = qcli_service._prepare_message("介绍Python", context2)
    print(f"\n准备发送给Q CLI的消息长度: {len(prepared_message)} 字符")
    print(f"消息开头: {repr(prepared_message[:200])}...")
    
    # 清理测试目录
    import shutil
    if os.path.exists("test_sessions"):
        shutil.rmtree("test_sessions")

def test_clean_context():
    """测试清理后的上下文"""
    print("\n=== 测试清理后的上下文 ===")
    
    # 创建一个会话
    session = Session.create_new("test_sessions")
    
    # 添加正常的对话
    user_msg = Message.create_user_message("你好")
    session.add_message(user_msg)
    
    clean_response = "你好！我是Amazon Q，很高兴为您服务。我可以帮助您处理各种技术问题。"
    assistant_msg = Message.create_assistant_message(clean_response)
    session.add_message(assistant_msg)
    
    # 获取上下文
    context = session.get_context()
    print(f"清理后的上下文: {repr(context)}")
    
    # 准备消息
    prepared_message = qcli_service._prepare_message("介绍Python", context)
    print(f"准备的消息: {repr(prepared_message[:200])}...")
    
    # 清理测试目录
    import shutil
    if os.path.exists("test_sessions"):
        shutil.rmtree("test_sessions")

if __name__ == "__main__":
    test_context_accumulation()
    test_clean_context()