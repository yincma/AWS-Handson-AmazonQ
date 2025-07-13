# 架构设计文档

## 系统架构图

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│    Slack    │───▶│ API Gateway  │───▶│   Lambda    │
│   Client    │    │              │    │  Function   │
└─────────────┘    └──────────────┘    └─────────────┘
                                              │
                   ┌─────────────────────────┼─────────────────────────┐
                   │                         │                         │
                   ▼                         ▼                         ▼
            ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
            │  DynamoDB   │         │   Bedrock   │         │  Secrets    │
            │    Table    │         │   Claude    │         │  Manager    │
            └─────────────┘         └─────────────┘         └─────────────┘
```

## 核心组件

### 1. API Gateway
- **作用**: 接收 Slack 请求，路由到 Lambda
- **端点**:
  - `POST /slack/command` - Slash Commands
  - `POST /slack/interaction` - 按钮交互
- **特性**: CORS 支持、请求验证、限流

### 2. Lambda Function
- **运行时**: Python 3.10
- **内存**: 256MB
- **超时**: 30秒
- **功能**:
  - Slack 请求签名验证
  - Slash Command 处理
  - Bedrock 题目生成
  - DynamoDB 数据操作
  - Block Kit 消息构建

### 3. DynamoDB 表设计

#### QuizScores 表结构
```json
{
  "TableName": "QuizScores",
  "KeySchema": [
    {
      "AttributeName": "user_id",
      "KeyType": "HASH"
    }
  ],
  "AttributeDefinitions": [
    {
      "AttributeName": "user_id", 
      "AttributeType": "S"
    },
    {
      "AttributeName": "score",
      "AttributeType": "N"
    }
  ],
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "ScoreIndex",
      "KeySchema": [
        {
          "AttributeName": "score",
          "KeyType": "HASH"
        }
      ]
    }
  ]
}
```

#### 数据模型
```json
{
  "user_id": "U1234567890",           // Slack 用户 ID (主键)
  "score": 15,                       // 正确答题数
  "total_questions": 20,             // 总答题数  
  "last_updated": 1640995200,        // 最后更新时间戳
  "accuracy_rate": 0.75,             // 正确率 (可选)
  "daily_streak": 5,                 // 连续答题天数 (扩展功能)
  "favorite_topics": ["EC2", "S3"]   // 偏好主题 (扩展功能)
}
```

### 4. Amazon Bedrock
- **模型**: Claude 3 Haiku
- **用途**: 生成 AWS 云服务多选题
- **输入**: 结构化提示词
- **输出**: 题目、选项、答案、解释

### 5. AWS Secrets Manager
- **存储内容**:
  - `slack/signing-secret`: Slack 应用签名密钥
  - `slack/bot-token`: Slack Bot OAuth Token
- **访问方式**: Lambda 运行时获取

## 数据流程

### 1. Quiz 命令流程
```
用户输入 /awsquiz
    ↓
API Gateway 接收请求
    ↓
Lambda 验证 Slack 签名
    ↓
调用 Bedrock 生成题目
    ↓
构建 Block Kit 消息
    ↓
返回给 Slack 显示
```

### 2. 答题交互流程
```
用户点击答案按钮
    ↓
API Gateway 接收交互请求
    ↓
Lambda 解析答案数据
    ↓
判断正确性并更新 DynamoDB
    ↓
构建结果消息
    ↓
返回反馈给用户
```

### 3. 排行榜查询流程
```
用户输入 /leaderboard
    ↓
API Gateway 接收请求
    ↓
Lambda 扫描 DynamoDB 表
    ↓
按分数排序获取前5名
    ↓
查询用户个人排名
    ↓
构建排行榜消息
    ↓
返回给 Slack 显示
```

## 安全设计

### 1. 请求验证
- **签名验证**: 使用 HMAC-SHA256 验证 Slack 请求
- **时间戳检查**: 防止重放攻击（5分钟窗口）
- **来源验证**: 仅接受来自 Slack 的请求

### 2. 密钥管理
- **Secrets Manager**: 集中管理敏感信息
- **IAM 权限**: 最小权限原则
- **加密传输**: HTTPS/TLS 1.2+

### 3. 访问控制
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem", 
        "dynamodb:UpdateItem",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/QuizScores"
    },
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-*"
    },
    {
      "Effect": "Allow", 
      "Action": "secretsmanager:GetSecretValue",
      "Resource": [
        "arn:aws:secretsmanager:*:*:secret:slack/signing-secret*",
        "arn:aws:secretsmanager:*:*:secret:slack/bot-token*"
      ]
    }
  ]
}
```

## 性能优化

### 1. Lambda 优化
- **内存配置**: 256MB（平衡性能和成本）
- **超时设置**: 30秒（满足 Slack 3秒响应要求）
- **并发控制**: 默认 1000 并发
- **冷启动优化**: 保持函数温热

### 2. DynamoDB 优化
- **按需计费**: 适合不规律访问模式
- **GSI 设计**: 支持排行榜查询
- **数据建模**: 单表设计减少查询次数

### 3. API Gateway 优化
- **缓存**: 对静态响应启用缓存
- **压缩**: 启用 GZIP 压缩
- **限流**: 防止滥用

## 可扩展性设计

### 1. 水平扩展
- **Lambda**: 自动扩展到 1000+ 并发
- **DynamoDB**: 按需扩展读写容量
- **API Gateway**: 支持高并发请求

### 2. 功能扩展
- **主题分类**: 在 DynamoDB 中添加 topic 字段
- **每日挑战**: 添加 daily_challenge 表
- **团队竞赛**: 添加 team_scores 表
- **难度等级**: 题目分级存储

### 3. 多区域部署
```yaml
# 跨区域复制配置
GlobalTables:
  - TableName: QuizScores
    Replicas:
      - Region: us-east-1
      - Region: us-west-2
      - Region: eu-west-1
```

## 监控与告警

### 1. 关键指标
- **Lambda 调用次数**: 使用量监控
- **错误率**: 可用性监控  
- **响应时间**: 性能监控
- **DynamoDB 读写**: 容量监控

### 2. 告警设置
```yaml
Alarms:
  - Name: HighErrorRate
    Metric: AWS/Lambda/Errors
    Threshold: 5%
    Period: 5min
    
  - Name: HighLatency  
    Metric: AWS/Lambda/Duration
    Threshold: 10000ms
    Period: 5min
    
  - Name: DynamoDBThrottles
    Metric: AWS/DynamoDB/ThrottledRequests  
    Threshold: 1
    Period: 1min
```

### 3. 日志分析
- **结构化日志**: JSON 格式便于查询
- **错误追踪**: 详细错误堆栈
- **性能分析**: 关键操作耗时记录