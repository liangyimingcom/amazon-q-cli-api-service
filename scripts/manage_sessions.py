#!/usr/bin/env python3
"""
会话管理脚本

用于管理和维护会话目录的命令行工具。
"""

import sys
import os
import argparse
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qcli_api_service.utils.session_directory_manager import session_directory_manager


def list_sessions():
    """列出所有会话目录"""
    directories = session_directory_manager.list_session_directories()
    
    if not directories:
        print("没有找到会话目录")
        return
    
    print(f"找到 {len(directories)} 个会话目录:")
    print("-" * 80)
    
    for dir_info in directories:
        created_time = datetime.fromtimestamp(dir_info["created_time"]).strftime("%Y-%m-%d %H:%M:%S")
        modified_time = datetime.fromtimestamp(dir_info["modified_time"]).strftime("%Y-%m-%d %H:%M:%S")
        size_mb = dir_info["size_bytes"] / (1024 * 1024)
        
        print(f"会话ID: {dir_info['session_id']}")
        print(f"路径: {dir_info['relative_path']}")
        print(f"创建时间: {created_time}")
        print(f"修改时间: {modified_time}")
        print(f"文件数量: {dir_info['file_count']}")
        print(f"大小: {size_mb:.2f} MB")
        print("-" * 80)


def show_session_details(session_id: str):
    """显示指定会话的详细信息"""
    info = session_directory_manager.get_directory_info(session_id)
    
    if not info:
        print(f"会话 {session_id} 不存在")
        return
    
    created_time = datetime.fromtimestamp(info["created_time"]).strftime("%Y-%m-%d %H:%M:%S")
    modified_time = datetime.fromtimestamp(info["modified_time"]).strftime("%Y-%m-%d %H:%M:%S")
    size_mb = info["size_bytes"] / (1024 * 1024)
    
    print(f"会话详细信息:")
    print(f"会话ID: {info['session_id']}")
    print(f"路径: {info['relative_path']}")
    print(f"绝对路径: {info['path']}")
    print(f"创建时间: {created_time}")
    print(f"修改时间: {modified_time}")
    print(f"文件数量: {info['file_count']}")
    print(f"大小: {size_mb:.2f} MB")
    
    if info["files"]:
        print("\n文件列表:")
        print("-" * 60)
        for file_info in info["files"]:
            file_created = datetime.fromtimestamp(file_info["created_time"]).strftime("%Y-%m-%d %H:%M:%S")
            file_size_kb = file_info["size"] / 1024
            print(f"  {file_info['path']} ({file_size_kb:.1f} KB, {file_created})")


def cleanup_empty():
    """清理空目录"""
    print("正在清理空的会话目录...")
    cleaned_count = session_directory_manager.cleanup_empty_directories()
    print(f"已清理 {cleaned_count} 个空目录")


def cleanup_old(hours: int):
    """清理过期目录"""
    print(f"正在清理超过 {hours} 小时的会话目录...")
    cleaned_count = session_directory_manager.cleanup_old_directories(hours)
    print(f"已清理 {cleaned_count} 个过期目录")


def export_session_info(output_file: str):
    """导出会话信息到JSON文件"""
    directories = session_directory_manager.list_session_directories()
    
    # 转换时间戳为可读格式
    for dir_info in directories:
        dir_info["created_time_str"] = datetime.fromtimestamp(dir_info["created_time"]).isoformat()
        dir_info["modified_time_str"] = datetime.fromtimestamp(dir_info["modified_time"]).isoformat()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(directories, f, ensure_ascii=False, indent=2)
    
    print(f"会话信息已导出到: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="会话管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出会话
    subparsers.add_parser('list', help='列出所有会话目录')
    
    # 显示会话详情
    detail_parser = subparsers.add_parser('detail', help='显示指定会话的详细信息')
    detail_parser.add_argument('session_id', help='会话ID')
    
    # 清理空目录
    subparsers.add_parser('cleanup-empty', help='清理空的会话目录')
    
    # 清理过期目录
    cleanup_old_parser = subparsers.add_parser('cleanup-old', help='清理过期的会话目录')
    cleanup_old_parser.add_argument('--hours', type=int, default=24, help='过期时间（小时，默认24）')
    
    # 导出信息
    export_parser = subparsers.add_parser('export', help='导出会话信息到JSON文件')
    export_parser.add_argument('output_file', help='输出文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_sessions()
        elif args.command == 'detail':
            show_session_details(args.session_id)
        elif args.command == 'cleanup-empty':
            cleanup_empty()
        elif args.command == 'cleanup-old':
            cleanup_old(args.hours)
        elif args.command == 'export':
            export_session_info(args.output_file)
    except Exception as e:
        print(f"执行命令时出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()