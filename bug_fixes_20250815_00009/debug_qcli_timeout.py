#!/usr/bin/env python3
"""
Q CLI超时问题诊断脚本

用于分析Q CLI调用超时的根本原因。
"""

import os
import sys
import time
import subprocess
import tempfile
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_qcli_availability():
    """检查Q CLI是否可用"""
    logger.info("=== 检查Q CLI可用性 ===")
    
    try:
        start_time = time.time()
        result = subprocess.run(
            ["q", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        end_time = time.time()
        
        logger.info(f"Q CLI版本检查耗时: {end_time - start_time:.2f}秒")
        logger.info(f"返回码: {result.returncode}")
        logger.info(f"输出: {result.stdout.strip()}")
        
        if result.stderr:
            logger.warning(f"错误输出: {result.stderr.strip()}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logger.error("Q CLI版本检查超时（10秒）")
        return False
    except FileNotFoundError:
        logger.error("Q CLI命令未找到，请确认已正确安装")
        return False
    except Exception as e:
        logger.error(f"Q CLI版本检查失败: {e}")
        return False

def test_simple_qcli_call():
    """测试简单的Q CLI调用"""
    logger.info("=== 测试简单Q CLI调用 ===")
    
    try:
        # 创建简单的输入
        test_message = "你好，请简单回复一下。"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_message)
            temp_file.write("\n/quit\n")
            temp_file_path = temp_file.name
        
        try:
            start_time = time.time()
            
            with open(temp_file_path, 'r') as input_file:
                process = subprocess.Popen(
                    ["q", "chat"],
                    stdin=input_file,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    universal_newlines=True
                )
            
            # 设置不同的超时时间进行测试
            timeout_values = [10, 30, 60]
            
            for timeout in timeout_values:
                logger.info(f"尝试{timeout}秒超时...")
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    end_time = time.time()
                    
                    logger.info(f"Q CLI调用成功，耗时: {end_time - start_time:.2f}秒")
                    logger.info(f"返回码: {process.returncode}")
                    logger.info(f"输出长度: {len(stdout)} 字符")
                    
                    if stderr:
                        logger.warning(f"错误输出: {stderr[:200]}...")
                    
                    # 显示输出的前200个字符
                    if stdout:
                        logger.info(f"输出预览: {stdout[:200]}...")
                    
                    return True
                    
                except subprocess.TimeoutExpired:
                    logger.warning(f"{timeout}秒超时")
                    if timeout == timeout_values[-1]:  # 最后一次尝试
                        process.kill()
                        logger.error("所有超时尝试都失败，终止进程")
                        return False
                    continue
                    
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
    except Exception as e:
        logger.error(f"简单Q CLI调用测试失败: {e}")
        return False

def test_network_connectivity():
    """测试网络连接性"""
    logger.info("=== 测试网络连接性 ===")
    
    # 测试基本网络连接
    test_hosts = [
        "8.8.8.8",  # Google DNS
        "1.1.1.1",  # Cloudflare DNS
        "amazon.com",  # Amazon
        "aws.amazon.com"  # AWS
    ]
    
    for host in test_hosts:
        try:
            start_time = time.time()
            result = subprocess.run(
                ["ping", "-c", "3", host],
                capture_output=True,
                text=True,
                timeout=10
            )
            end_time = time.time()
            
            if result.returncode == 0:
                logger.info(f"✅ {host} 连接正常，耗时: {end_time - start_time:.2f}秒")
            else:
                logger.warning(f"❌ {host} 连接失败")
                
        except subprocess.TimeoutExpired:
            logger.warning(f"⏰ {host} ping超时")
        except Exception as e:
            logger.error(f"❌ {host} 测试失败: {e}")

def check_system_resources():
    """检查系统资源"""
    logger.info("=== 检查系统资源 ===")
    
    try:
        # 检查内存使用
        result = subprocess.run(
            ["free", "-h"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("内存使用情况:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
    except:
        logger.warning("无法获取内存信息")
    
    try:
        # 检查磁盘使用
        result = subprocess.run(
            ["df", "-h", "."],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("磁盘使用情况:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
    except:
        logger.warning("无法获取磁盘信息")

def check_environment_variables():
    """检查环境变量"""
    logger.info("=== 检查环境变量 ===")
    
    # 检查AWS相关环境变量
    aws_vars = [
        "AWS_PROFILE",
        "AWS_REGION", 
        "AWS_DEFAULT_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN"
    ]
    
    for var in aws_vars:
        value = os.getenv(var)
        if value:
            # 隐藏敏感信息
            if "KEY" in var or "TOKEN" in var:
                logger.info(f"{var}: ***隐藏***")
            else:
                logger.info(f"{var}: {value}")
        else:
            logger.info(f"{var}: 未设置")

def test_qcli_with_different_inputs():
    """测试不同输入的Q CLI调用"""
    logger.info("=== 测试不同输入的Q CLI调用 ===")
    
    test_cases = [
        ("简单问候", "你好"),
        ("短问题", "什么是AWS?"),
        ("中等问题", "请解释一下Amazon S3的主要功能和使用场景。"),
        ("长问题", "请详细解释AWS Lambda的工作原理，包括其优势、限制、定价模型，以及在什么情况下应该使用Lambda而不是EC2。同时，请提供一些最佳实践建议。")
    ]
    
    for test_name, message in test_cases:
        logger.info(f"--- 测试: {test_name} ---")
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(f"请用中文回答：{message}")
                temp_file.write("\n/quit\n")
                temp_file_path = temp_file.name
            
            try:
                start_time = time.time()
                
                with open(temp_file_path, 'r') as input_file:
                    process = subprocess.Popen(
                        ["q", "chat"],
                        stdin=input_file,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        universal_newlines=True
                    )
                
                try:
                    stdout, stderr = process.communicate(timeout=45)  # 45秒超时
                    end_time = time.time()
                    
                    logger.info(f"✅ {test_name} 成功，耗时: {end_time - start_time:.2f}秒")
                    logger.info(f"   输出长度: {len(stdout)} 字符")
                    
                    if stderr:
                        logger.warning(f"   错误输出: {stderr[:100]}...")
                        
                except subprocess.TimeoutExpired:
                    process.kill()
                    logger.error(f"❌ {test_name} 超时（45秒）")
                    
            finally:
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"❌ {test_name} 测试失败: {e}")

def main():
    """主函数"""
    logger.info("开始Q CLI超时问题诊断")
    logger.info(f"诊断时间: {datetime.now()}")
    logger.info("=" * 50)
    
    # 1. 检查Q CLI可用性
    if not check_qcli_availability():
        logger.error("Q CLI不可用，无法继续诊断")
        return
    
    # 2. 检查网络连接
    test_network_connectivity()
    
    # 3. 检查系统资源
    check_system_resources()
    
    # 4. 检查环境变量
    check_environment_variables()
    
    # 5. 测试简单调用
    if not test_simple_qcli_call():
        logger.error("简单Q CLI调用失败")
        return
    
    # 6. 测试不同输入
    test_qcli_with_different_inputs()
    
    logger.info("=" * 50)
    logger.info("Q CLI超时问题诊断完成")

if __name__ == "__main__":
    main()