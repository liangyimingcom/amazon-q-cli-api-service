#!/usr/bin/env python3
"""
测试响应时间优化效果

验证进度提示和性能优化是否有效。
"""

import sys
import os
import time
import logging
from typing import List

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from qcli_api_service.services.qcli_service import qcli_service

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_progress_indicators():
    """测试进度提示功能"""
    logger.info("=== 测试进度提示功能 ===")
    
    try:
        message = "请简单介绍一下AWS Lambda。"
        
        logger.info("开始流式对话，观察进度提示...")
        start_time = time.time()
        
        chunks = []
        chunk_times = []
        
        for i, chunk in enumerate(qcli_service.stream_chat(message)):
            current_time = time.time()
            elapsed = current_time - start_time
            
            chunks.append(chunk)
            chunk_times.append(elapsed)
            
            logger.info(f"收到第{i+1}个数据块 (耗时: {elapsed:.2f}秒): {chunk[:50]}...")
            
            # 如果是前几个块，检查是否包含进度提示
            if i < 3:
                if "正在处理" in chunk or "正在思考" in chunk or "🤖" in chunk or "🔄" in chunk:
                    logger.info(f"  ✅ 检测到进度提示")
        
        total_time = time.time() - start_time
        logger.info(f"✅ 流式对话完成，总耗时: {total_time:.2f}秒")
        logger.info(f"   总共收到 {len(chunks)} 个数据块")
        logger.info(f"   首个数据块耗时: {chunk_times[0]:.2f}秒")
        
        # 检查是否有进度提示
        has_progress = any("正在处理" in chunk or "正在思考" in chunk for chunk in chunks[:3])
        if has_progress:
            logger.info("   ✅ 进度提示功能正常")
            return True
        else:
            logger.warning("   ⚠️ 未检测到进度提示")
            return False
            
    except Exception as e:
        logger.error(f"❌ 进度提示测试失败: {e}")
        return False

def test_output_processing_performance():
    """测试输出处理性能"""
    logger.info("=== 测试输出处理性能 ===")
    
    # 创建测试用的重复内容
    test_content = """
    我可以帮助您：
    • 管理和查询 AWS 资源
    • 执行命令行操作
    • 读写文件和目录
    • 编写和调试代码
    • 提供 AWS 最佳实践建议
    • 解决技术问题
    
    请问有什么我可以帮助您的吗？
    
    我可以帮助您：
    • 管理和查询 AWS 资源
    • 执行命令行操作
    • 读写文件和目录
    • 编写和调试代码
    • 提供 AWS 最佳实践建议
    • 解决技术问题
    
    请问有什么我可以帮助您的吗？
    """
    
    try:
        # 测试优化后的清理性能
        start_time = time.time()
        
        cleaned_content = qcli_service._remove_duplicate_content(test_content)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        logger.info(f"✅ 输出处理完成")
        logger.info(f"   处理时间: {processing_time:.4f}秒")
        logger.info(f"   原始长度: {len(test_content)} 字符")
        logger.info(f"   清理后长度: {len(cleaned_content)} 字符")
        logger.info(f"   压缩率: {(1 - len(cleaned_content)/len(test_content))*100:.1f}%")
        
        # 检查是否正确去除了重复内容
        lines = cleaned_content.split('\n')
        help_lines = [line for line in lines if "我可以帮助您" in line]
        
        if len(help_lines) <= 1:
            logger.info("   ✅ 重复内容已正确移除")
            return True
        else:
            logger.warning(f"   ⚠️ 仍有 {len(help_lines)} 行重复内容")
            return False
            
    except Exception as e:
        logger.error(f"❌ 输出处理性能测试失败: {e}")
        return False

def benchmark_response_times():
    """基准测试响应时间"""
    logger.info("=== 基准测试响应时间 ===")
    
    test_cases = [
        ("简单问候", "你好"),
        ("短问题", "什么是AWS?"),
        ("中等问题", "请解释一下Amazon S3的主要功能。")
    ]
    
    results = []
    
    for test_name, message in test_cases:
        logger.info(f"--- 测试: {test_name} ---")
        
        try:
            start_time = time.time()
            
            # 使用非流式方法进行基准测试
            response = qcli_service.chat(message)
            
            end_time = time.time()
            duration = end_time - start_time
            
            results.append({
                'test_name': test_name,
                'duration': duration,
                'response_length': len(response),
                'success': True
            })
            
            logger.info(f"✅ {test_name} 完成")
            logger.info(f"   耗时: {duration:.2f}秒")
            logger.info(f"   回复长度: {len(response)} 字符")
            logger.info(f"   处理速度: {len(response)/duration:.1f} 字符/秒")
            
        except Exception as e:
            logger.error(f"❌ {test_name} 失败: {e}")
            results.append({
                'test_name': test_name,
                'duration': 0,
                'response_length': 0,
                'success': False
            })
    
    # 分析结果
    logger.info("=== 性能分析 ===")
    successful_tests = [r for r in results if r['success']]
    
    if successful_tests:
        avg_duration = sum(r['duration'] for r in successful_tests) / len(successful_tests)
        avg_speed = sum(r['response_length']/r['duration'] for r in successful_tests) / len(successful_tests)
        
        logger.info(f"平均响应时间: {avg_duration:.2f}秒")
        logger.info(f"平均处理速度: {avg_speed:.1f} 字符/秒")
        
        # 与之前的基线比较
        baseline_times = {
            "简单问候": 9.7,
            "短问题": 11.3,
            "中等问题": 18.3
        }
        
        for result in successful_tests:
            test_name = result['test_name']
            if test_name in baseline_times:
                baseline = baseline_times[test_name]
                current = result['duration']
                improvement = (baseline - current) / baseline * 100
                
                if improvement > 0:
                    logger.info(f"{test_name}: 性能提升 {improvement:.1f}%")
                else:
                    logger.info(f"{test_name}: 性能下降 {abs(improvement):.1f}%")
    
    return results

def test_streaming_experience():
    """测试流式体验"""
    logger.info("=== 测试流式体验 ===")
    
    try:
        message = "请详细解释AWS Lambda的工作原理。"
        
        logger.info("测试流式响应的用户体验...")
        start_time = time.time()
        
        first_chunk_time = None
        meaningful_content_time = None
        chunks_received = 0
        
        for chunk in qcli_service.stream_chat(message):
            current_time = time.time()
            elapsed = current_time - start_time
            chunks_received += 1
            
            if first_chunk_time is None:
                first_chunk_time = elapsed
                logger.info(f"首个数据块耗时: {elapsed:.2f}秒")
            
            # 检测到有意义的内容（非进度提示）
            if (meaningful_content_time is None and 
                "正在处理" not in chunk and "正在思考" not in chunk and 
                len(chunk.strip()) > 20):
                meaningful_content_time = elapsed
                logger.info(f"首个有意义内容耗时: {elapsed:.2f}秒")
            
            if chunks_received <= 5:  # 只显示前5个块的详情
                logger.info(f"数据块 {chunks_received} ({elapsed:.2f}s): {chunk[:30]}...")
        
        total_time = time.time() - start_time
        
        logger.info(f"✅ 流式响应完成")
        logger.info(f"   总耗时: {total_time:.2f}秒")
        logger.info(f"   首个数据块: {first_chunk_time:.2f}秒")
        logger.info(f"   首个有意义内容: {meaningful_content_time:.2f}秒")
        logger.info(f"   总数据块数: {chunks_received}")
        
        # 评估用户体验
        if first_chunk_time and first_chunk_time < 1.0:
            logger.info("   ✅ 响应及时，用户体验良好")
            return True
        else:
            logger.warning("   ⚠️ 首个响应较慢，用户体验一般")
            return False
            
    except Exception as e:
        logger.error(f"❌ 流式体验测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("开始测试响应时间优化效果")
    logger.info("=" * 50)
    
    # 测试结果统计
    tests = []
    
    # 1. 测试进度提示
    tests.append(("进度提示功能", test_progress_indicators()))
    
    # 2. 测试输出处理性能
    tests.append(("输出处理性能", test_output_processing_performance()))
    
    # 3. 基准测试响应时间
    benchmark_results = benchmark_response_times()
    benchmark_success = all(r['success'] for r in benchmark_results)
    tests.append(("响应时间基准测试", benchmark_success))
    
    # 4. 测试流式体验
    tests.append(("流式体验", test_streaming_experience()))
    
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
        logger.info("🎉 所有测试通过！响应时间优化成功。")
    else:
        logger.warning(f"⚠️ {total - passed} 个测试失败，需要进一步优化。")

if __name__ == "__main__":
    main()