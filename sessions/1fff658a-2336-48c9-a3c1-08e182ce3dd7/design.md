# 日志分析系统设计文档

## 系统架构

### 整体架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   日志文件输入   │───▶│   数据处理引擎   │───▶│   结果输出模块   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   文件读取器     │    │   统计计算器     │    │   报告生成器     │
│   日志解析器     │    │   数据聚合器     │    │   CSV导出器     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 核心模块设计

#### 1. 日志解析模块 (LogParser)
**职责**: 解析日志文件，提取关键信息
```python
class LogParser:
    def parse_line(self, line: str) -> LogEntry
    def parse_file(self, file_path: str) -> Iterator[LogEntry]
```

**数据结构**:
```python
@dataclass
class LogEntry:
    ip_address: str
    timestamp: datetime
    method: str
    url: str
    status_code: int
    response_size: int
```

#### 2. 统计分析模块 (StatisticsEngine)
**职责**: 对解析后的数据进行统计分析
```python
class StatisticsEngine:
    def calculate_pv(self, entries: List[LogEntry]) -> int
    def calculate_uv(self, entries: List[LogEntry]) -> int
    def get_hourly_stats(self, entries: List[LogEntry]) -> Dict[str, int]
    def get_top_pages(self, entries: List[LogEntry], limit: int) -> List[Tuple[str, int]]
```

#### 3. 报告生成模块 (ReportGenerator)
**职责**: 生成各种格式的分析报告
```python
class ReportGenerator:
    def generate_text_report(self, stats: Statistics) -> str
    def export_to_csv(self, stats: Statistics, file_path: str) -> None
    def print_summary(self, stats: Statistics) -> None
```

## 数据流设计

### 处理流程
1. **文件读取阶段**
   - 逐行读取日志文件
   - 使用正则表达式解析每行日志
   - 验证数据格式有效性

2. **数据处理阶段**
   - 将解析结果存储在内存中
   - 按时间维度进行数据分组
   - 计算各项统计指标

3. **结果输出阶段**
   - 生成文本格式统计报告
   - 导出CSV格式详细数据
   - 在控制台显示关键指标

### 数据存储策略
- 使用Python字典和列表进行内存存储
- 按小时分组存储访问记录
- 使用集合(Set)去重计算UV

## 算法设计

### 日志解析算法
```python
LOG_PATTERN = r'(\S+) \S+ \S+ \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) \S+" (\d{3}) (\d+|-)'
```

### 统计算法
1. **PV统计**: 直接计数所有有效请求
2. **UV统计**: 使用Set数据结构对IP地址去重
3. **时间分组**: 使用datetime模块按小时分组
4. **排序算法**: 使用Python内置sorted()函数

## 性能优化策略

### 内存优化
- 使用生成器(Generator)逐行处理大文件
- 及时释放不需要的数据对象
- 使用__slots__优化数据类内存占用

### 处理速度优化
- 预编译正则表达式
- 使用批量处理减少I/O操作
- 并行处理多个文件(可选扩展)

## 错误处理设计

### 异常类型
```python
class LogAnalysisError(Exception): pass
class InvalidLogFormatError(LogAnalysisError): pass
class FileNotFoundError(LogAnalysisError): pass
```

### 错误处理策略
- 对无效日志行进行跳过并记录警告
- 文件不存在时提供明确错误信息
- 内存不足时提供优化建议

## 配置管理

### 配置文件格式 (config.yaml)
```yaml
input:
  log_file_path: "/var/log/access.log"
  log_format: "apache_common"

output:
  report_file: "analysis_report.txt"
  csv_file: "detailed_stats.csv"
  
processing:
  batch_size: 10000
  memory_limit_mb: 1024
```
