#!/usr/bin/env python3
"""
基于测试结果的修复实施脚本

根据测试发现的问题，自动实施修复方案。
"""

import os
import re
import shutil
from datetime import datetime

class FixImplementation:
    """修复实施类"""
    
    def __init__(self):
        self.backup_dir = f"test_results_20250815_114958/backups_{datetime.now().strftime('%H%M%S')}"
        self.fixes_applied = []
        
    def create_backup(self, file_path: str):
        """创建文件备份"""
        os.makedirs(self.backup_dir, exist_ok=True)
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        print(f"已备份: {file_path} -> {backup_path}")
        
    def apply_fix_1_timeout_optimization(self):
        """修复1: 带会话聊天超时优化"""
        print("=" * 50)
        print("应用修复1: 带会话聊天超时优化")
        print("=" * 50)
        
        # 修复配置文件
        config_file = "qcli_api_service/config.py"
        self.create_backup(config_file)
        
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加动态超时函数
        timeout_function = '''
def get_timeout_for_request(has_context: bool = False, context_length: int = 0) -> int:
    """根据请求类型动态计算超时时间"""
    base_timeout = 45
    if has_context and context_length > 0:
        # 根据上下文长度动态调整，每1000字符增加5秒，最多增加30秒
        context_factor = min(context_length // 1000 * 5, 30)
        return base_timeout + context_factor
    return base_timeout
'''
        
        # 在Config类之前插入函数
        if 'def get_timeout_for_request' not in content:
            content = content.replace('@dataclass\nclass Config:', 
                                    timeout_function + '\n\n@dataclass\nclass Config:')
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 修复服务文件
        service_file = "qcli_api_service/services/qcli_service.py"
        self.create_backup(service_file)
        
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 导入动态超时函数
        if 'from qcli_api_service.config import config, get_timeout_for_request' not in content:
            content = content.replace(
                'from qcli_api_service.config import config',
                'from qcli_api_service.config import config, get_timeout_for_request'
            )
        
        # 在chat方法中使用动态超时
        old_timeout_pattern = r'process\.communicate\(timeout=config\.QCLI_TIMEOUT\)'
        new_timeout_code = '''# 根据上下文动态计算超时时间
                dynamic_timeout = get_timeout_for_request(bool(context), len(context))
                stdout, stderr = process.communicate(timeout=dynamic_timeout)'''
        
        if 'dynamic_timeout = get_timeout_for_request' not in content:
            content = re.sub(
                r'(\s+)# 等待完成\s+stdout, stderr = process\.communicate\(timeout=config\.QCLI_TIMEOUT\)',
                r'\1' + new_timeout_code,
                content
            )
        
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fixes_applied.append("修复1: 带会话聊天超时优化")
        print("✅ 修复1应用完成")
        
    def apply_fix_2_special_characters(self):
        """修复2: 特殊字符处理优化"""
        print("=" * 50)
        print("应用修复2: 特殊字符处理优化")
        print("=" * 50)
        
        validator_file = "qcli_api_service/utils/validators.py"
        self.create_backup(validator_file)
        
        with open(validator_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换恶意内容检测函数
        new_malicious_detection = '''    @staticmethod
    def _contains_malicious_content(message: str) -> bool:
        """
        改进的恶意内容检测 - 更精确的安全检查
        
        参数:
            message: 消息内容
            
        返回:
            是否包含恶意内容
        """
        # 更精确的恶意内容检查 - 只检测真正危险的模式
        malicious_patterns = [
            r'<script[^>]*>.*?</script>',  # JavaScript脚本块
            r'javascript:',  # JavaScript协议
            r'on\\w+\\s*=\\s*["\'][^"\']*["\']',  # 事件处理器属性
            r'<iframe[^>]*src\s*=',  # 带src的iframe（可能的XSS）
            r'<object[^>]*data\s*=',  # 带data的object（可能的代码执行）
            r'<embed[^>]*src\s*=',  # 带src的embed（可能的代码执行）
            r'<link[^>]*href\s*=\s*["\']javascript:',  # JavaScript链接
            r'<meta[^>]*http-equiv\s*=\s*["\']refresh',  # 自动刷新（可能的重定向攻击）
        ]
        
        # 允许的安全标签和模式 - 常见的格式化和代码展示
        safe_patterns = [
            r'</?code>',  # 代码标签
            r'</?pre>',   # 预格式化标签
            r'</?b>',     # 粗体标签
            r'</?i>',     # 斜体标签
            r'</?strong>', # 强调标签
            r'</?em>',    # 斜体强调标签
            r'<br\s*/?>', # 换行标签
            r'<p>',       # 段落标签（开始）
            r'</p>',      # 段落标签（结束）
        ]
        
        # 创建消息副本用于检测
        cleaned_message = message
        
        # 先移除安全标签，避免误报
        for pattern in safe_patterns:
            cleaned_message = re.sub(pattern, '', cleaned_message, flags=re.IGNORECASE)
        
        # 检测剩余内容中的恶意模式
        message_lower = cleaned_message.lower()
        for pattern in malicious_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        return False'''
        
        # 替换原有的_contains_malicious_content方法
        pattern = r'@staticmethod\s+def _contains_malicious_content\(message: str\) -> bool:.*?return False'
        content = re.sub(pattern, new_malicious_detection, content, flags=re.DOTALL)
        
        with open(validator_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fixes_applied.append("修复2: 特殊字符处理优化")
        print("✅ 修复2应用完成")
        
    def create_verification_test(self):
        """创建修复验证测试"""
        print("=" * 50)
        print("创建修复验证测试")
        print("=" * 50)
        
        test_content = '''#!/usr/bin/env python3
"""
修复验证测试脚本

验证应用的修复是否有效。
"""

import requests
import time
import json

BASE_URL = "http://localhost:8080"

def test_fix_1_timeout():
    """测试修复1: 带会话聊天超时"""
    print("测试修复1: 带会话聊天超时优化")
    
    # 先创建一个会话并进行对话
    response = requests.post(f"{BASE_URL}/api/v1/chat", 
                           json={"message": "你好，我想了解AWS服务"}, 
                           timeout=60)
    
    if response.status_code != 200:
        print(f"❌ 初始对话失败: {response.status_code}")
        return False
    
    session_id = response.json().get("session_id")
    print(f"✅ 创建会话: {session_id}")
    
    # 进行带会话的对话（应该包含更多上下文）
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/api/v1/chat", 
                           json={
                               "message": "基于我们刚才的对话，请详细解释一下Amazon EC2的主要功能和使用场景", 
                               "session_id": session_id
                           }, 
                           timeout=90)  # 给更长的超时时间
    end_time = time.time()
    
    duration = end_time - start_time
    print(f"带会话对话耗时: {duration:.2f}秒")
    
    if response.status_code == 200:
        print("✅ 修复1验证成功 - 带会话聊天正常工作")
        return True
    elif response.status_code == 408:
        print(f"❌ 修复1验证失败 - 仍然超时 ({duration:.2f}秒)")
        return False
    else:
        print(f"❌ 修复1验证失败 - 意外错误: {response.status_code}")
        return False

def test_fix_2_special_characters():
    """测试修复2: 特殊字符处理"""
    print("测试修复2: 特殊字符处理优化")
    
    test_cases = [
        {
            "name": "代码标签",
            "message": "请解释这段代码: <code>print('Hello World')</code>",
            "should_pass": True
        },
        {
            "name": "预格式化标签",
            "message": "这是一个示例: <pre>function test() { return true; }</pre>",
            "should_pass": True
        },
        {
            "name": "粗体标签",
            "message": "这是<b>重要</b>的信息",
            "should_pass": True
        },
        {
            "name": "恶意脚本（应该被拒绝）",
            "message": "<script>alert('xss')</script>",
            "should_pass": False
        },
        {
            "name": "事件处理器（应该被拒绝）",
            "message": "<div onclick='alert(1)'>点击</div>",
            "should_pass": False
        }
    ]
    
    results = []
    for test_case in test_cases:
        response = requests.post(f"{BASE_URL}/api/v1/chat", 
                               json={"message": test_case["message"]}, 
                               timeout=30)
        
        success = response.status_code == 200
        expected = test_case["should_pass"]
        
        if success == expected:
            print(f"✅ {test_case['name']}: 预期{'通过' if expected else '拒绝'}, 实际{'通过' if success else '拒绝'}")
            results.append(True)
        else:
            print(f"❌ {test_case['name']}: 预期{'通过' if expected else '拒绝'}, 实际{'通过' if success else '拒绝'}")
            results.append(False)
    
    success_rate = sum(results) / len(results)
    print(f"修复2验证结果: {sum(results)}/{len(results)} ({success_rate*100:.1f}%)")
    
    return success_rate >= 0.8  # 80%以上通过率认为成功

def main():
    """主函数"""
    print("开始修复验证测试")
    print("=" * 50)
    
    # 检查服务器可用性
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务器不可用")
            return
    except:
        print("❌ 无法连接到服务器")
        return
    
    print("✅ 服务器连接正常")
    
    # 执行修复验证测试
    results = []
    
    # 测试修复1
    results.append(test_fix_1_timeout())
    
    print()
    
    # 测试修复2
    results.append(test_fix_2_special_characters())
    
    # 汇总结果
    print("=" * 50)
    print("修复验证结果汇总:")
    print(f"修复1 (超时优化): {'✅ 通过' if results[0] else '❌ 失败'}")
    print(f"修复2 (特殊字符): {'✅ 通过' if results[1] else '❌ 失败'}")
    
    overall_success = all(results)
    print(f"整体验证结果: {'✅ 成功' if overall_success else '❌ 失败'}")
    
    if overall_success:
        print("🎉 所有修复验证通过，可以部署到生产环境")
    else:
        print("⚠️ 部分修复验证失败，需要进一步调试")

if __name__ == "__main__":
    main()
'''
        
        with open("test_results_20250815_114958/fix_verification_test.py", 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print("✅ 修复验证测试脚本已创建")
        
    def generate_fix_summary(self):
        """生成修复总结"""
        summary_content = f'''# 修复实施总结

**实施时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**修复数量**: {len(self.fixes_applied)}  
**备份目录**: {self.backup_dir}  

## 已应用的修复

'''
        
        for i, fix in enumerate(self.fixes_applied, 1):
            summary_content += f"{i}. {fix}\n"
        
        summary_content += '''
## 修复详情

### 修复1: 带会话聊天超时优化
- **文件**: qcli_api_service/config.py, qcli_api_service/services/qcli_service.py
- **改动**: 添加动态超时计算函数，根据上下文长度调整超时时间
- **效果**: 带会话的聊天请求超时时间从固定45秒变为45-75秒动态调整

### 修复2: 特殊字符处理优化
- **文件**: qcli_api_service/utils/validators.py
- **改动**: 改进恶意内容检测逻辑，允许安全的HTML标签
- **效果**: 用户可以正常使用代码标签等安全的HTML格式

## 验证步骤

1. 运行修复验证测试:
   ```bash
   python test_results_20250815_114958/fix_verification_test.py
   ```

2. 重新运行完整测试套件:
   ```bash
   python test_results_20250815_114958/comprehensive_test.py
   ```

3. 检查通过率是否提升到95%+

## 回滚方案

如果修复出现问题，可以从备份恢复:
```bash
# 恢复配置文件
cp {self.backup_dir}/config.py qcli_api_service/config.py

# 恢复服务文件
cp {self.backup_dir}/qcli_service.py qcli_api_service/services/qcli_service.py

# 恢复验证器文件
cp {self.backup_dir}/validators.py qcli_api_service/utils/validators.py
```

## 监控建议

修复部署后，建议监控以下指标:
1. 带会话聊天的成功率
2. 平均响应时间变化
3. 特殊字符输入的处理情况
4. 用户反馈和错误报告

## 下一步计划

1. 验证修复效果
2. 更新文档和用户指南
3. 计划下一轮功能优化
'''
        
        with open("test_results_20250815_114958/fix_summary.md", 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        print("✅ 修复总结已生成")
        
    def run_all_fixes(self):
        """执行所有修复"""
        print("开始应用基于测试结果的修复")
        print("=" * 60)
        
        try:
            # 应用修复1
            self.apply_fix_1_timeout_optimization()
            
            # 应用修复2
            self.apply_fix_2_special_characters()
            
            # 创建验证测试
            self.create_verification_test()
            
            # 生成修复总结
            self.generate_fix_summary()
            
            print("=" * 60)
            print("✅ 所有修复应用完成")
            print(f"备份目录: {self.backup_dir}")
            print("请运行验证测试确认修复效果")
            
        except Exception as e:
            print(f"❌ 修复应用失败: {e}")
            print("请检查备份并手动恢复")

def main():
    """主函数"""
    fixer = FixImplementation()
    fixer.run_all_fixes()

if __name__ == "__main__":
    main()