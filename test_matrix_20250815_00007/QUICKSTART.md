# 测试矩阵快速开始指南

## 概述

本指南帮助您快速开始使用Amazon Q CLI API服务的完整测试矩阵。

## 前置条件

### 系统要求
- Python 3.8+
- Amazon Q CLI已安装并配置
- 服务运行在 http://localhost:8080
- 至少2GB可用内存

### 依赖安装
```bash
# 安装测试依赖
pip install pytest requests sseclient-py

# 可选：安装报告生成工具
pip install pytest-html pytest-json-report
```

## 快速测试

### 1. 检查服务状态
```bash
# 检查服务是否运行
curl http://localhost:8080/health

# 预期响应
{
  "status": "healthy",
  "qcli_available": true,
  "active_sessions": 0,
  "timestamp": 1703123456.789
}
```

### 2. 运行基础功能测试
```bash
# 进入测试目录
cd test_matrix

# 运行API接口测试（最快）
python scripts/api_test_suite.py

# 运行所有测试
python scripts/run_all_tests.py
```

### 3. 查看测试结果
```bash
# 查看测试报告
cat reports/test_results.md

# 查看JSON格式结果
cat reports/test_results.json
```

## 分类测试

### 按功能模块测试
```bash
# 只测试API接口
python scripts/run_all_tests.py --categories "API接口测试"

# 测试多个模块
python scripts/run_all_tests.py --categories "功能测试" "会话管理测试"

# 查看所有可用类别
python scripts/run_all_tests.py --list-categories
```

### 按优先级测试
```bash
# 高优先级测试（核心功能）
pytest test_matrix/scripts/ -m "high_priority"

# 快速冒烟测试
pytest test_matrix/scripts/api_test_suite.py::TestServiceInfo
```

## 常见测试场景

### 场景1: 开发环境验证
```bash
# 快速验证基本功能
python -c "
import requests
import json

base_url = 'http://localhost:8080'

# 健康检查
health = requests.get(f'{base_url}/health').json()
print('服务状态:', health['status'])

# 创建会话
session = requests.post(f'{base_url}/api/v1/sessions').json()
print('会话创建:', session['session_id'])

# 发送消息
chat = requests.post(f'{base_url}/api/v1/chat', 
    json={'message': '你好'}).json()
print('AI回复:', chat['message'][:50] + '...')

print('✅ 基本功能正常')
"
```

### 场景2: 部署前验证
```bash
# 运行核心测试套件
python scripts/run_all_tests.py --categories \
  "功能测试" "API接口测试" "会话管理测试"

# 检查测试结果
if [ $? -eq 0 ]; then
  echo "✅ 部署前验证通过"
else
  echo "❌ 发现问题，请检查测试报告"
fi
```

### 场景3: 性能基准测试
```bash
# 运行性能测试
python scripts/performance_test.py

# 并发测试
python -c "
import requests
import threading
import time

def test_concurrent():
    start = time.time()
    response = requests.post('http://localhost:8080/api/v1/chat',
        json={'message': '你好'})
    return time.time() - start

# 10个并发请求
threads = []
results = []

for i in range(10):
    t = threading.Thread(target=lambda: results.append(test_concurrent()))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print(f'平均响应时间: {sum(results)/len(results):.2f}秒')
print(f'最大响应时间: {max(results):.2f}秒')
"
```

## 测试数据说明

### 测试消息类型
- **基础消息**: 简单问候和介绍
- **技术消息**: 编程和AWS相关问题
- **文件操作**: 文件创建和管理请求
- **上下文测试**: 多轮对话场景
- **边界测试**: 空消息、超长消息等
- **安全测试**: 各种攻击向量

### 测试场景分类
- **功能场景**: 完整业务流程
- **并发场景**: 多用户同时操作
- **性能场景**: 响应时间和负载测试
- **安全场景**: 攻击防护验证
- **错误场景**: 异常情况处理

## 自定义测试

### 添加自定义测试消息
```bash
# 编辑测试数据文件
vim test_matrix/data/test_messages.json

# 添加新的测试消息
{
  "custom_messages": [
    {
      "id": "custom_001",
      "message": "你的自定义测试消息",
      "category": "custom",
      "expected_response_type": "normal",
      "description": "自定义测试描述"
    }
  ]
}
```

### 创建自定义测试脚本
```python
# custom_test.py
import requests
import pytest

BASE_URL = "http://localhost:8080"

def test_custom_functionality():
    """自定义功能测试"""
    response = requests.post(
        f"{BASE_URL}/api/v1/chat",
        json={"message": "你的测试消息"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    # 添加你的验证逻辑

if __name__ == "__main__":
    test_custom_functionality()
    print("✅ 自定义测试通过")
```

## 故障排查

### 常见问题

#### 1. 服务连接失败
```bash
# 检查服务是否运行
ps aux | grep python | grep app.py

# 检查端口是否监听
netstat -tlnp | grep 8080

# 重启服务
python app.py
```

#### 2. 测试失败
```bash
# 查看详细错误信息
python scripts/run_all_tests.py -v

# 运行单个测试文件
pytest test_matrix/scripts/api_test_suite.py -v

# 查看测试日志
tail -f test_matrix/reports/test.log
```

#### 3. Amazon Q CLI问题
```bash
# 检查Q CLI状态
q --version

# 测试Q CLI功能
q chat --message "test"

# 检查配置
q configure list
```

### 调试模式
```bash
# 启用调试模式
export DEBUG=true
python scripts/run_all_tests.py

# 保存详细日志
python scripts/run_all_tests.py 2>&1 | tee test_debug.log
```

## 持续集成

### GitHub Actions示例
```yaml
# .github/workflows/test.yml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests sseclient-py
      
      - name: Start service
        run: |
          python app.py &
          sleep 10
      
      - name: Run tests
        run: python test_matrix/scripts/run_all_tests.py
      
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test_matrix/reports/
```

### Jenkins Pipeline示例
```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'pip install pytest requests sseclient-py'
            }
        }
        
        stage('Start Service') {
            steps {
                sh 'python app.py &'
                sh 'sleep 10'
            }
        }
        
        stage('Run Tests') {
            steps {
                sh 'python test_matrix/scripts/run_all_tests.py'
            }
        }
        
        stage('Publish Results') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'test_matrix/reports',
                    reportFiles: 'test_results.md',
                    reportName: 'Test Results'
                ])
            }
        }
    }
}
```

## 最佳实践

### 1. 测试前准备
- 确保服务健康运行
- 清理之前的测试数据
- 检查系统资源充足

### 2. 测试执行
- 按优先级顺序执行
- 记录测试环境信息
- 保存详细的测试日志

### 3. 结果分析
- 重点关注失败的测试
- 分析性能指标趋势
- 识别潜在的风险点

### 4. 问题跟踪
- 记录所有发现的问题
- 分类问题的严重程度
- 制定修复计划和时间表

## 获取帮助

### 文档资源
- [完整测试矩阵文档](README.md)
- [API接口文档](../docs/API.md)
- [部署指南](../docs/DEPLOYMENT.md)

### 联系支持
- 提交Issue到项目仓库
- 查看FAQ和常见问题
- 联系开发团队获取支持

---

**快速开始完成！** 🎉

现在您可以开始使用完整的测试矩阵来验证Amazon Q CLI API服务的功能和性能了。