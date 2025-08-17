# 设计文档 - 网站日志分析系统

## 系统架构

### 整体架构
```
[Web服务器] → [日志文件] → [日志收集器] → [消息队列] → [数据处理器] → [数据库] → [Web界面]
```

### 技术栈选择
- **日志收集**: Fluentd / Filebeat
- **消息队列**: Apache Kafka
- **数据处理**: Apache Spark / Python pandas
- **数据存储**: 
  - 原始数据: HDFS / Amazon S3
  - 统计结果: MySQL / PostgreSQL
- **Web框架**: Flask (Python)
- **前端**: Bootstrap + Chart.js

## 核心组件设计

### 1. 日志收集器 (Log Collector)
```python
class LogCollector:
    def __init__(self, log_path, kafka_topic):
        self.log_path = log_path
        self.kafka_producer = KafkaProducer()
        
    def parse_log_line(self, line):
        # 解析Common Log Format
        # 返回结构化数据
        
    def monitor_log_file(self):
        # 监控日志文件变化
        # 实时发送到Kafka
```

### 2. 数据处理器 (Data Processor)
```python
class LogProcessor:
    def process_batch(self, log_records):
        # 批量处理日志记录
        # 生成统计数据
        
    def calculate_hourly_stats(self, records):
        # 计算每小时统计
        
    def calculate_daily_stats(self, records):
        # 计算每日统计
        
    def get_top_pages(self, records, limit=10):
        # 获取热门页面
```

### 3. 数据存储层
```sql
-- 原始日志表
CREATE TABLE raw_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    ip_address VARCHAR(45),
    method VARCHAR(10),
    url VARCHAR(500),
    status_code INT,
    response_size BIGINT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 小时统计表
CREATE TABLE hourly_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hour_timestamp DATETIME,
    total_requests INT,
    unique_visitors INT,
    total_bytes BIGINT,
    avg_response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 热门页面表
CREATE TABLE top_pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    url VARCHAR(500),
    request_count INT,
    rank_position INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. Web界面设计
```python
# Flask应用结构
app/
├── __init__.py
├── routes/
│   ├── dashboard.py    # 仪表板路由
│   └── api.py         # API接口
├── templates/
│   ├── dashboard.html  # 主仪表板
│   └── reports.html   # 报告页面
├── static/
│   ├── css/
│   └── js/
└── models/
    └── stats.py       # 数据模型
```

## 数据流设计

### 实时处理流程
1. Web服务器生成访问日志
2. Fluentd监控日志文件变化
3. 解析日志并发送到Kafka
4. Spark Streaming消费Kafka消息
5. 实时计算统计指标
6. 更新数据库中的统计表
7. Web界面展示最新数据

### 批处理流程
1. 每小时触发批处理任务
2. 从原始日志表读取数据
3. 计算详细统计指标
4. 生成报告和图表数据
5. 更新汇总统计表

## 性能优化策略

### 数据库优化
- 对timestamp, ip_address, url字段建立索引
- 使用分区表按日期分区
- 定期清理历史数据

### 缓存策略
- Redis缓存热门查询结果
- 缓存过期时间设置为5分钟
- 预计算常用统计指标

### 扩展性设计
- Kafka支持多分区并行处理
- Spark可以增加worker节点
- 数据库支持读写分离

## 监控和告警
- 系统健康检查接口
- 日志处理延迟监控
- 数据库连接池监控
- 磁盘空间使用监控

## 安全考虑
- 日志数据脱敏处理
- Web界面访问控制
- 数据库连接加密
- API接口限流
