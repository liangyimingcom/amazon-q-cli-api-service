#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复Q CLI配置的脚本
"""

import os
import subprocess
import json

def setup_qcli_trust():
    """设置Q CLI自动信任工具"""
    print("=== 设置Q CLI自动信任工具 ===")
    
    try:
        # 运行 /tools trust 命令
        result = subprocess.run([
            "q", "chat", "--non-interactive"
        ], input="/tools trust\n/quit\n", text=True, capture_output=True)
        
        print(f"设置信任工具返回码: {result.returncode}")
        print(f"输出: {result.stdout}")
        if result.stderr:
            print(f"错误: {result.stderr}")
            
    except Exception as e:
        print(f"设置失败: {e}")

def check_qcli_config():
    """检查Q CLI配置"""
    print("\n=== 检查Q CLI配置 ===")
    
    # 查找Q CLI配置文件
    config_paths = [
        os.path.expanduser("~/.config/q/config.json"),
        os.path.expanduser("~/.q/config.json"),
        os.path.expanduser("~/Library/Application Support/q/config.json"),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            print(f"找到配置文件: {config_path}")
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    print(f"配置内容: {json.dumps(config, indent=2, ensure_ascii=False)}")
            except Exception as e:
                print(f"读取配置失败: {e}")
            break
    else:
        print("未找到Q CLI配置文件")

def test_with_trust():
    """测试带信任的Q CLI调用"""
    print("\n=== 测试带信任的Q CLI调用 ===")
    
    session_dir = "sessions/test-trust"
    os.makedirs(session_dir, exist_ok=True)
    
    try:
        # 尝试使用 --trust-all 参数（如果支持）
        result = subprocess.run([
            "q", "chat"
        ], input="你好，请介绍一下自己，然后保存结果到trust-test.md\n/quit\n", 
        text=True, capture_output=True, cwd=session_dir)
        
        print(f"返回码: {result.returncode}")
        print(f"输出长度: {len(result.stdout)} 字符")
        
        # 检查文件是否创建
        test_file = os.path.join(session_dir, "trust-test.md")
        if os.path.exists(test_file):
            print(f"✓ 文件已创建: {test_file}")
        else:
            print("✗ 文件未创建")
            files = os.listdir(session_dir)
            print(f"目录内容: {files}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    check_qcli_config()
    setup_qcli_trust()
    test_with_trust()