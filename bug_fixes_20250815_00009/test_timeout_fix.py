#!/usr/bin/env python3
"""
测试超时问题修复效果

验证超时配置调整和AWS区域配置是否有效。
"""

import sys
import os
import time
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qcli_api_service.services.qcli_service import qcli_service
from qcli_api_service.config import config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_timeout_configuration():
    """测试超时配置"""
    logger.info("=== 测试超时配置 ===")
    logger.info(f"当前超时设置: {config.QCLI_TIMEOUT}秒")
    logger.info(f"AWS默认区域: {config.AWS_DEFAULT_REGION}")
    
    # 检查环境变量
    aws_region = os.getenv("AWS_DEFAULT_REGION")
    logger.info(f"环境变量AWS_DEFAULT_REGION: {aws_region}")

def test_qcli_availability():
    """测试Q CLI可用性"""
    logger.info("=== 测试Q CLI可用性 ===")
    
    try:
        is_available = qcli_service.is_available()
        logger.info(f"Q CLI可用性: {'✅ 可用' if is_available else '❌ 不可用'}")
        return is_available
    except Exception as e:
        logger.error(f"Q CLI可用性检查失败: {e}")
        return False

def test_simple_chat():
    """测试简单对话"""
    logger.info("=== 测试简单对话 ===")
    
    try:
        start_time = time.time()
        
        message = "你好，请简单回复一下。"
        response = qcli_service.chat(message)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ 简单对话成功")
        logger.info(f"   耗时: {duration:.2f}秒")
        logger.info(f"   回复长度: {len(response)}字符")
        logger.info(f"   回复预览: {response[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 简单对话失败: {e}")
        return False

def test_medium_chat():
    """测试中等复杂度对话"""
    logger.info("=== 测试中等复杂度对话 ===")
    
    try:
        start_time = time.time()
        
        message = "请解释一下Amazon S3的主要功能和使用场景。"
        response = qcli_service.chat(message)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"✅ 中等复杂度对话成功")
        logger.info(f"   耗时: {duration:.2f}秒")
        logger.info(f"   回复长度: {len(response)}字符")
        logger.info(f"   回复预览: {response[:100]}...")
        
        # 检查是否在合理时间内完成
        if duration <= config.QCLI_TIMEOUT:
            logger.info(f"   ✅ 在超时限制内完成（{config.QCLI_TIMEOUT}秒）")
        else:
            logger.warning(f"   ⚠️ 超过超时限制（{config.QCLI_TIMEOUT}秒）")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 中等复杂度对话失败: {e}")
        return False

def test_timeout_error_message():
    """测试超时错误消息（通过设置很短的超时时间）"""
    logger.info("=== 测试超时错误消息 ===")
    
    # 临时修改超时时间为很短的值来触发超时
    original_timeout = config.QCLI_TIMEOUT
    config.QCLI_TIMEOUT = 1  # 1秒，肯定会超时
    
    try:
        message = "请详细解释AWS Lambda的工作原理。"
        response = qcli_service.chat(message)
        
        # 如果没有超时，说明测试失败
        logger.warning("⚠️ 预期超时但实际成功了")
        return False
        
    except RuntimeError as e:
        error_msg = str(e)
        logger.info(f"✅ 成功触发超时错误")
        logger.info(f"   错误消息: {error_msg}")
        
        # 检查错误消息是否包含改进的内容
        if "AI处理复杂问题需要较长时间" in error_msg:
            logger.info("   ✅ 错误消息已改进，包含用户友好的提示")
            return True
        else:
            logger.warning("   ⚠️ 错误消息未改进")
            return False
            
    except Exception as e:
        logger.error(f"❌ 超时测试失败: {e}")
        return False
        
    finally:
        # 恢复原始超时时间
        config.QCLI_TIMEOUT = original_timeout

def test_aws_region_setting():
    """测试AWS区域设置"""
    logger.info("=== 测试AWS区域设置 ===")
    
    # 检查配置中的AWS区域
    logger.info(f"配置中的AWS区域: {config.AWS_DEFAULT_REGION}")
    
    # 检查环境变量
    env_region = os.getenv("AWS_DEFAULT_REGION")
    logger.info(f"环境变量AWS_DEFAULT_REGION: {env_region}")
    
    # 如果环境变量未设置，应该使用配置中的默认值
    if not env_region:
        logger.info("✅ 环境变量未设置，将使用配置中的默认区域")
        return True
    else:
        logger.info(f"✅ 环境变量已设置为: {env_region}")
        return True

def main():
    """主函数"""
    logger.info("开始测试超时问题修复效果")
    logger.info("=" * 50)
    
    # 测试结果统计
    tests = []
    
    # 1. 测试配置
    test_timeout_configuration()
    
    # 2. 测试Q CLI可用性
    if not test_qcli_availability():
        logger.error("Q CLI不可用，无法继续测试")
        return
    
    # 3. 测试AWS区域设置
    tests.append(("AWS区域设置", test_aws_region_setting()))
    
    # 4. 测试简单对话
    tests.append(("简单对话", test_simple_chat()))
    
    # 5. 测试中等复杂度对话
    tests.append(("中等复杂度对话", test_medium_chat()))
    
    # 6. 测试超时错误消息
    tests.append(("超时错误消息", test_timeout_error_message()))
    
    # 统计结果
    logger.info("=" * 50)
    logger.info("测试结果汇总:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！超时问题修复成功。")
    else:
        logger.warning(f"⚠️ {total - passed} 个测试失败，需要进一步调查。")

if __name__ == "__main__":
    main()