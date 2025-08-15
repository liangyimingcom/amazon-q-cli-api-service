#!/usr/bin/env python3
"""
测试改进的重复检测算法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qcli_api_service.services.qcli_service import QCLIService

def test_improved_deduplication():
    """测试改进的重复检测"""
    print("=== 测试改进的重复检测算法 ===")
    
    service = QCLIService()
    
    # 测试用例1：语义相似的重复
    test_text1 = """请您：
1. 提供之前的对话历史内容
2. 明确说明您希望我回答的具体问题
这样我就能基于上下文为您提供准确的中文回答了。
• 管理和查询 AWS 资源
• 读写本地文件系统
• 执行 bash 命令
• 编写和调试代码
• 提供 AWS 最佳实践建议
• 协助基础设施配置
有什么我可以帮助您的吗？
• AWS 服务管理和配置
• 文件系统操作
• 代码编写和调试
• 命令行操作
• 基础设施优化
请问有什么我可以帮助您的吗？"""
    
    print("测试用例1 - 语义相似的重复:")
    print(f"原始长度: {len(test_text1)} 字符")
    print(f"原始内容:\n{test_text1}")
    
    cleaned1 = service._remove_duplicate_content(test_text1)
    print(f"\n清理后长度: {len(cleaned1)} 字符")
    print(f"清理后内容:\n{cleaned1}")
    
    # 测试用例2：完全重复的段落
    test_text2 = """你好！我是Amazon Q，很高兴为您服务。我可以帮助您：
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
    
    print("\n\n测试用例2 - 完全重复的段落:")
    print(f"原始长度: {len(test_text2)} 字符")
    cleaned2 = service._remove_duplicate_content(test_text2)
    print(f"清理后长度: {len(cleaned2)} 字符")
    print(f"清理后内容:\n{cleaned2}")
    
    # 测试用例3：混合重复
    test_text3 = """Python是一种高级编程语言。
它具有以下特点：
• 语法简洁
• 易于学习
• 功能强大

Python是一门强大的编程语言。
主要特点包括：
• 简洁的语法
• 容易学习
• 功能丰富

Python广泛应用于各个领域。"""
    
    print("\n\n测试用例3 - 混合重复:")
    print(f"原始长度: {len(test_text3)} 字符")
    cleaned3 = service._remove_duplicate_content(test_text3)
    print(f"清理后长度: {len(cleaned3)} 字符")
    print(f"清理后内容:\n{cleaned3}")

def test_pattern_matching():
    """测试模式匹配重复检测"""
    print("\n\n=== 测试模式匹配重复检测 ===")
    
    service = QCLIService()
    
    # 测试服务描述标准化
    test_descriptions = [
        "• 管理和查询 AWS 资源",
        "• AWS 服务管理和配置",
        "• 代码编写和调试",
        "• 编写和调试代码",
        "• 文件系统操作",
        "• 读写本地文件系统",
    ]
    
    print("服务描述标准化测试:")
    for desc in test_descriptions:
        normalized = service._normalize_service_description(desc)
        print(f"  {desc} -> {normalized}")
    
    # 测试重复帮助提示检测
    test_text = """我可以帮助您处理各种问题。
有什么我可以帮助您的吗？
请问有什么我可以帮助您的吗？
其他内容。"""
    
    print(f"\n重复帮助提示测试:")
    print(f"原始: {repr(test_text)}")
    cleaned = service._remove_pattern_duplicates(test_text)
    print(f"清理后: {repr(cleaned)}")

if __name__ == "__main__":
    test_improved_deduplication()
    test_pattern_matching()