#!/usr/bin/env python3
"""
Amazon Q CLI API服务 - 完整测试套件执行脚本

该脚本用于执行所有测试矩阵中定义的测试用例，生成详细的测试报告。
"""

import os
import sys
import time
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import requests

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """测试执行器"""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.results = {
            "start_time": None,
            "end_time": None,
            "total_duration": 0,
            "test_suites": {},
            "summary": {
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "success_rate": 0
            }
        }
    
    def check_service_health(self):
        """检查服务健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ 服务健康检查通过")
                print(f"   状态: {health_data.get('status', 'unknown')}")
                print(f"   Q CLI可用: {health_data.get('qcli_available', 'unknown')}")
                print(f"   活跃会话: {health_data.get('active_sessions', 'unknown')}")
                return True
            else:
                print(f"❌ 服务健康检查失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到服务: {e}")
            return False
    
    def run_test_suite(self, suite_name, test_file):
        """运行单个测试套件"""
        print(f"\n🧪 运行测试套件: {suite_name}")
        print(f"   测试文件: {test_file}")
        
        start_time = time.time()
        
        try:
            # 使用pytest运行测试
            cmd = [
                "python", "-m", "pytest", 
                str(test_file),
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file=test_matrix/reports/{suite_name}_report.json"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=project_root
            )
            
            duration = time.time() - start_time
            
            # 解析测试结果
            report_file = project_root / f"test_matrix/reports/{suite_name}_report.json"
            if report_file.exists():
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                suite_result = {
                    "duration": duration,
                    "total": report_data.get("summary", {}).get("total", 0),
                    "passed": report_data.get("summary", {}).get("passed", 0),
                    "failed": report_data.get("summary", {}).get("failed", 0),
                    "skipped": report_data.get("summary", {}).get("skipped", 0),
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                # 如果没有JSON报告，从返回码推断结果
                suite_result = {
                    "duration": duration,
                    "total": 1,
                    "passed": 1 if result.returncode == 0 else 0,
                    "failed": 0 if result.returncode == 0 else 1,
                    "skipped": 0,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            self.results["test_suites"][suite_name] = suite_result
            
            # 打印结果摘要
            if suite_result["return_code"] == 0:
                print(f"   ✅ 通过: {suite_result['passed']}/{suite_result['total']} 测试")
            else:
                print(f"   ❌ 失败: {suite_result['failed']}/{suite_result['total']} 测试")
            
            print(f"   ⏱️  耗时: {duration:.2f}秒")
            
            return suite_result["return_code"] == 0
            
        except Exception as e:
            print(f"   ❌ 测试套件执行异常: {e}")
            self.results["test_suites"][suite_name] = {
                "duration": time.time() - start_time,
                "total": 0,
                "passed": 0,
                "failed": 1,
                "skipped": 0,
                "return_code": -1,
                "error": str(e)
            }
            return False
    
    def run_all_tests(self, test_categories=None):
        """运行所有测试"""
        print("🚀 开始执行Amazon Q CLI API服务完整测试套件")
        print(f"   服务地址: {self.base_url}")
        print(f"   开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.results["start_time"] = datetime.now().isoformat()
        
        # 检查服务健康状态
        if not self.check_service_health():
            print("❌ 服务不可用，终止测试")
            return False
        
        # 定义测试套件
        test_suites = {
            "功能测试": "test_matrix/scripts/functional_test.py",
            "API接口测试": "test_matrix/scripts/api_test_suite.py",
            "会话管理测试": "test_matrix/scripts/session_management_test.py",
            "流式处理测试": "test_matrix/scripts/streaming_test.py",
            "会话隔离测试": "test_matrix/scripts/session_isolation_test.py",
            "性能测试": "test_matrix/scripts/performance_test.py",
            "安全测试": "test_matrix/scripts/security_test.py",
            "集成测试": "test_matrix/scripts/integration_test.py"
        }
        
        # 如果指定了测试类别，只运行指定的测试
        if test_categories:
            test_suites = {k: v for k, v in test_suites.items() if k in test_categories}
        
        # 确保报告目录存在
        reports_dir = project_root / "test_matrix/reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 运行每个测试套件
        all_passed = True
        for suite_name, test_file in test_suites.items():
            test_file_path = project_root / test_file
            
            if test_file_path.exists():
                success = self.run_test_suite(suite_name, test_file_path)
                if not success:
                    all_passed = False
            else:
                print(f"⚠️  测试文件不存在: {test_file}")
                self.results["test_suites"][suite_name] = {
                    "duration": 0,
                    "total": 0,
                    "passed": 0,
                    "failed": 1,
                    "skipped": 0,
                    "return_code": -1,
                    "error": "测试文件不存在"
                }
                all_passed = False
        
        # 计算总体结果
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = sum(
            suite.get("duration", 0) for suite in self.results["test_suites"].values()
        )
        
        # 计算汇总统计
        for suite_result in self.results["test_suites"].values():
            self.results["summary"]["total_tests"] += suite_result.get("total", 0)
            self.results["summary"]["passed"] += suite_result.get("passed", 0)
            self.results["summary"]["failed"] += suite_result.get("failed", 0)
            self.results["summary"]["skipped"] += suite_result.get("skipped", 0)
        
        if self.results["summary"]["total_tests"] > 0:
            self.results["summary"]["success_rate"] = (
                self.results["summary"]["passed"] / self.results["summary"]["total_tests"] * 100
            )
        
        # 生成测试报告
        self.generate_report()
        
        return all_passed
    
    def generate_report(self):
        """生成测试报告"""
        print("\n📊 测试结果汇总")
        print("=" * 60)
        
        # 打印总体统计
        summary = self.results["summary"]
        print(f"总测试数: {summary['total_tests']}")
        print(f"通过: {summary['passed']} ✅")
        print(f"失败: {summary['failed']} ❌")
        print(f"跳过: {summary['skipped']} ⏭️")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"总耗时: {self.results['total_duration']:.2f}秒")
        
        # 打印各测试套件结果
        print("\n📋 各测试套件详情")
        print("-" * 60)
        
        for suite_name, suite_result in self.results["test_suites"].items():
            status = "✅" if suite_result.get("return_code") == 0 else "❌"
            duration = suite_result.get("duration", 0)
            passed = suite_result.get("passed", 0)
            total = suite_result.get("total", 0)
            
            print(f"{status} {suite_name:<20} {passed:>3}/{total:<3} ({duration:>6.2f}s)")
        
        # 保存详细报告到文件
        report_file = project_root / "test_matrix/reports/test_results.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        # 生成Markdown报告
        self.generate_markdown_report()
        
        print(f"\n📄 详细报告已保存到: {report_file}")
    
    def generate_markdown_report(self):
        """生成Markdown格式的测试报告"""
        report_file = project_root / "test_matrix/reports/test_results.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Amazon Q CLI API服务 - 测试结果报告\n\n")
            
            # 基本信息
            f.write("## 测试概览\n\n")
            f.write(f"- **开始时间**: {self.results['start_time']}\n")
            f.write(f"- **结束时间**: {self.results['end_time']}\n")
            f.write(f"- **总耗时**: {self.results['total_duration']:.2f}秒\n")
            f.write(f"- **服务地址**: {self.base_url}\n\n")
            
            # 总体统计
            summary = self.results["summary"]
            f.write("## 测试统计\n\n")
            f.write("| 指标 | 数量 | 百分比 |\n")
            f.write("|------|------|--------|\n")
            f.write(f"| 总测试数 | {summary['total_tests']} | 100% |\n")
            f.write(f"| 通过 | {summary['passed']} | {summary['passed']/max(summary['total_tests'],1)*100:.1f}% |\n")
            f.write(f"| 失败 | {summary['failed']} | {summary['failed']/max(summary['total_tests'],1)*100:.1f}% |\n")
            f.write(f"| 跳过 | {summary['skipped']} | {summary['skipped']/max(summary['total_tests'],1)*100:.1f}% |\n\n")
            
            # 各测试套件详情
            f.write("## 测试套件详情\n\n")
            f.write("| 测试套件 | 状态 | 通过/总数 | 耗时(秒) | 成功率 |\n")
            f.write("|----------|------|-----------|----------|--------|\n")
            
            for suite_name, suite_result in self.results["test_suites"].items():
                status = "✅ 通过" if suite_result.get("return_code") == 0 else "❌ 失败"
                passed = suite_result.get("passed", 0)
                total = suite_result.get("total", 0)
                duration = suite_result.get("duration", 0)
                success_rate = (passed / max(total, 1)) * 100
                
                f.write(f"| {suite_name} | {status} | {passed}/{total} | {duration:.2f} | {success_rate:.1f}% |\n")
            
            # 失败的测试详情
            failed_suites = [
                (name, result) for name, result in self.results["test_suites"].items()
                if result.get("failed", 0) > 0 or result.get("return_code") != 0
            ]
            
            if failed_suites:
                f.write("\n## 失败测试详情\n\n")
                for suite_name, suite_result in failed_suites:
                    f.write(f"### {suite_name}\n\n")
                    if "error" in suite_result:
                        f.write(f"**错误**: {suite_result['error']}\n\n")
                    if suite_result.get("stderr"):
                        f.write("**错误输出**:\n```\n")
                        f.write(suite_result["stderr"])
                        f.write("\n```\n\n")
        
        print(f"📄 Markdown报告已保存到: {report_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Amazon Q CLI API服务完整测试套件")
    parser.add_argument(
        "--base-url", 
        default="http://localhost:8080",
        help="服务基础URL (默认: http://localhost:8080)"
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        help="指定要运行的测试类别"
    )
    parser.add_argument(
        "--list-categories",
        action="store_true",
        help="列出所有可用的测试类别"
    )
    
    args = parser.parse_args()
    
    if args.list_categories:
        print("可用的测试类别:")
        categories = [
            "功能测试", "API接口测试", "会话管理测试", "流式处理测试",
            "会话隔离测试", "性能测试", "安全测试", "集成测试"
        ]
        for category in categories:
            print(f"  - {category}")
        return
    
    # 创建测试运行器
    runner = TestRunner(base_url=args.base_url)
    
    # 运行测试
    success = runner.run_all_tests(test_categories=args.categories)
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()