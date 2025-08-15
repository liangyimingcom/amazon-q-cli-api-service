#!/usr/bin/env python3
"""
修复控制器文件中的语法错误
"""

import re

def fix_controller_syntax():
    """修复控制器文件中的f-string语法错误"""
    
    file_path = "qcli_api_service/api/controllers.py"
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复所有的f-string语法错误
    # 模式：yield f"data: ... 后面跟着换行但没有正确闭合
    
    # 修复模式1: yield f"data: {{'type': 'done'}} 后面有换行
    content = re.sub(
        r'yield f"data: \{\{\'type\': \'done\'\}\}\n\n"',
        'yield f"data: {{\'type\': \'done\'}}\\n\\n"',
        content
    )
    
    # 修复模式2: yield f"data: {json.dumps(...)} 后面有换行
    content = re.sub(
        r'yield f"data: \{json\.dumps\(error_data, ensure_ascii=False\)\}\n\n"',
        'yield f"data: {json.dumps(error_data, ensure_ascii=False)}\\n\\n"',
        content
    )
    
    # 更通用的修复：查找所有未正确闭合的f-string
    lines = content.split('\n')
    fixed_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # 检查是否是有问题的yield f"data:行
        if 'yield f"data:' in line and not line.strip().endswith('"'):
            # 这是一个未闭合的f-string，需要修复
            # 收集后续行直到找到闭合
            full_line = line
            i += 1
            while i < len(lines) and not full_line.strip().endswith('"'):
                full_line += '\\n' + lines[i].strip()
                i += 1
            
            # 确保正确闭合
            if not full_line.strip().endswith('"'):
                full_line += '"'
            
            fixed_lines.append(full_line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    # 重新组合内容
    fixed_content = '\n'.join(fixed_lines)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ 修复了控制器文件中的语法错误")

if __name__ == "__main__":
    fix_controller_syntax()