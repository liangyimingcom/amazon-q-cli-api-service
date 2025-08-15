#!/usr/bin/env python3
"""
测试重复内容修复

验证重复内容清理功能是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qcli_api_service.services.qcli_service import QCLIService

def test_duplicate_removal():
    """测试重复内容移除功能"""
    print("=== 测试重复内容移除功能 ===")
    
    service = QCLIService()
    
    # 测试用例1：段落级别重复
    test_text1 = """你好！我是Amazon Q，很高兴为您服务。我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
• 读写文件和目录
• 编写和调试代码
请问有什么我可以帮助您的吗？

你好！我是Amazon Q，很高兴为您服务。我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
• 读写文件和目录
• 编写和调试代码
请问有什么我可以帮助您的吗？"""
    
    print("测试用例1 - 段落级别重复:")
    print(f"原始长度: {len(test_text1)} 字符")
    cleaned1 = service._remove_duplicate_content(test_text1)
    print(f"清理后长度: {len(cleaned1)} 字符")
    print(f"清理后内容:\n{cleaned1}")
    
    # 测试用例2：行级别重复
    test_text2 = """你好！我是Amazon Q，很高兴为您服务。
我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
请问有什么我可以帮助您的吗？
你好！我是Amazon Q，很高兴为您服务。
我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
请问有什么我可以帮助您的吗？"""
    
    print("\n测试用例2 - 行级别重复:")
    print(f"原始长度: {len(test_text2)} 字符")
    cleaned2 = service._remove_duplicate_content(test_text2)
    print(f"清理后长度: {len(cleaned2)} 字符")
    print(f"清理后内容:\n{cleaned2}")
    
    # 测试用例3：无重复内容
    test_text3 = """你好！我是Amazon Q，很高兴为您服务。
我可以帮助您处理各种技术问题。
有什么我可以帮助您的吗？"""
    
    print("\n测试用例3 - 无重复内容:")
    print(f"原始长度: {len(test_text3)} 字符")
    cleaned3 = service._remove_duplicate_content(test_text3)
    print(f"清理后长度: {len(cleaned3)} 字符")
    print(f"清理后内容:\n{cleaned3}")
    
    # 测试用例4：部分重复
    test_text4 = """Python是一种高级编程语言。
它具有以下特点：
• 语法简洁
• 易于学习
• 功能强大

Python是一种高级编程语言。
它具有以下特点：
• 语法简洁
• 易于学习
• 功能强大

Python广泛应用于各个领域。"""
    
    print("\n测试用例4 - 部分重复:")
    print(f"原始长度: {len(test_text4)} 字符")
    cleaned4 = service._remove_duplicate_content(test_text4)
    print(f"清理后长度: {len(cleaned4)} 字符")
    print(f"清理后内容:\n{cleaned4}")

def test_block_removal():
    """测试块级别重复移除"""
    print("\n=== 测试块级别重复移除 ===")
    
    service = QCLIService()
    
    # 测试连续重复块
    lines = [
        "你好！我是Amazon Q",
        "我可以帮助您：",
        "• 管理AWS资源",
        "• 编写代码",
        "你好！我是Amazon Q",
        "我可以帮助您：",
        "• 管理AWS资源", 
        "• 编写代码",
        "有什么问题吗？"
    ]
    
    print("原始行数:", len(lines))
    print("原始内容:")
    for i, line in enumerate(lines):
        print(f"{i}: {line}")
    
    result = service._remove_duplicate_blocks(lines)
    result_lines = result.split('\n')
    
    print(f"\n清理后行数: {len(result_lines)}")
    print("清理后内容:")
    for i, line in enumerate(result_lines):
        print(f"{i}: {line}")

if __name__ == "__main__":
    test_duplicate_removal()
    test_block_removal()