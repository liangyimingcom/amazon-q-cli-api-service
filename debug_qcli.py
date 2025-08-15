#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Q CLI问题的测试脚本
"""

import os
import subprocess
import tempfile
import json

def test_qcli_direct():
    """直接测试Q CLI"""
    print("=== 直接测试Q CLI ===")
    try:
        # 测试基本功能
        result = subprocess.run(
            ["q", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(f"Q CLI版本: {result.stdout.strip()}")
        
        # 测试聊天功能
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("你好，请介绍一下自己\n/quit\n")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'r') as input_file:
                process = subprocess.Popen(
                    ["q", "chat"],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True
                )
            
            stdout, stderr = process.communicate(timeout=30)
            
            print(f"返回码: {process.returncode}")
            print(f"标准输出长度: {len(stdout)} 字符")
            print(f"错误输出: {stderr}")
            
            # 清理输出
            lines = stdout.split('\n')
            cleaned_lines = []
            for line in lines:
                # 移除ANSI颜色代码
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                cleaned = ansi_escape.sub('', line).strip()
                
                # 跳过无效行
                if (cleaned and 
                    not cleaned.startswith(">") and 
                    "/quit" not in cleaned and 
                    not cleaned.startswith("q chat") and 
                    "Welcome to" not in cleaned and 
                    "Type /quit" not in cleaned):
                    cleaned_lines.append(cleaned)
            
            cleaned_output = '\n'.join(cleaned_lines)
            print(f"清理后输出长度: {len(cleaned_output)} 字符")
            print(f"清理后输出前200字符: {cleaned_output[:200]}")
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"测试失败: {e}")

def test_qcli_in_session_dir():
    """在session目录中测试Q CLI"""
    print("\n=== 在session目录中测试Q CLI ===")
    
    # 创建测试session目录
    session_dir = "sessions/test-session"
    os.makedirs(session_dir, exist_ok=True)
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("你好，请介绍一下自己，然后保存结果到test.md\n/quit\n")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'r') as input_file:
                process = subprocess.Popen(
                    ["q", "chat"],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True,
                    cwd=session_dir  # 在session目录中运行
                )
            
            stdout, stderr = process.communicate(timeout=30)
            
            print(f"在session目录中运行:")
            print(f"工作目录: {os.path.abspath(session_dir)}")
            print(f"返回码: {process.returncode}")
            print(f"标准输出长度: {len(stdout)} 字符")
            print(f"错误输出: {stderr}")
            
            # 检查是否创建了文件
            test_file = os.path.join(session_dir, "test.md")
            if os.path.exists(test_file):
                print(f"✓ 文件已创建: {test_file}")
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"文件内容长度: {len(content)} 字符")
            else:
                print("✗ 文件未创建")
                # 列出目录内容
                files = os.listdir(session_dir)
                print(f"目录内容: {files}")
            
        finally:
            os.unlink(temp_file_path)
            
    except Exception as e:
        print(f"测试失败: {e}")

def test_api_call():
    """测试API调用"""
    print("\n=== 测试API调用 ===")
    
    try:
        # 创建会话
        result = subprocess.run([
            "curl", "-s", "-X", "POST", "http://localhost:8080/api/v1/sessions"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            session_data = json.loads(result.stdout)
            session_id = session_data['session_id']
            print(f"创建会话成功: {session_id}")
            
            # 发送消息
            result = subprocess.run([
                "curl", "-s", "-X", "POST", "http://localhost:8080/api/v1/chat",
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "session_id": session_id,
                    "message": "你好，请介绍一下自己，然后保存结果到debug.md"
                })
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                response_data = json.loads(result.stdout)
                print(f"API调用成功")
                print(f"响应消息长度: {len(response_data.get('message', ''))} 字符")
                print(f"响应消息前200字符: {response_data.get('message', '')[:200]}")
                
                # 检查session目录
                session_dir = f"sessions/{session_id}"
                if os.path.exists(session_dir):
                    files = os.listdir(session_dir)
                    print(f"Session目录文件: {files}")
                    
                    debug_file = os.path.join(session_dir, "debug.md")
                    if os.path.exists(debug_file):
                        print(f"✓ debug.md文件已创建")
                    else:
                        print("✗ debug.md文件未创建")
                else:
                    print("✗ Session目录不存在")
            else:
                print(f"API调用失败: {result.stderr}")
        else:
            print(f"创建会话失败: {result.stderr}")
            
    except Exception as e:
        print(f"API测试失败: {e}")

if __name__ == "__main__":
    test_qcli_direct()
    test_qcli_in_session_dir()
    test_api_call()