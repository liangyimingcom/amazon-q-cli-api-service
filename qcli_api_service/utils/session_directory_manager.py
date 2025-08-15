"""
会话目录管理工具

提供会话目录的管理和维护功能。
"""

import os
import shutil
import logging
from typing import List, Dict, Optional
from qcli_api_service.config import config

logger = logging.getLogger(__name__)


class SessionDirectoryManager:
    """会话目录管理器"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or config.SESSIONS_BASE_DIR
        os.makedirs(self.base_dir, exist_ok=True)
    
    def list_session_directories(self) -> List[Dict[str, any]]:
        """列出所有会话目录"""
        directories = []
        
        if not os.path.exists(self.base_dir):
            return directories
        
        for item in os.listdir(self.base_dir):
            item_path = os.path.join(self.base_dir, item)
            if os.path.isdir(item_path):
                try:
                    stat = os.stat(item_path)
                    file_count = self._count_files_in_directory(item_path)
                    
                    directories.append({
                        "session_id": item,
                        "path": item_path,
                        "relative_path": os.path.relpath(item_path),
                        "created_time": stat.st_ctime,
                        "modified_time": stat.st_mtime,
                        "file_count": file_count,
                        "size_bytes": self._get_directory_size(item_path)
                    })
                except Exception as e:
                    logger.warning(f"无法获取目录信息 {item_path}: {e}")
        
        return directories
    
    def cleanup_empty_directories(self) -> int:
        """清理空的会话目录"""
        cleaned_count = 0
        
        for dir_info in self.list_session_directories():
            if dir_info["file_count"] == 0:
                try:
                    shutil.rmtree(dir_info["path"])
                    cleaned_count += 1
                    logger.info(f"清理空目录: {dir_info['path']}")
                except Exception as e:
                    logger.error(f"清理目录失败 {dir_info['path']}: {e}")
        
        return cleaned_count
    
    def cleanup_old_directories(self, max_age_hours: int = 24) -> int:
        """清理超过指定时间的目录"""
        import time
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for dir_info in self.list_session_directories():
            age_seconds = current_time - dir_info["modified_time"]
            if age_seconds > max_age_seconds:
                try:
                    shutil.rmtree(dir_info["path"])
                    cleaned_count += 1
                    logger.info(f"清理过期目录: {dir_info['path']} (年龄: {age_seconds/3600:.1f}小时)")
                except Exception as e:
                    logger.error(f"清理目录失败 {dir_info['path']}: {e}")
        
        return cleaned_count
    
    def get_directory_info(self, session_id: str) -> Optional[Dict[str, any]]:
        """获取指定会话目录的详细信息"""
        session_path = os.path.join(self.base_dir, session_id)
        
        if not os.path.exists(session_path) or not os.path.isdir(session_path):
            return None
        
        try:
            stat = os.stat(session_path)
            files = self._list_files_in_directory(session_path)
            
            return {
                "session_id": session_id,
                "path": session_path,
                "relative_path": os.path.relpath(session_path),
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "file_count": len(files),
                "size_bytes": self._get_directory_size(session_path),
                "files": files
            }
        except Exception as e:
            logger.error(f"获取目录信息失败 {session_path}: {e}")
            return None
    
    def _count_files_in_directory(self, directory: str) -> int:
        """计算目录中的文件数量"""
        count = 0
        try:
            for root, dirs, files in os.walk(directory):
                count += len(files)
        except Exception:
            pass
        return count
    
    def _get_directory_size(self, directory: str) -> int:
        """计算目录大小（字节）"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                    except Exception:
                        pass
        except Exception:
            pass
        return total_size
    
    def _list_files_in_directory(self, directory: str) -> List[Dict[str, any]]:
        """列出目录中的所有文件"""
        files = []
        try:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    relative_path = os.path.relpath(file_path, directory)
                    
                    try:
                        stat = os.stat(file_path)
                        files.append({
                            "name": filename,
                            "path": relative_path,
                            "absolute_path": file_path,
                            "size": stat.st_size,
                            "created_time": stat.st_ctime,
                            "modified_time": stat.st_mtime
                        })
                    except Exception as e:
                        logger.warning(f"无法获取文件信息 {file_path}: {e}")
        except Exception as e:
            logger.error(f"列出目录文件失败 {directory}: {e}")
        
        return files


# 全局会话目录管理器实例
session_directory_manager = SessionDirectoryManager()