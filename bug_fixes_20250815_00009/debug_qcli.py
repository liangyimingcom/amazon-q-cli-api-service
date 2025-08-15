#!/usr/bin/env python3
"""
Q CLI调试脚本

用于直接测试Q CLI调用，分析响应重复问题
"""

import subprocess
import tempfile
import os
import re

def test_qcli_direct():
    """直接测试Q CLI调用"""
    print("=== 直接测试Q CLI调用 ===")
    
    message = "你好"
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(f"请用中文回答以下问题：{message}")
        temp_file.write("\n/quit\n")
        temp_file_path = temp_file.name
    
    try:
        # 调用Q CLI
        with open(temp_file_path, 'r') as input_file:
            process = subprocess.Popen(
                ["q", "chat"],
                stdin=input_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
        
        # 等待完成
        stdout, stderr = process.communicate(timeout=30)
        
        print(f"返回码: {process.returncode}")
        print(f"标准输出长度: {len(stdout)} 字符")
        print(f"标准错误: {stderr}")
        print("\n=== 原始输出 ===")
        print(repr(stdout))
        print("\n=== 格式化输出 ===")
        print(stdout)
        
        # 分析输出
        lines = stdout.split('\n')
        print(f"\n=== 输出分析 ===")
        print(f"总行数: {len(lines)}")
        
        # 检查重复行
        line_counts = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped:
                if stripped in line_counts:
                    line_counts[stripped].append(i)
                else:
                    line_counts[stripped] = [i]
        
        print("\n重复行分析:")
        for line, positions in line_counts.items():
            if len(positions) > 1:
                print(f"重复行 (出现{len(positions)}次): {repr(line)}")
                print(f"  位置: {positions}")
        
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except:
            pass

def test_qcli_cleaning():
    """测试Q CLI输出清理逻辑"""
    print("\n=== 测试输出清理逻辑 ===")
    
    # 模拟一个可能的Q CLI输出
    sample_output = """Welcome to Amazon Q CLI
> 请用中文回答以下问题：你好
你好！我是Amazon Q，很高兴为您服务。我可以帮助您：
• 管理和查询 AWS 资源
• 执行命令行操作
• 读写文件和目录
• 编写和调试代码
• 提供 AWS 最佳实践建议
• 解决技术问题
请问有什么我可以帮助您的吗？
> /quit
"""
    
    print("原始输出:")
    print(repr(sample_output))
    
    # 应用清理逻辑
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    lines = sample_output.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 移除ANSI颜色代码
        cleaned = ansi_escape.sub('', line)
        # 去除首尾空白
        cleaned = cleaned.strip()
        
        # 跳过无效行
        if not cleaned:
            continue
            
        # 跳过命令提示符和退出命令
        skip_patterns = [
            lambda l: l.startswith(">"),
            lambda l: "/quit" in l,
            lambda l: l.startswith("q chat"),
            lambda l: "Welcome to" in l,
            lambda l: "Type /quit" in l,
        ]
        
        if any(pattern(cleaned) for pattern in skip_patterns):
            continue
            
        cleaned_lines.append(cleaned)
    
    result = '\n'.join(cleaned_lines)
    
    print("\n清理后输出:")
    print(repr(result))
    print("\n格式化输出:")
    print(result)

if __name__ == "__main__":
    test_qcli_direct()
    test_qcli_cleaning()