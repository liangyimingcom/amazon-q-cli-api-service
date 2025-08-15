#!/usr/bin/env python3
"""
详细调试Q CLI输出

分析Q CLI的原始输出，找出重复的真正原因
"""

import subprocess
import tempfile
import os
import re

def debug_qcli_output():
    """详细调试Q CLI输出"""
    print("=== 详细调试Q CLI输出 ===")
    
    message = "请用中文回答以下问题：你好"
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        temp_file.write(message)
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
        
        # 逐行分析输出
        lines = stdout.split('\n')
        print(f"\n=== 逐行分析 (共{len(lines)}行) ===")
        
        content_lines = []
        for i, line in enumerate(lines):
            # 移除ANSI颜色代码
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            cleaned = ansi_escape.sub('', line).strip()
            
            print(f"行{i:2d}: {repr(line)}")
            if cleaned:
                print(f"     清理后: {repr(cleaned)}")
                
                # 检查是否应该跳过
                skip_patterns = [
                    lambda l: l.startswith(">"),
                    lambda l: "/quit" in l,
                    lambda l: l.startswith("q chat"),
                    lambda l: "Welcome to" in l,
                    lambda l: "Type /quit" in l,
                ]
                
                should_skip = any(pattern(cleaned) for pattern in skip_patterns)
                if not should_skip:
                    content_lines.append(cleaned)
                    print(f"     -> 保留内容")
                else:
                    print(f"     -> 跳过")
            print()
        
        print(f"=== 最终内容行 (共{len(content_lines)}行) ===")
        for i, line in enumerate(content_lines):
            print(f"{i}: {line}")
        
        final_content = '\n'.join(content_lines)
        print(f"\n=== 最终拼接内容 ===")
        print(f"长度: {len(final_content)} 字符")
        print(f"内容:\n{final_content}")
        
        # 检查是否有重复模式
        print(f"\n=== 重复模式分析 ===")
        
        # 检查相同行
        line_counts = {}
        for line in content_lines:
            if line in line_counts:
                line_counts[line] += 1
            else:
                line_counts[line] = 1
        
        print("重复行统计:")
        for line, count in line_counts.items():
            if count > 1:
                print(f"  重复{count}次: {repr(line)}")
        
        # 检查相似内容
        print("\n相似内容分析:")
        for i, line1 in enumerate(content_lines):
            for j, line2 in enumerate(content_lines[i+1:], i+1):
                if line1 != line2:
                    # 计算相似度（简单的包含关系检查）
                    if len(line1) > 10 and len(line2) > 10:
                        if line1 in line2 or line2 in line1:
                            print(f"  相似行 {i} 和 {j}:")
                            print(f"    {repr(line1)}")
                            print(f"    {repr(line2)}")
        
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_file_path)
        except:
            pass

if __name__ == "__main__":
    debug_qcli_output()