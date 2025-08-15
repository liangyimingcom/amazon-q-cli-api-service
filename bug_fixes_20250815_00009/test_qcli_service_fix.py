#!/usr/bin/env python3
"""
直接测试Q CLI服务的修复效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qcli_api_service.services.qcli_service import qcli_service

def test_qcli_service_fix():
    """测试Q CLI服务的修复效果"""
    print("=== 测试Q CLI服务修复效果 ===")
    
    try:
        # 直接调用Q CLI服务
        response = qcli_service.chat("你好", "", None)
        print(f"响应长度: {len(response)} 字符")
        print(f"响应内容:\n{response}")
        
        # 检查是否还有重复
        lines = response.split('\n')
        print(f"\n响应行数: {len(lines)}")
        
        # 检查重复行
        line_counts = {}
        for line in lines:
            line = line.strip()
            if line:
                line_counts[line] = line_counts.get(line, 0) + 1
        
        print("\n重复行检查:")
        has_duplicates = False
        for line, count in line_counts.items():
            if count > 1:
                print(f"  重复{count}次: {repr(line)}")
                has_duplicates = True
        
        if not has_duplicates:
            print("  没有发现重复行")
        
        # 检查帮助提示重复
        help_count = response.count("我可以帮助")
        print(f"\n'我可以帮助'出现次数: {help_count}")
        
        question_count = response.count("什么我可以帮助您的吗")
        print(f"'什么我可以帮助您的吗'出现次数: {question_count}")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_qcli_service_fix()