#!/usr/bin/env python3
"""
会话隔离功能演示

演示如何使用会话隔离功能进行多会话并行处理。
"""

import requests
import json
import time
import threading
from typing import List, Dict


class QChatClient:
    """Q Chat API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    def create_session(self) -> str:
        """创建会话"""
        response = requests.post(f"{self.base_url}/api/v1/sessions")
        response.raise_for_status()
        return response.json()["session_id"]
    
    def get_session_info(self, session_id: str) -> Dict:
        """获取会话信息"""
        response = requests.get(f"{self.base_url}/api/v1/sessions/{session_id}")
        response.raise_for_status()
        return response.json()
    
    def get_session_files(self, session_id: str) -> Dict:
        """获取会话文件列表"""
        response = requests.get(f"{self.base_url}/api/v1/sessions/{session_id}/files")
        response.raise_for_status()
        return response.json()
    
    def chat(self, session_id: str, message: str) -> str:
        """发送聊天消息"""
        data = {
            "session_id": session_id,
            "message": message
        }
        response = requests.post(f"{self.base_url}/api/v1/chat", json=data)
        response.raise_for_status()
        return response.json()["message"]
    
    def delete_session(self, session_id: str) -> None:
        """删除会话"""
        response = requests.delete(f"{self.base_url}/api/v1/sessions/{session_id}")
        response.raise_for_status()


def demo_basic_isolation():
    """演示基本的会话隔离功能"""
    print("🔍 演示基本会话隔离功能")
    print("-" * 40)
    
    client = QChatClient()
    
    # 创建会话
    session_id = client.create_session()
    print(f"✅ 创建会话: {session_id}")
    
    # 获取会话信息
    session_info = client.get_session_info(session_id)
    print(f"📁 工作目录: {session_info['work_directory']}")
    
    # 发送消息创建文件
    print("\n💬 请求创建Python脚本...")
    response = client.chat(session_id, "请创建一个简单的Python脚本hello.py，打印'Hello World'")
    print(f"🤖 AI回复: {response[:100]}...")
    
    # 等待文件创建
    time.sleep(2)
    
    # 检查文件列表
    files_info = client.get_session_files(session_id)
    print(f"\n📄 会话文件数量: {files_info['file_count']}")
    if files_info['files']:
        for file_info in files_info['files']:
            print(f"   - {file_info['name']} ({file_info['size']} bytes)")
    
    # 清理会话
    client.delete_session(session_id)
    print(f"\n🗑️ 会话已删除: {session_id}")


def demo_parallel_sessions():
    """演示并行会话处理"""
    print("\n🔍 演示并行会话处理")
    print("-" * 40)
    
    client = QChatClient()
    sessions = []
    
    # 创建多个会话
    for i in range(3):
        session_id = client.create_session()
        sessions.append(session_id)
        print(f"✅ 创建会话 {i+1}: {session_id}")
    
    def process_session(session_id: str, task_name: str):
        """处理单个会话的任务"""
        try:
            print(f"🚀 开始处理 {task_name} (会话: {session_id[:8]}...)")
            
            # 发送不同的任务给不同会话
            if "Python" in task_name:
                message = "请创建一个Python脚本计算斐波那契数列"
            elif "JavaScript" in task_name:
                message = "请创建一个JavaScript函数实现快速排序"
            else:
                message = "请创建一个Shell脚本备份文件"
            
            response = client.chat(session_id, message)
            print(f"✅ {task_name} 完成 (会话: {session_id[:8]}...)")
            
            # 检查生成的文件
            time.sleep(1)
            files_info = client.get_session_files(session_id)
            print(f"📄 {task_name} 生成了 {files_info['file_count']} 个文件")
            
        except Exception as e:
            print(f"❌ {task_name} 处理失败: {e}")
    
    # 并行处理不同任务
    tasks = ["Python任务", "JavaScript任务", "Shell任务"]
    threads = []
    
    for i, (session_id, task_name) in enumerate(zip(sessions, tasks)):
        thread = threading.Thread(
            target=process_session,
            args=(session_id, task_name)
        )
        threads.append(thread)
        thread.start()
    
    # 等待所有任务完成
    for thread in threads:
        thread.join()
    
    print("\n📊 所有会话的最终状态:")
    for i, session_id in enumerate(sessions):
        try:
            session_info = client.get_session_info(session_id)
            files_info = client.get_session_files(session_id)
            print(f"   会话 {i+1}: {files_info['file_count']} 个文件，目录: {session_info['work_directory']}")
        except Exception as e:
            print(f"   会话 {i+1}: 获取信息失败 - {e}")
    
    # 清理所有会话
    print("\n🗑️ 清理所有会话...")
    for session_id in sessions:
        try:
            client.delete_session(session_id)
            print(f"   ✅ 已删除会话: {session_id[:8]}...")
        except Exception as e:
            print(f"   ❌ 删除会话失败: {e}")


def demo_file_management():
    """演示文件管理功能"""
    print("\n🔍 演示文件管理功能")
    print("-" * 40)
    
    client = QChatClient()
    
    # 创建会话
    session_id = client.create_session()
    session_info = client.get_session_info(session_id)
    print(f"✅ 创建会话: {session_id}")
    print(f"📁 工作目录: {session_info['work_directory']}")
    
    # 创建多个文件
    file_tasks = [
        "请创建一个config.json文件，包含应用配置信息",
        "请创建一个README.md文件，说明项目用途",
        "请创建一个requirements.txt文件，列出Python依赖"
    ]
    
    for i, task in enumerate(file_tasks, 1):
        print(f"\n💬 任务 {i}: {task[:30]}...")
        response = client.chat(session_id, task)
        print(f"🤖 任务 {i} 完成")
        time.sleep(1)  # 等待文件创建
    
    # 检查最终文件列表
    print("\n📄 最终文件列表:")
    files_info = client.get_session_files(session_id)
    print(f"   总文件数: {files_info['file_count']}")
    print(f"   工作目录: {files_info['work_directory']}")
    
    if files_info['files']:
        for file_info in files_info['files']:
            size_kb = file_info['size'] / 1024
            print(f"   - {file_info['name']} ({size_kb:.1f} KB)")
    
    # 清理会话
    client.delete_session(session_id)
    print(f"\n🗑️ 会话已删除，文件已清理")


def main():
    """主演示函数"""
    print("🎯 Q Chat 会话隔离功能演示")
    print("=" * 50)
    
    try:
        # 检查服务状态
        response = requests.get("http://localhost:8080/health")
        if response.status_code != 200:
            print("❌ 服务不可用，请确保API服务正在运行")
            return
        
        print("✅ API服务运行正常")
        
        # 运行演示
        demo_basic_isolation()
        demo_parallel_sessions()
        demo_file_management()
        

        
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        print("\n💡 要点总结:")
        print("   - 每个会话都有独立的工作目录")
        print("   - 不同会话的文件操作完全隔离")
        print("   - 可以并行处理多个会话")
        print("   - 会话删除时自动清理文件")
        print("   - 提供API查看会话文件列表")
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到API服务，请确保服务正在运行在 http://localhost:8080")
    except Exception as e:
        print(f"❌ 演示过程中发生错误: {e}")


if __name__ == '__main__':
    main()