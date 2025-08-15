#!/usr/bin/env python3
"""
Amazon Q CLI API服务 - 综合测试脚本

按照测试矩阵执行全面的系统测试，记录所有结果用于后续修复。
"""

import json
import time
import requests
import threading
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple
import os

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = "http://localhost:8080"
TEST_TIMEOUT = 60
RESULTS_DIR = "test_results_20250815_114958"

class TestResult:
    """测试结果记录类"""
    def __init__(self, test_name: str, category: str):
        self.test_name = test_name
        self.category = category
        self.start_time = None
        self.end_time = None
        self.status = "PENDING"  # PENDING, PASS, FAIL, ERROR
        self.expected = None
        self.actual = None
        self.error_message = None
        self.response_data = None
        self.performance_data = {}
        
    def start(self):
        self.start_time = time.time()
        self.status = "RUNNING"
        
    def finish(self, status: str, expected=None, actual=None, error_message=None, response_data=None):
        self.end_time = time.time()
        self.status = status
        self.expected = expected
        self.actual = actual
        self.error_message = error_message
        self.response_data = response_data
        
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0
        
    def to_dict(self) -> Dict:
        return {
            "test_name": self.test_name,
            "category": self.category,
            "status": self.status,
            "duration": self.duration(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "expected": self.expected,
            "actual": self.actual,
            "error_message": self.error_message,
            "response_data": self.response_data,
            "performance_data": self.performance_data
        }

class ComprehensiveTestSuite:
    """综合测试套件"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.session_id = None
        
    def add_result(self, result: TestResult):
        self.results.append(result)
        
    def run_all_tests(self):
        """执行所有测试"""
        logger.info("开始执行综合测试套件")
        logger.info("=" * 60)
        
        # 1. 环境准备
        if not self.check_server_availability():
            logger.error("服务器不可用，测试终止")
            return
            
        # 2. 基础功能测试
        self.test_basic_functionality()
        
        # 3. 聊天功能测试
        self.test_chat_functionality()
        
        # 4. 会话管理测试
        self.test_session_management()
        
        # 5. 错误处理测试
        self.test_error_handling()
        
        # 6. 性能测试
        self.test_performance()
        
        # 7. 边界测试
        self.test_boundary_conditions()
        
        # 8. 内容质量测试
        self.test_content_quality()
        
        # 9. 生成测试报告
        self.generate_test_report()
        
    def check_server_availability(self) -> bool:
        """检查服务器可用性"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def test_basic_functionality(self):
        """基础功能测试"""
        logger.info("执行基础功能测试...")
        
        # 测试健康检查
        result = TestResult("健康检查", "基础功能")
        result.start()
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            result.finish(
                "PASS" if response.status_code == 200 else "FAIL",
                expected="200状态码和服务状态信息",
                actual=f"状态码: {response.status_code}, 响应: {response.text[:200]}",
                response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            )
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
        # 测试根路径
        result = TestResult("根路径访问", "基础功能")
        result.start()
        try:
            response = requests.get(f"{BASE_URL}/", timeout=10)
            result.finish(
                "PASS" if response.status_code == 200 else "FAIL",
                expected="200状态码和服务信息",
                actual=f"状态码: {response.status_code}, 响应: {response.text[:200]}",
                response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            )
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
    def test_chat_functionality(self):
        """聊天功能测试"""
        logger.info("执行聊天功能测试...")
        
        # 测试标准聊天
        result = TestResult("标准聊天", "聊天功能")
        result.start()
        try:
            payload = {"message": "你好，这是一个测试消息"}
            response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                has_session_id = "session_id" in data
                has_message = "message" in data and len(data["message"]) > 0
                has_timestamp = "timestamp" in data
                
                if has_session_id and has_message and has_timestamp:
                    result.finish("PASS", 
                                expected="200状态码，包含session_id、message、timestamp",
                                actual=f"状态码: {response.status_code}, 字段完整: {has_session_id and has_message and has_timestamp}",
                                response_data=data)
                    # 保存会话ID用于后续测试
                    self.session_id = data.get("session_id")
                else:
                    result.finish("FAIL",
                                expected="完整的响应字段",
                                actual=f"缺少字段: session_id={has_session_id}, message={has_message}, timestamp={has_timestamp}",
                                response_data=data)
            else:
                result.finish("FAIL",
                            expected="200状态码",
                            actual=f"状态码: {response.status_code}",
                            response_data=response.text)
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
        # 测试流式聊天
        result = TestResult("流式聊天", "聊天功能")
        result.start()
        try:
            payload = {"message": "请简单介绍一下AWS Lambda"}
            response = requests.post(f"{BASE_URL}/api/v1/chat/stream", json=payload, timeout=TEST_TIMEOUT, stream=True)
            
            if response.status_code == 200:
                chunks = []
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            chunks.append(line_str[6:])  # 移除 'data: ' 前缀
                            if len(chunks) >= 5:  # 收集前5个数据块就够了
                                break
                
                if len(chunks) > 0:
                    result.finish("PASS",
                                expected="SSE流式响应",
                                actual=f"收到 {len(chunks)} 个数据块",
                                response_data={"chunks": chunks[:3]})  # 只保存前3个块
                else:
                    result.finish("FAIL",
                                expected="SSE流式响应",
                                actual="未收到数据块",
                                response_data={"raw_response": response.text[:500]})
            else:
                result.finish("FAIL",
                            expected="200状态码",
                            actual=f"状态码: {response.status_code}",
                            response_data=response.text)
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
        # 测试带会话的聊天
        if self.session_id:
            result = TestResult("带会话聊天", "聊天功能")
            result.start()
            try:
                payload = {"message": "请记住我刚才说的话", "session_id": self.session_id}
                response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, timeout=TEST_TIMEOUT)
                
                result.finish(
                    "PASS" if response.status_code == 200 else "FAIL",
                    expected="200状态码，上下文相关回复",
                    actual=f"状态码: {response.status_code}",
                    response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
            except Exception as e:
                result.finish("ERROR", error_message=str(e))
            self.add_result(result)
            
    def test_session_management(self):
        """会话管理测试"""
        logger.info("执行会话管理测试...")
        
        # 测试创建会话
        result = TestResult("创建会话", "会话管理")
        result.start()
        try:
            response = requests.post(f"{BASE_URL}/api/v1/sessions", timeout=10)
            
            if response.status_code == 201:
                data = response.json()
                if "session_id" in data and "created_at" in data:
                    result.finish("PASS",
                                expected="201状态码，包含session_id和created_at",
                                actual=f"状态码: {response.status_code}, 字段完整",
                                response_data=data)
                    test_session_id = data["session_id"]
                else:
                    result.finish("FAIL",
                                expected="完整的会话信息",
                                actual="缺少必要字段",
                                response_data=data)
                    test_session_id = None
            else:
                result.finish("FAIL",
                            expected="201状态码",
                            actual=f"状态码: {response.status_code}",
                            response_data=response.text)
                test_session_id = None
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
            test_session_id = None
        self.add_result(result)
        
        # 测试获取会话（使用刚创建的会话）
        if test_session_id:
            result = TestResult("获取会话", "会话管理")
            result.start()
            try:
                response = requests.get(f"{BASE_URL}/api/v1/sessions/{test_session_id}", timeout=10)
                result.finish(
                    "PASS" if response.status_code == 200 else "FAIL",
                    expected="200状态码，会话详细信息",
                    actual=f"状态码: {response.status_code}",
                    response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
            except Exception as e:
                result.finish("ERROR", error_message=str(e))
            self.add_result(result)
            
            # 测试获取会话文件
            result = TestResult("获取会话文件", "会话管理")
            result.start()
            try:
                response = requests.get(f"{BASE_URL}/api/v1/sessions/{test_session_id}/files", timeout=10)
                result.finish(
                    "PASS" if response.status_code == 200 else "FAIL",
                    expected="200状态码，文件列表",
                    actual=f"状态码: {response.status_code}",
                    response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
            except Exception as e:
                result.finish("ERROR", error_message=str(e))
            self.add_result(result)
            
            # 测试删除会话
            result = TestResult("删除会话", "会话管理")
            result.start()
            try:
                response = requests.delete(f"{BASE_URL}/api/v1/sessions/{test_session_id}", timeout=10)
                result.finish(
                    "PASS" if response.status_code == 200 else "FAIL",
                    expected="200状态码，删除确认",
                    actual=f"状态码: {response.status_code}",
                    response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
            except Exception as e:
                result.finish("ERROR", error_message=str(e))
            self.add_result(result)
            
    def test_error_handling(self):
        """错误处理测试"""
        logger.info("执行错误处理测试...")
        
        error_test_cases = [
            {
                "name": "空请求体",
                "method": "POST",
                "url": f"{BASE_URL}/api/v1/chat",
                "data": None,
                "expected_status": 400,
                "expected_fields": ["error", "code", "suggestions"]
            },
            {
                "name": "无效JSON",
                "method": "POST", 
                "url": f"{BASE_URL}/api/v1/chat",
                "data": "invalid json",
                "headers": {"Content-Type": "application/json"},
                "expected_status": 400,
                "expected_fields": ["error", "code", "suggestions"]
            },
            {
                "name": "缺少消息字段",
                "method": "POST",
                "url": f"{BASE_URL}/api/v1/chat",
                "data": {"session_id": "test"},
                "expected_status": 400,
                "expected_fields": ["error", "code", "suggestions"]
            },
            {
                "name": "不存在的会话",
                "method": "GET",
                "url": f"{BASE_URL}/api/v1/sessions/nonexistent-session-id",
                "expected_status": 404,
                "expected_fields": ["error", "code", "suggestions"]
            },
            {
                "name": "不存在的接口",
                "method": "GET",
                "url": f"{BASE_URL}/api/v1/nonexistent",
                "expected_status": 404,
                "expected_fields": ["error", "code", "suggestions"]
            },
            {
                "name": "方法不允许",
                "method": "GET",
                "url": f"{BASE_URL}/api/v1/chat",
                "expected_status": 405,
                "expected_fields": ["error", "code", "suggestions"]
            }
        ]
        
        for test_case in error_test_cases:
            result = TestResult(test_case["name"], "错误处理")
            result.start()
            
            try:
                if test_case["method"] == "POST":
                    if test_case.get("data") is None:
                        response = requests.post(test_case["url"], timeout=10)
                    elif isinstance(test_case["data"], str):
                        response = requests.post(
                            test_case["url"],
                            data=test_case["data"],
                            headers=test_case.get("headers", {}),
                            timeout=10
                        )
                    else:
                        response = requests.post(test_case["url"], json=test_case["data"], timeout=10)
                elif test_case["method"] == "GET":
                    response = requests.get(test_case["url"], timeout=10)
                elif test_case["method"] == "DELETE":
                    response = requests.delete(test_case["url"], timeout=10)
                
                # 检查状态码
                status_ok = response.status_code == test_case["expected_status"]
                
                # 检查响应格式
                try:
                    data = response.json()
                    fields_ok = all(field in data for field in test_case["expected_fields"])
                    suggestions_ok = len(data.get("suggestions", [])) > 0
                except:
                    data = {"raw_response": response.text}
                    fields_ok = False
                    suggestions_ok = False
                
                if status_ok and fields_ok and suggestions_ok:
                    result.finish("PASS",
                                expected=f"状态码{test_case['expected_status']}，包含{test_case['expected_fields']}和建议",
                                actual=f"状态码: {response.status_code}, 字段完整: {fields_ok}, 有建议: {suggestions_ok}",
                                response_data=data)
                else:
                    result.finish("FAIL",
                                expected=f"状态码{test_case['expected_status']}，完整错误信息",
                                actual=f"状态码: {response.status_code}, 字段完整: {fields_ok}, 有建议: {suggestions_ok}",
                                response_data=data)
                    
            except Exception as e:
                result.finish("ERROR", error_message=str(e))
                
            self.add_result(result)
            
    def test_performance(self):
        """性能测试"""
        logger.info("执行性能测试...")
        
        # 测试响应时间
        result = TestResult("响应时间测试", "性能测试")
        result.start()
        try:
            start_time = time.time()
            payload = {"message": "什么是AWS?"}
            response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, timeout=TEST_TIMEOUT)
            end_time = time.time()
            
            duration = end_time - start_time
            result.performance_data["response_time"] = duration
            
            if response.status_code == 200 and duration < 30:  # 30秒内完成
                result.finish("PASS",
                            expected="< 30秒响应时间",
                            actual=f"响应时间: {duration:.2f}秒",
                            response_data={"duration": duration, "status_code": response.status_code})
            else:
                result.finish("FAIL",
                            expected="< 30秒响应时间",
                            actual=f"响应时间: {duration:.2f}秒, 状态码: {response.status_code}",
                            response_data={"duration": duration, "status_code": response.status_code})
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
        # 测试进度提示
        result = TestResult("进度提示测试", "性能测试")
        result.start()
        try:
            payload = {"message": "请详细解释AWS Lambda"}
            response = requests.post(f"{BASE_URL}/api/v1/chat/stream", json=payload, timeout=5, stream=True)
            
            first_chunk_time = None
            chunk_count = 0
            
            for line in response.iter_lines():
                if line:
                    if first_chunk_time is None:
                        first_chunk_time = time.time() - result.start_time
                    chunk_count += 1
                    if chunk_count >= 3:  # 收到3个块就够了
                        break
            
            if first_chunk_time and first_chunk_time < 2.0:  # 2秒内首个响应
                result.finish("PASS",
                            expected="< 2秒首个响应",
                            actual=f"首个响应时间: {first_chunk_time:.2f}秒",
                            response_data={"first_chunk_time": first_chunk_time, "chunk_count": chunk_count})
            else:
                result.finish("FAIL",
                            expected="< 2秒首个响应",
                            actual=f"首个响应时间: {first_chunk_time}秒" if first_chunk_time else "无响应",
                            response_data={"first_chunk_time": first_chunk_time, "chunk_count": chunk_count})
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
    def test_boundary_conditions(self):
        """边界条件测试"""
        logger.info("执行边界条件测试...")
        
        boundary_test_cases = [
            {
                "name": "空消息",
                "payload": {"message": ""},
                "expected_status": 400
            },
            {
                "name": "超长消息",
                "payload": {"message": "x" * 5000},
                "expected_status": 400
            },
            {
                "name": "特殊字符",
                "payload": {"message": "<script>alert('test')</script>"},
                "expected_status": 200  # 应该正常处理或安全拒绝
            },
            {
                "name": "无效会话ID格式",
                "payload": {"message": "test", "session_id": "invalid-format"},
                "expected_status": 400
            }
        ]
        
        for test_case in boundary_test_cases:
            result = TestResult(test_case["name"], "边界测试")
            result.start()
            
            try:
                response = requests.post(f"{BASE_URL}/api/v1/chat", json=test_case["payload"], timeout=30)
                
                status_match = response.status_code == test_case["expected_status"]
                
                result.finish(
                    "PASS" if status_match else "FAIL",
                    expected=f"状态码 {test_case['expected_status']}",
                    actual=f"状态码: {response.status_code}",
                    response_data=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                )
            except Exception as e:
                result.finish("ERROR", error_message=str(e))
                
            self.add_result(result)
            
    def test_content_quality(self):
        """内容质量测试"""
        logger.info("执行内容质量测试...")
        
        # 测试重复内容检测
        result = TestResult("重复内容检测", "内容质量")
        result.start()
        try:
            payload = {"message": "你好，请介绍一下你自己"}
            response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                # 简单检测重复：查找重复的句子或段落
                sentences = message.split('。')
                unique_sentences = set(s.strip() for s in sentences if s.strip())
                
                has_duplicates = len(sentences) > len(unique_sentences) + 2  # 允许少量重复
                
                result.finish(
                    "FAIL" if has_duplicates else "PASS",
                    expected="无明显重复内容",
                    actual=f"句子总数: {len(sentences)}, 唯一句子: {len(unique_sentences)}, 有重复: {has_duplicates}",
                    response_data={"message_length": len(message), "sentences": len(sentences), "unique_sentences": len(unique_sentences)}
                )
            else:
                result.finish("ERROR", error_message=f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
        # 测试内容完整性
        result = TestResult("内容完整性检测", "内容质量")
        result.start()
        try:
            payload = {"message": "请解释什么是云计算"}
            response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                # 检查内容完整性：不应该以不完整的句子开头
                starts_incomplete = message.startswith(('的', '。', '，', '、'))
                has_reasonable_length = len(message) > 50
                
                result.finish(
                    "FAIL" if starts_incomplete or not has_reasonable_length else "PASS",
                    expected="完整的回复内容",
                    actual=f"开头完整: {not starts_incomplete}, 长度合理: {has_reasonable_length}, 长度: {len(message)}",
                    response_data={"message_length": len(message), "starts_incomplete": starts_incomplete, "message_preview": message[:100]}
                )
            else:
                result.finish("ERROR", error_message=f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
        # 测试中文支持
        result = TestResult("中文支持测试", "内容质量")
        result.start()
        try:
            payload = {"message": "请用中文回答：什么是人工智能？"}
            response = requests.post(f"{BASE_URL}/api/v1/chat", json=payload, timeout=TEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                # 检查中文字符比例
                chinese_chars = sum(1 for char in message if '\u4e00' <= char <= '\u9fff')
                total_chars = len(message)
                chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
                
                result.finish(
                    "PASS" if chinese_ratio > 0.3 else "FAIL",  # 至少30%中文字符
                    expected="主要使用中文回复",
                    actual=f"中文字符比例: {chinese_ratio:.2%}, 总字符数: {total_chars}",
                    response_data={"chinese_ratio": chinese_ratio, "total_chars": total_chars, "chinese_chars": chinese_chars}
                )
            else:
                result.finish("ERROR", error_message=f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            result.finish("ERROR", error_message=str(e))
        self.add_result(result)
        
    def generate_test_report(self):
        """生成测试报告"""
        logger.info("生成测试报告...")
        
        # 统计结果
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        
        # 按类别统计
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"total": 0, "pass": 0, "fail": 0, "error": 0}
            categories[result.category]["total"] += 1
            if result.status == "PASS":
                categories[result.category]["pass"] += 1
            elif result.status == "FAIL":
                categories[result.category]["fail"] += 1
            elif result.status == "ERROR":
                categories[result.category]["error"] += 1
        
        # 生成Markdown报告
        report_content = f"""# 系统测试报告

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**测试环境**: {BASE_URL}  
**总测试数**: {total_tests}  
**通过**: {passed_tests} | **失败**: {failed_tests} | **错误**: {error_tests}  
**通过率**: {(passed_tests/total_tests*100):.1f}%

## 测试结果汇总

| 类别 | 总数 | 通过 | 失败 | 错误 | 通过率 |
|------|------|------|------|------|--------|
"""
        
        for category, stats in categories.items():
            pass_rate = (stats["pass"] / stats["total"] * 100) if stats["total"] > 0 else 0
            report_content += f"| {category} | {stats['total']} | {stats['pass']} | {stats['fail']} | {stats['error']} | {pass_rate:.1f}% |\n"
        
        report_content += "\n## 详细测试结果\n\n"
        
        for result in self.results:
            status_emoji = {"PASS": "✅", "FAIL": "❌", "ERROR": "💥"}.get(result.status, "⏳")
            report_content += f"### {status_emoji} {result.test_name} ({result.category})\n\n"
            report_content += f"- **状态**: {result.status}\n"
            report_content += f"- **耗时**: {result.duration():.2f}秒\n"
            
            if result.expected:
                report_content += f"- **预期**: {result.expected}\n"
            if result.actual:
                report_content += f"- **实际**: {result.actual}\n"
            if result.error_message:
                report_content += f"- **错误**: {result.error_message}\n"
            
            report_content += "\n"
        
        # 问题汇总
        failed_results = [r for r in self.results if r.status in ["FAIL", "ERROR"]]
        if failed_results:
            report_content += "## 问题汇总\n\n"
            
            # 按优先级分类问题
            p0_issues = []  # 核心功能不可用
            p1_issues = []  # 功能异常
            p2_issues = []  # 体验问题
            
            for result in failed_results:
                issue = {
                    "name": result.test_name,
                    "category": result.category,
                    "status": result.status,
                    "error": result.error_message or result.actual
                }
                
                # 简单的优先级分类逻辑
                if result.category in ["基础功能", "聊天功能"] and result.status == "ERROR":
                    p0_issues.append(issue)
                elif result.category in ["聊天功能", "会话管理"] and result.status == "FAIL":
                    p1_issues.append(issue)
                else:
                    p2_issues.append(issue)
            
            if p0_issues:
                report_content += "### 🔴 P0 严重问题（核心功能不可用）\n\n"
                for issue in p0_issues:
                    report_content += f"- **{issue['name']}** ({issue['category']}): {issue['error']}\n"
                report_content += "\n"
            
            if p1_issues:
                report_content += "### 🟡 P1 重要问题（功能异常）\n\n"
                for issue in p1_issues:
                    report_content += f"- **{issue['name']}** ({issue['category']}): {issue['error']}\n"
                report_content += "\n"
            
            if p2_issues:
                report_content += "### 🟢 P2 一般问题（体验问题）\n\n"
                for issue in p2_issues:
                    report_content += f"- **{issue['name']}** ({issue['category']}): {issue['error']}\n"
                report_content += "\n"
        
        # 修复建议
        if failed_results:
            report_content += "## 修复建议\n\n"
            report_content += "基于测试结果，建议按以下优先级进行修复：\n\n"
            report_content += "1. **立即修复P0问题** - 影响核心功能，需要立即处理\n"
            report_content += "2. **优先修复P1问题** - 影响用户体验，需要尽快处理\n"
            report_content += "3. **计划修复P2问题** - 优化体验，可以安排在后续版本\n\n"
        
        # 保存报告
        with open(f"{RESULTS_DIR}/test_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        
        # 保存详细的JSON数据
        detailed_results = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "pass_rate": passed_tests/total_tests*100 if total_tests > 0 else 0,
                "test_time": datetime.now().isoformat(),
                "categories": categories
            },
            "results": [result.to_dict() for result in self.results]
        }
        
        with open(f"{RESULTS_DIR}/detailed_results.json", "w", encoding="utf-8") as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"测试报告已生成: {RESULTS_DIR}/test_report.md")
        logger.info(f"详细结果已保存: {RESULTS_DIR}/detailed_results.json")
        logger.info(f"测试完成 - 通过: {passed_tests}/{total_tests} ({(passed_tests/total_tests*100):.1f}%)")

def main():
    """主函数"""
    # 确保结果目录存在
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # 创建测试套件并执行
    test_suite = ComprehensiveTestSuite()
    test_suite.run_all_tests()

if __name__ == "__main__":
    main()