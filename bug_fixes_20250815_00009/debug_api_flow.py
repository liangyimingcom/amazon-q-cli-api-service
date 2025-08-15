#!/usr/bin/env python3
"""
调试API流程

跟踪API调用的完整流程，找出重复内容的来源
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qcli_api_service.services.qcli_service import qcli_service
from qcli_api_service.services.session_manager import session_manager
from qcli_api_service.models.core import Message

def debug_api_flow():
    """调试API流程"""
    print("=== 调试API流程 ===")
    
    # 1. 创建会话
    session = session_manager.create_session()
    print(f"1. 创建会话: {session.session_id}")
    
    # 2. 第一次调用 - 无上下文
    message1 = "你好"
    print(f"\n2. 第一次调用消息: {repr(message1)}")
    
    # 添加用户消息
    user_msg1 = Message.create_user_message(message1)
    session_manager.add_message(session.session_id, user_msg1)
    
    # 获取上下文（应该只有用户消息）
    context1 = session_manager.get_context(session.session_id)
    print(f"   上下文1: {repr(context1)}")
    
    # 调用Q CLI
    try:
        response1 = qcli_service.chat(message1, context1, session.work_directory)
        print(f"   Q CLI响应长度: {len(response1)} 字符")
        print(f"   Q CLI响应内容: {repr(response1[:200])}...")
        
        # 添加助手回复
        assistant_msg1 = Message.create_assistant_message(response1)
        session_manager.add_message(session.session_id, assistant_msg1)
        
        print(f"   保存到会话的响应长度: {len(assistant_msg1.content)} 字符")
        
    except Exception as e:
        print(f"   Q CLI调用失败: {e}")
        return
    
    # 3. 第二次调用 - 有上下文
    message2 = "介绍Python"
    print(f"\n3. 第二次调用消息: {repr(message2)}")
    
    # 添加用户消息
    user_msg2 = Message.create_user_message(message2)
    session_manager.add_message(session.session_id, user_msg2)
    
    # 获取上下文（包含之前的对话）
    context2 = session_manager.get_context(session.session_id)
    print(f"   上下文2长度: {len(context2)} 字符")
    print(f"   上下文2内容: {repr(context2[:300])}...")
    
    # 检查上下文中是否有重复内容
    if "我可以帮助" in context2:
        count = context2.count("我可以帮助")
        print(f"   上下文中'我可以帮助'出现次数: {count}")
    
    # 准备发送给Q CLI的消息
    prepared_msg = qcli_service._prepare_message(message2, context2)
    print(f"   准备的消息长度: {len(prepared_msg)} 字符")
    print(f"   准备的消息内容: {repr(prepared_msg[:300])}...")
    
    # 清理会话
    session_manager.delete_session(session.session_id)

def test_qcli_direct_call():
    """直接测试Q CLI调用"""
    print("\n=== 直接测试Q CLI调用 ===")
    
    try:
        # 无上下文调用
        response1 = qcli_service.chat("你好", "", None)
        print(f"无上下文响应长度: {len(response1)} 字符")
        print(f"无上下文响应: {repr(response1)}")
        
        # 检查是否有重复
        lines = response1.split('\n')
        line_counts = {}
        for line in lines:
            line = line.strip()
            if line:
                line_counts[line] = line_counts.get(line, 0) + 1
        
        print("\n重复行检查:")
        for line, count in line_counts.items():
            if count > 1:
                print(f"  重复{count}次: {repr(line)}")
        
        # 检查是否有相似内容
        print("\n相似内容检查:")
        for i, line1 in enumerate(lines):
            for j, line2 in enumerate(lines[i+1:], i+1):
                line1 = line1.strip()
                line2 = line2.strip()
                if line1 and line2 and line1 != line2:
                    if len(line1) > 20 and len(line2) > 20:
                        # 检查是否有显著重叠
                        words1 = set(line1.split())
                        words2 = set(line2.split())
                        overlap = len(words1 & words2)
                        if overlap > 3:  # 如果有超过3个相同词汇
                            print(f"  相似行 {i} 和 {j} (重叠{overlap}词):")
                            print(f"    {repr(line1)}")
                            print(f"    {repr(line2)}")
        
    except Exception as e:
        print(f"Q CLI调用失败: {e}")

if __name__ == "__main__":
    debug_api_flow()
    test_qcli_direct_call()