#!/usr/bin/env python3
"""
部署验证测试脚本

验证Amazon Q CLI API服务是否正确部署和运行。
"""

import requests
import json
import time
import sys
from typing import Optional


class DeploymentTester:
    """部署测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url.rstrip('/')
        self.session_id: Optional[str] = None
    
    def test_service_info(self) -> bool:
        """测试服务信息接口"""
        try:
            print("🔍 测试服务信息接口...")
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 服务信息接口失败: HTTP {response.status_code}")
                return False
            
            data = response.json()
            if data.get('service') != 'Amazon Q CLI API Service':
                print(f"❌ 服务信息不正确: {data}")
                return False
            
            print(f"✅ 服务信息正常: {data.get('service')} v{data.get('version')}")
            return True
            
        except Exception as e:
            print(f"❌ 服务信息接口异常: {e}")
            return False
    
    def test_health_check(self) -> bool:
        """测试健康检查接口"""
        try:
            print("🔍 测试健康检查接口...")
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 健康检查失败: HTTP {response.status_code}")
                return False
            
            data = response.json()
            status = data.get('status')
            qcli_available = data.get('qcli_available')
            
            if status not in ['healthy', 'degraded']:
                print(f"❌ 健康状态异常: {status}")
                return False
            
            print(f"✅ 健康检查正常: {status}, Q CLI可用: {qcli_available}")
            
            if not qcli_available:
                print("⚠️  警告: Amazon Q CLI不可用，某些功能可能受限")
            
            return True
            
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_session_management(self) -> bool:
        """测试会话管理"""
        try:
            print("🔍 测试会话管理...")
            
            # 创建会话
            response = requests.post(f"{self.base_url}/api/v1/sessions", timeout=10)
            
            if response.status_code != 201:
                print(f"❌ 创建会话失败: HTTP {response.status_code}")
                return False
            
            data = response.json()
            self.session_id = data.get('session_id')
            
            if not self.session_id:
                print(f"❌ 会话ID为空: {data}")
                return False
            
            print(f"✅ 会话创建成功: {self.session_id}")
            
            # 查询会话
            response = requests.get(f"{self.base_url}/api/v1/sessions/{self.session_id}", timeout=10)
            
            if response.status_code != 200:
                print(f"❌ 查询会话失败: HTTP {response.status_code}")
                return False
            
            session_info = response.json()
            if session_info.get('session_id') != self.session_id:
                print(f"❌ 会话信息不匹配: {session_info}")
                return False
            
            print(f"✅ 会话查询成功: 消息数量 {session_info.get('message_count', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ 会话管理异常: {e}")
            return False
    
    def test_chat_api(self) -> bool:
        """测试聊天API"""
        try:
            print("🔍 测试聊天API...")
            
            if not self.session_id:
                print("❌ 没有可用的会话ID")
                return False
            
            # 发送测试消息
            chat_data = {
                "session_id": self.session_id,
                "message": "你好，这是一个测试消息"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 503:
                print("⚠️  Q CLI不可用，跳过聊天测试")
                return True
            
            if response.status_code != 200:
                print(f"❌ 聊天API失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
            
            data = response.json()
            if not data.get('message'):
                print(f"❌ 聊天响应为空: {data}")
                return False
            
            print(f"✅ 聊天API正常: 收到回复 ({len(data['message'])} 字符)")
            return True
            
        except Exception as e:
            print(f"❌ 聊天API异常: {e}")
            return False
    
    def test_stream_chat(self) -> bool:
        """测试流式聊天"""
        try:
            print("🔍 测试流式聊天...")
            
            if not self.session_id:
                print("❌ 没有可用的会话ID")
                return False
            
            chat_data = {
                "session_id": self.session_id,
                "message": "请简单介绍一下自己"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/chat/stream",
                json=chat_data,
                timeout=30,
                stream=True
            )
            
            if response.status_code == 503:
                print("⚠️  Q CLI不可用，跳过流式聊天测试")
                return True
            
            if response.status_code != 200:
                print(f"❌ 流式聊天失败: HTTP {response.status_code}")
                return False
            
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('text/event-stream'):
                print(f"❌ 流式聊天响应类型错误: {content_type}")
                return False
            
            # 读取流式响应
            chunk_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    chunk_count += 1
                    if chunk_count >= 3:  # 读取几个chunk就够了
                        break
            
            if chunk_count == 0:
                print("❌ 没有收到流式数据")
                return False
            
            print(f"✅ 流式聊天正常: 收到 {chunk_count} 个数据块")
            return True
            
        except Exception as e:
            print(f"❌ 流式聊天异常: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """测试错误处理"""
        try:
            print("🔍 测试错误处理...")
            
            # 测试无效请求
            response = requests.post(
                f"{self.base_url}/api/v1/chat",
                json={"message": ""},  # 空消息
                timeout=10
            )
            
            if response.status_code != 400:
                print(f"❌ 错误处理失败: 应该返回400，实际返回 {response.status_code}")
                return False
            
            data = response.json()
            if 'error' not in data:
                print(f"❌ 错误响应格式不正确: {data}")
                return False
            
            print(f"✅ 错误处理正常: {data.get('error')}")
            
            # 测试404错误
            response = requests.get(f"{self.base_url}/nonexistent-endpoint", timeout=10)
            
            if response.status_code != 404:
                print(f"❌ 404处理失败: 应该返回404，实际返回 {response.status_code}")
                return False
            
            print("✅ 404错误处理正常")
            return True
            
        except Exception as e:
            print(f"❌ 错误处理测试异常: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理测试数据"""
        try:
            if self.session_id:
                print("🧹 清理测试会话...")
                response = requests.delete(
                    f"{self.base_url}/api/v1/sessions/{self.session_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ 测试会话已清理")
                else:
                    print(f"⚠️  清理会话失败: HTTP {response.status_code}")
        except Exception as e:
            print(f"⚠️  清理异常: {e}")
    
    def run_all_tests(self) -> bool:
        """运行所有测试"""
        print(f"🚀 开始测试Amazon Q CLI API服务部署")
        print(f"📍 测试地址: {self.base_url}")
        print("=" * 50)
        
        tests = [
            ("服务信息", self.test_service_info),
            ("健康检查", self.test_health_check),
            ("会话管理", self.test_session_management),
            ("聊天API", self.test_chat_api),
            ("流式聊天", self.test_stream_chat),
            ("错误处理", self.test_error_handling),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print()
            if test_func():
                passed += 1
            else:
                print(f"💥 {test_name} 测试失败")
        
        print()
        print("=" * 50)
        print(f"📊 测试结果: {passed}/{total} 通过")
        
        if passed == total:
            print("🎉 所有测试通过！服务部署成功")
            return True
        else:
            print("❌ 部分测试失败，请检查服务配置")
            return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Amazon Q CLI API服务部署验证")
    parser.add_argument(
        "--url",
        default="http://localhost:8080",
        help="服务URL (默认: http://localhost:8080)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="不清理测试数据"
    )
    
    args = parser.parse_args()
    
    tester = DeploymentTester(args.url)
    
    try:
        success = tester.run_all_tests()
        
        if not args.no_cleanup:
            tester.cleanup()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        if not args.no_cleanup:
            tester.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        if not args.no_cleanup:
            tester.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()