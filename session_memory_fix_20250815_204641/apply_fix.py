#!/usr/bin/env python3
"""
应用会话记忆修复

将修复后的代码应用到实际系统中
"""

import os
import shutil
import sys
from pathlib import Path

def backup_original_files():
    """备份原始文件"""
    print("📦 备份原始文件...")
    
    backup_dir = "session_memory_fix_20250815_204641/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "qcli_api_service/services/qcli_service.py",
        "qcli_api_service/api/controllers.py"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path) + ".backup")
            shutil.copy2(file_path, backup_path)
            print(f"  ✅ 备份: {file_path} -> {backup_path}")
        else:
            print(f"  ⚠️ 文件不存在: {file_path}")

def install_session_process_manager():
    """安装会话进程管理器"""
    print("\n🔧 安装会话进程管理器...")
    
    source_file = "session_memory_fix_20250815_204641/session_process_manager.py"
    target_file = "qcli_api_service/services/session_process_manager.py"
    
    if os.path.exists(source_file):
        shutil.copy2(source_file, target_file)
        print(f"  ✅ 安装: {source_file} -> {target_file}")
    else:
        print(f"  ❌ 源文件不存在: {source_file}")
        return False
    
    return True

def update_qcli_service():
    """更新QCLIService"""
    print("\n🔧 更新QCLIService...")
    
    # 读取修复后的代码
    source_file = "session_memory_fix_20250815_204641/qcli_service_fixed.py"
    target_file = "qcli_api_service/services/qcli_service.py"
    
    if not os.path.exists(source_file):
        print(f"  ❌ 源文件不存在: {source_file}")
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        fixed_content = f.read()
    
    # 移除测试用的导入路径修改
    fixed_content = fixed_content.replace(
        "# 导入新的会话进程管理器\nimport sys\nsys.path.append(os.path.dirname(__file__))\nfrom session_process_manager import session_process_manager",
        "from .session_process_manager import session_process_manager"
    )
    
    # 写入目标文件
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"  ✅ 更新: {target_file}")
    return True

def update_controllers():
    """更新控制器"""
    print("\n🔧 更新控制器...")
    
    source_file = "session_memory_fix_20250815_204641/controllers_fixed.py"
    target_file = "qcli_api_service/api/controllers.py"
    
    if not os.path.exists(source_file):
        print(f"  ❌ 源文件不存在: {source_file}")
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        fixed_content = f.read()
    
    # 移除测试用的导入路径修改，使用正确的相对导入
    fixed_content = fixed_content.replace(
        "# 导入修复后的服务\nimport sys\nsys.path.append(os.path.dirname(__file__))\nfrom qcli_service_fixed import qcli_service",
        "from qcli_api_service.services.qcli_service import qcli_service"
    )
    
    # 只替换需要修复的函数，保留其他函数
    with open(target_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    # 提取修复后的函数
    import re
    
    # 提取stream_chat函数
    stream_chat_match = re.search(r'def stream_chat\(\):.*?(?=\n\ndef|\nclass|\Z)', fixed_content, re.DOTALL)
    if stream_chat_match:
        new_stream_chat = stream_chat_match.group(0)
        
        # 替换原文件中的stream_chat函数
        original_content = re.sub(
            r'def stream_chat\(\):.*?(?=\n\ndef|\nclass|\Z)',
            new_stream_chat,
            original_content,
            flags=re.DOTALL
        )
    
    # 提取chat函数
    chat_match = re.search(r'def chat\(\):.*?(?=\n\ndef|\nclass|\Z)', fixed_content, re.DOTALL)
    if chat_match:
        new_chat = chat_match.group(0)
        
        # 替换原文件中的chat函数
        original_content = re.sub(
            r'def chat\(\):.*?(?=\n\ndef|\nclass|\Z)',
            new_chat,
            original_content,
            flags=re.DOTALL
        )
    
    # 提取delete_session函数
    delete_session_match = re.search(r'def delete_session\(session_id: str\):.*?(?=\n\ndef|\nclass|\Z)', fixed_content, re.DOTALL)
    if delete_session_match:
        new_delete_session = delete_session_match.group(0)
        
        # 替换原文件中的delete_session函数
        original_content = re.sub(
            r'def delete_session\(session_id: str\):.*?(?=\n\ndef|\nclass|\Z)',
            new_delete_session,
            original_content,
            flags=re.DOTALL
        )
    
    # 添加导入语句（如果不存在）
    if "from qcli_api_service.services.qcli_service import qcli_service" not in original_content:
        # 找到其他导入语句的位置
        import_match = re.search(r'(from qcli_api_service\.services\.qcli_service import.*?\n)', original_content)
        if import_match:
            # 替换现有的导入
            original_content = original_content.replace(
                import_match.group(1),
                "from qcli_api_service.services.qcli_service import qcli_service\n"
            )
    
    # 写入更新后的内容
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(original_content)
    
    print(f"  ✅ 更新: {target_file}")
    return True

def create_summary():
    """创建修复总结"""
    print("\n📋 创建修复总结...")
    
    summary_content = """# 🎉 会话记忆修复完成

## 修复内容

### 1. 新增文件
- `qcli_api_service/services/session_process_manager.py` - 会话进程管理器

### 2. 修改文件
- `qcli_api_service/services/qcli_service.py` - 使用持久化会话进程
- `qcli_api_service/api/controllers.py` - 更新聊天接口逻辑

### 3. 备份文件
- `session_memory_fix_20250815_204641/backups/` - 原始文件备份

## 核心改进

### ✅ 会话记忆功能
- 每个API会话对应一个持久的 `q chat --trust-all-tools` 进程
- 不再重复发送历史上下文，让Q Chat自然维护记忆
- 系统上下文保留用于日志记录和调试

### ✅ 进程管理
- 自动启动和清理Q Chat进程
- 会话删除时正确终止对应进程
- 异常处理和进程恢复机制

### ✅ 性能优化
- 避免重复发送大量历史数据
- 减少Q Chat的处理负担
- 提高响应速度和准确性

## 测试建议

1. 重启服务器应用修复
2. 运行 `test_session_memory.py` 验证功能
3. 测试多会话隔离效果
4. 验证会话清理功能

## 回滚方法

如果需要回滚，可以从备份目录恢复原始文件：
```bash
cp session_memory_fix_20250815_204641/backups/*.backup qcli_api_service/services/
cp session_memory_fix_20250815_204641/backups/*.backup qcli_api_service/api/
```
"""
    
    with open("session_memory_fix_20250815_204641/SUMMARY.md", 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print("  ✅ 创建修复总结: session_memory_fix_20250815_204641/SUMMARY.md")

def main():
    """主函数"""
    print("🚀 开始应用会话记忆修复...")
    
    try:
        # 备份原始文件
        backup_original_files()
        
        # 安装新组件
        if not install_session_process_manager():
            print("❌ 安装会话进程管理器失败")
            return False
        
        # 更新现有文件
        if not update_qcli_service():
            print("❌ 更新QCLIService失败")
            return False
        
        if not update_controllers():
            print("❌ 更新控制器失败")
            return False
        
        # 创建总结
        create_summary()
        
        print("\n🎉 修复应用完成！")
        print("\n📋 下一步操作：")
        print("1. 重启服务器: kill <pid> && python app.py")
        print("2. 运行测试: python session_memory_fix_20250815_204641/test_session_memory.py")
        print("3. 验证功能是否正常工作")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 应用修复时发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)