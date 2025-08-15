#!/usr/bin/env python3
"""
调试上下文内容脚本

专门用于调试第一次调用时的上下文问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qcli_api_service.models.core import Message, Session
from qcli_api_service.services.qcli_service import qcli_service

def test_context_logic():
    """测试上下文逻辑"""
    print("🔍 测试上下文处理逻辑...")
    
    # 1. 测试空会话
    print("\n1. 测试空会话:")
    session = Session.create_new("test_sessions")
    context = session.get_context(10)
    print(f"   空会话上下文: '{context}'")
    print(f"   上下文长度: {len(context)}")
    print(f"   上下文repr: {repr(context)}")
    print(f"   bool(context): {bool(context)}")
    print(f"   context.strip(): '{context.strip()}'")
    print(f"   bool(context.strip()): {bool(context.strip())}")
    
    # 2. 测试消息准备
    print("\n2. 测试消息准备:")
    message = "你好，请简单介绍一下你自己"
    prepared = qcli_service._prepare_message(message, context)
    print(f"   原始消息: {message}")
    print(f"   准备后消息: {prepared}")
    
    # 3. 测试有一条消息的会话
    print("\n3. 测试有一条消息的会话:")
    user_msg = Message.create_user_message("你好，请简单介绍一下你自己")
    session.add_message(user_msg)
    context_with_one = session.get_context(10)
    print(f"   一条消息上下文: '{context_with_one}'")
    print(f"   上下文长度: {len(context_with_one)}")
    print(f"   bool(context_with_one): {bool(context_with_one)}")
    
    prepared_with_one = qcli_service._prepare_message("第二条消息", context_with_one)
    print(f"   准备后消息: {prepared_with_one}")
    
    # 4. 测试有两条消息的会话
    print("\n4. 测试有两条消息的会话:")
    assistant_msg = Message.create_assistant_message("你好！我是Amazon Q...")
    session.add_message(assistant_msg)
    context_with_two = session.get_context(10)
    print(f"   两条消息上下文: '{context_with_two}'")
    print(f"   上下文长度: {len(context_with_two)}")
    
    prepared_with_two = qcli_service._prepare_message("第三条消息", context_with_two)
    print(f"   准备后消息: {prepared_with_two}")

def test_config_force_chinese():
    """测试FORCE_CHINESE配置"""
    print("\n🔍 测试FORCE_CHINESE配置...")
    from qcli_api_service.config import config
    print(f"   FORCE_CHINESE: {config.FORCE_CHINESE}")

if __name__ == "__main__":
    print("🚀 开始上下文调试...")
    
    try:
        test_config_force_chinese()
        test_context_logic()
        
    except Exception as e:
        print(f"\n❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()