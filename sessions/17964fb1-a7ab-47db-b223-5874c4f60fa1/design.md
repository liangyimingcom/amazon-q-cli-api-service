# 设计文档 - Apache Spark大规模CSV数据处理系统

## 系统架构

### 整体架构
```
数据源层 -> 数据处理层 -> 数据存储层 -> 应用层
   |           |            |          |
CSV文件 -> Spark处理引擎 -> 分布式存储 -> 报表展示
```

### 技术栈选择
- **计算引擎**: Apache Spark 3.x
- **编程语言**: Python (PySpark)
- **存储格式**: Parquet (高性能), CSV (兼容性)
- **配置管理**: YAML配置文件
- **日志系统**: Python logging + Spark UI

## 核心模块设计

### 1. 数据读取模块 (DataReader)
```python
class CSVDataReader:
    def __init__(self, spark_session, config)
    def read_csv_files(self, file_paths, schema=None)
    def infer_schema(self, sample_file)
    def validate_data_format(self, df)
```

**功能特性**:
- 支持通配符批量读取文件
- 自动schema推断和验证
- 支持自定义分隔符和编码
- 错误文件跳过机制

### 2. 数据清洗模块 (DataCleaner)
```python
class DataCleaner:
    def remove_duplicates(self, df)
    def handle_null_values(self, df, strategy='drop')
    def standardize_formats(self, df)
    def filter_invalid_records(self, df, rules)
    def validate_data_quality(self, df)
```

**清洗规则**:
- 重复数据：基于order_id去重
- 空值处理：关键字段空值删除，非关键字段填充默认值
- 数据验证：数量和价格必须为正数，日期格式标准化
- 异常值检测：基于统计方法识别离群值

### 3. 数据聚合模块 (DataAggregator)
```python
class DataAggregator:
    def aggregate_by_date(self, df)
    def aggregate_by_category(self, df)
    def calculate_statistics(self, df)
    def generate_summary_report(self, df)
```

**聚合逻辑**:
- 日期聚合：按天/月/年统计销售额和订单量
- 类别聚合：按产品类别统计销售情况
- 地区聚合：按地区统计销售分布
- 统计指标：总销售额、平均订单金额、热销产品等

### 4. 数据输出模块 (DataWriter)
```python
class DataWriter:
    def write_to_parquet(self, df, output_path)
    def write_to_csv(self, df, output_path)
    def write_summary_report(self, summary_data)
    def partition_by_date(self, df, partition_col)
```

## 性能优化策略

### 1. 内存管理
- 使用DataFrame缓存减少重复计算
- 合理设置Spark executor内存配置
- 采用列式存储格式(Parquet)提高I/O效率

### 2. 并行处理
- 根据文件大小自动调整分区数
- 使用repartition()优化数据分布
- 避免shuffle操作，优先使用窄依赖转换

### 3. 资源配置
```yaml
spark_config:
  executor_memory: "4g"
  executor_cores: 2
  num_executors: 4
  driver_memory: "2g"
  serializer: "org.apache.spark.serializer.KryoSerializer"
```

## 错误处理机制

### 1. 异常分类
- 文件读取异常：文件不存在、格式错误
- 数据处理异常：schema不匹配、数据类型转换失败
- 资源异常：内存不足、磁盘空间不够

### 2. 容错策略
- 文件级别容错：单个文件失败不影响整体处理
- 记录级别容错：错误记录记录到日志，继续处理其他数据
- 自动重试：网络异常等临时性错误自动重试3次

## 监控和日志

### 1. 处理进度监控
- 实时显示处理进度百分比
- 记录各阶段耗时统计
- 资源使用情况监控

### 2. 数据质量监控
- 数据清洗前后记录数对比
- 异常数据比例统计
- 数据完整性检查结果

### 3. 日志输出格式
```
[2024-01-15 10:30:15] INFO - 开始处理文件: sales_data_20240115.csv
[2024-01-15 10:30:20] INFO - 原始记录数: 1,000,000
[2024-01-15 10:30:25] WARN - 发现重复记录: 1,250条
[2024-01-15 10:30:30] INFO - 清洗后记录数: 998,750
[2024-01-15 10:35:15] INFO - 处理完成，耗时: 5分钟
```
