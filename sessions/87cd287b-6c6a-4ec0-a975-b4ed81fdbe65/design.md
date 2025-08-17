# 大数据实时日志分析系统设计文档

## 系统架构设计

### 1. 整体架构
```
[Web服务器] → [Flume/Filebeat] → [Kafka] → [Spark Streaming] → [Redis/HDFS]
                                                    ↓
                                            [实时分析引擎]
                                                    ↓
                                            [告警系统] → [监控面板]
```

### 2. 核心组件设计

#### 2.1 数据接入层
- **Kafka集群**：3个broker节点，副本因子为2
- **Topic设计**：
  - `web-access-logs`：Web访问日志
  - `error-logs`：错误日志
  - 分区数：6个分区（支持并行处理）

#### 2.2 流处理层
- **Spark Streaming应用**：
  - 批处理间隔：2秒
  - 检查点机制：启用，间隔10秒
  - 并行度：根据Kafka分区数动态调整

#### 2.3 数据存储层
- **Redis集群**：
  - 主从复制 + 哨兵模式
  - 数据结构：Hash、ZSet、String
  - TTL设置：实时数据1小时过期
- **HDFS存储**：
  - 按日期分区存储：/logs/year=2024/month=08/day=16/
  - 文件格式：Parquet（压缩存储）

## 数据模型设计

### 1. 输入数据模型
```json
{
  "timestamp": "2024-08-16T19:13:00.000Z",
  "ip": "192.168.1.100",
  "method": "GET",
  "url": "/api/users",
  "status_code": 200,
  "response_time": 150,
  "user_agent": "Mozilla/5.0...",
  "referer": "https://example.com"
}
```

### 2. 输出数据模型
```json
{
  "window_start": "2024-08-16T19:10:00.000Z",
  "window_end": "2024-08-16T19:15:00.000Z",
  "metrics": {
    "total_requests": 15000,
    "unique_visitors": 3500,
    "avg_response_time": 200,
    "status_codes": {
      "200": 12000,
      "404": 2000,
      "500": 1000
    },
    "top_pages": [
      {"url": "/api/users", "count": 5000},
      {"url": "/home", "count": 3000}
    ]
  }
}
```

## 算法设计

### 1. 滑动窗口统计算法
- 使用Spark的`window()`函数实现时间窗口
- 窗口大小：1分钟、5分钟、15分钟
- 滑动间隔：30秒

### 2. 异常检测算法
- **阈值检测**：请求量超过历史平均值3倍
- **状态码异常**：5xx错误率超过5%
- **响应时间异常**：平均响应时间超过1秒

### 3. Top-K算法
- 使用Count-Min Sketch + Heap实现
- 内存效率高，适合大数据量场景

## 性能优化设计

### 1. Spark优化
- **内存管理**：
  - executor-memory: 4g
  - executor-cores: 2
  - driver-memory: 2g
- **序列化**：使用Kryo序列化
- **缓存策略**：对频繁访问的RDD进行缓存

### 2. Kafka优化
- **生产者配置**：
  - batch.size: 16384
  - linger.ms: 10
  - compression.type: snappy
- **消费者配置**：
  - fetch.min.bytes: 1024
  - max.poll.records: 1000

### 3. Redis优化
- **连接池**：使用Jedis连接池
- **管道操作**：批量写入减少网络开销
- **数据压缩**：对大对象进行压缩存储

## 监控和告警设计

### 1. 系统监控指标
- **处理延迟**：端到端处理时间
- **吞吐量**：每秒处理记录数
- **错误率**：处理失败比例
- **资源使用率**：CPU、内存、网络使用情况

### 2. 业务监控指标
- **访问量异常**：突增或突降
- **错误率异常**：5xx状态码比例
- **响应时间异常**：平均响应时间
- **安全异常**：可疑IP访问模式

### 3. 告警机制
- **告警级别**：INFO、WARN、ERROR、CRITICAL
- **通知方式**：邮件、短信、钉钉群消息
- **告警抑制**：避免重复告警
