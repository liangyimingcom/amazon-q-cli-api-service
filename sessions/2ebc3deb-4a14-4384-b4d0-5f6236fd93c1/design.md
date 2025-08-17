# 日志分析系统设计文档

## 系统架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   日志文件       │───▶│   数据处理层     │───▶│   输出层         │
│  (Input Layer)  │    │ (Processing)    │    │ (Output Layer)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 模块设计

#### 1. 日志解析模块 (LogParser)
**职责**: 解析不同格式的日志文件
```python
class LogParser:
    def parse_line(self, line: str) -> dict
    def detect_format(self, sample_lines: list) -> str
    def parse_file(self, file_path: str) -> Iterator[dict]
```

**支持的日志格式**:
- Common Log Format: `IP - - [timestamp] "method URL protocol" status size`
- Combined Log Format: 在Common基础上增加referer和user-agent

#### 2. 数据分析模块 (DataAnalyzer)
**职责**: 对解析后的数据进行统计分析
```python
class DataAnalyzer:
    def analyze_traffic(self, data: Iterator[dict]) -> dict
    def analyze_popular_pages(self, data: Iterator[dict]) -> list
    def analyze_status_codes(self, data: Iterator[dict]) -> dict
    def analyze_user_agents(self, data: Iterator[dict]) -> dict
```

#### 3. 报告生成模块 (ReportGenerator)
**职责**: 生成各种格式的分析报告
```python
class ReportGenerator:
    def generate_text_report(self, analysis_result: dict) -> str
    def generate_json_report(self, analysis_result: dict) -> str
    def save_report(self, content: str, file_path: str) -> None
```

#### 4. 主控制模块 (LogAnalyzer)
**职责**: 协调各个模块，提供统一接口
```python
class LogAnalyzer:
    def __init__(self, config: dict)
    def analyze(self, log_file_path: str) -> dict
    def run_analysis(self, args: argparse.Namespace) -> None
```

## 数据流设计

### 处理流程
1. **文件读取**: 逐行读取日志文件，避免内存溢出
2. **格式检测**: 自动检测日志格式
3. **数据解析**: 将每行日志解析为结构化数据
4. **数据聚合**: 使用字典和计数器进行实时统计
5. **结果输出**: 生成报告并保存

### 数据结构
```python
# 解析后的日志条目
LogEntry = {
    'ip': str,
    'timestamp': datetime,
    'method': str,
    'url': str,
    'status_code': int,
    'response_size': int,
    'user_agent': str,
    'referer': str
}

# 分析结果
AnalysisResult = {
    'total_requests': int,
    'unique_visitors': int,
    'daily_stats': dict,
    'hourly_stats': dict,
    'popular_pages': list,
    'status_code_stats': dict,
    'user_agent_stats': dict
}
```

## 性能优化策略

### 内存优化
- 使用生成器(Iterator)处理大文件，避免一次性加载到内存
- 使用collections.Counter进行高效计数
- 定期清理不需要的中间数据

### 处理速度优化
- 使用正则表达式预编译
- 批量处理数据而非逐条处理
- 使用多进程处理超大文件（可选扩展）

## 错误处理策略

### 异常类型
- 文件不存在或无权限访问
- 日志格式无法识别
- 内存不足
- 磁盘空间不足

### 处理方式
- 使用try-catch包装关键操作
- 提供详细的错误信息和建议
- 支持部分失败继续处理
- 记录错误日志便于调试

## 配置设计

### 配置文件格式 (config.json)
```json
{
    "input": {
        "log_format": "auto",
        "encoding": "utf-8"
    },
    "analysis": {
        "time_range": {
            "start": null,
            "end": null
        },
        "top_pages_limit": 10,
        "top_user_agents_limit": 5
    },
    "output": {
        "format": ["text", "json"],
        "output_dir": "./reports/"
    }
}
```
