# 成本分析与优化

## 月度成本预估

### 基础假设
- **活跃用户**: 100人
- **每日使用**: 每人平均 5 次答题
- **月度总调用**: 100 × 5 × 30 = 15,000 次
- **平均响应时间**: 2秒
- **数据存储**: 100 用户记录

### 详细成本分解

#### 1. AWS Lambda
```
调用次数: 15,000 次/月
执行时间: 15,000 × 2秒 = 30,000 GB-秒
内存配置: 256MB (0.25GB)

计算成本:
- 请求费用: 15,000 × $0.0000002 = $0.003
- 计算费用: 30,000 × $0.0000166667 = $0.50
- 月度小计: $0.503
```

#### 2. Amazon API Gateway
```
API 调用: 15,000 次/月
数据传输: 15,000 × 2KB = 30MB

计算成本:
- API 调用费: 15,000 × $0.0000035 = $0.053
- 数据传输费: 30MB × $0.09/GB = $0.003
- 月度小计: $0.056
```

#### 3. Amazon DynamoDB
```
存储数据: 100 用户 × 1KB = 100KB ≈ 0.0001GB
读取操作: 15,000 次 (强一致性读取)
写入操作: 15,000 次

计算成本:
- 存储费用: 0.0001GB × $0.25 = $0.000025
- 读取费用: 15,000 × $0.000000125 = $0.0019
- 写入费用: 15,000 × $0.000000625 = $0.0094
- 月度小计: $0.011
```

#### 4. Amazon Bedrock (Claude 3 Haiku)
```
输入 Token: 15,000 × 200 = 3,000,000 tokens
输出 Token: 15,000 × 300 = 4,500,000 tokens

计算成本:
- 输入费用: 3M × $0.00025/1K = $0.75
- 输出费用: 4.5M × $0.00125/1K = $5.625
- 月度小计: $6.375
```

#### 5. AWS Secrets Manager
```
密钥数量: 2个 (Signing Secret + Bot Token)
API 调用: 15,000 次 (每次 Lambda 调用)

计算成本:
- 密钥存储: 2 × $0.40 = $0.80
- API 调用: 15,000 × $0.05/10,000 = $0.075
- 月度小计: $0.875
```

#### 6. CloudWatch Logs
```
日志数据: 15,000 × 1KB = 15MB
存储期: 7天

计算成本:
- 日志摄取: 15MB × $0.50/GB = $0.0075
- 日志存储: 15MB × 7天 × $0.03/GB/月 = $0.0001
- 月度小计: $0.008
```

### 总成本汇总

| 服务 | 月度成本 | 占比 |
|------|----------|------|
| Amazon Bedrock | $6.375 | 82.1% |
| AWS Secrets Manager | $0.875 | 11.3% |
| AWS Lambda | $0.503 | 6.5% |
| Amazon API Gateway | $0.056 | 0.7% |
| Amazon DynamoDB | $0.011 | 0.1% |
| CloudWatch Logs | $0.008 | 0.1% |
| **总计** | **$7.828** | **100%** |

## 成本优化策略

### 1. Bedrock 成本优化 (最大节省潜力)

#### 策略 A: 题库缓存
```python
# 实现题库缓存，减少 Bedrock 调用
QUESTION_CACHE = []
CACHE_SIZE = 50

def get_cached_question():
    if len(QUESTION_CACHE) < 10:
        # 批量生成题目
        questions = generate_batch_questions(10)
        QUESTION_CACHE.extend(questions)
    
    return QUESTION_CACHE.pop()

# 预估节省: 70% Bedrock 成本 = $4.46/月
```

#### 策略 B: 预生成题库
```yaml
# 使用 EventBridge 定时生成题库
QuestionGeneratorSchedule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: "rate(1 hour)"
    Targets:
      - Arn: !GetAtt QuestionGeneratorFunction.Arn

# 预估节省: 80% Bedrock 成本 = $5.10/月
```

### 2. Secrets Manager 优化

#### 策略: Lambda 环境变量缓存
```python
import os
from functools import lru_cache

@lru_cache(maxsize=2)
def get_cached_secret(secret_arn):
    # 缓存密钥，减少 API 调用
    return secrets_client.get_secret_value(SecretId=secret_arn)

# 预估节省: 90% API 调用费 = $0.068/月
```

### 3. Lambda 优化

#### 策略 A: 内存调优
```yaml
# 测试不同内存配置的性价比
MemoryConfigurations:
  - 128MB: 执行时间 3s, 成本 $0.75
  - 256MB: 执行时间 2s, 成本 $0.50  # 当前配置
  - 512MB: 执行时间 1.5s, 成本 $0.75

# 当前配置最优，无需调整
```

#### 策略 B: 预留并发
```yaml
# 对于稳定负载，使用预留并发
ReservedConcurrency: 10
ProvisionedConcurrency: 5

# 仅在高频使用场景下考虑
```

### 4. DynamoDB 优化

#### 策略: 数据生命周期管理
```python
# 设置 TTL 自动清理旧数据
table.update_item(
    Key={'user_id': user_id},
    UpdateExpression='SET #ttl = :ttl',
    ExpressionAttributeNames={'#ttl': 'ttl'},
    ExpressionAttributeValues={':ttl': int(time.time()) + 86400 * 365}  # 1年
)
```

## 优化后成本预估

### 实施所有优化策略后

| 服务 | 原成本 | 优化后 | 节省 |
|------|--------|--------|------|
| Amazon Bedrock | $6.375 | $1.275 | $5.10 |
| AWS Secrets Manager | $0.875 | $0.807 | $0.068 |
| AWS Lambda | $0.503 | $0.503 | $0 |
| 其他服务 | $0.075 | $0.075 | $0 |
| **总计** | **$7.828** | **$2.66** | **$5.168** |

**优化效果**: 成本降低 66%，月度总成本 $2.66

## 不同规模成本预测

### 小规模 (50 用户)
```
月度调用: 7,500 次
预估成本: $1.33/月
```

### 中等规模 (500 用户)  
```
月度调用: 75,000 次
预估成本: $13.30/月
```

### 大规模 (2000 用户)
```
月度调用: 300,000 次
预估成本: $53.20/月
```

## 成本监控与告警

### 1. 成本预算设置
```yaml
CostBudget:
  Type: AWS::Budgets::Budget
  Properties:
    Budget:
      BudgetName: SlackQuizBudget
      BudgetLimit:
        Amount: 10
        Unit: USD
      TimeUnit: MONTHLY
      BudgetType: COST
    NotificationsWithSubscribers:
      - Notification:
          NotificationType: ACTUAL
          ComparisonOperator: GREATER_THAN
          Threshold: 80
        Subscribers:
          - SubscriptionType: EMAIL
            Address: admin@company.com
```

### 2. 成本异常检测
```yaml
CostAnomaly:
  Type: AWS::CE::AnomalyDetector
  Properties:
    AnomalyDetectorName: SlackQuizCostAnomaly
    MonitorType: DIMENSIONAL
    MonitorSpecification:
      DimensionKey: SERVICE
      MatchOptions:
        - EQUALS
      Values:
        - Amazon Bedrock
        - AWS Lambda
```

### 3. 实时成本监控
```python
# Lambda 函数中添加成本跟踪
import boto3

def track_bedrock_usage(input_tokens, output_tokens):
    cloudwatch = boto3.client('cloudwatch')
    
    # 记录 token 使用量
    cloudwatch.put_metric_data(
        Namespace='SlackQuiz/Cost',
        MetricData=[
            {
                'MetricName': 'BedrockInputTokens',
                'Value': input_tokens,
                'Unit': 'Count'
            },
            {
                'MetricName': 'BedrockOutputTokens', 
                'Value': output_tokens,
                'Unit': 'Count'
            }
        ]
    )
```

## 成本优化最佳实践

### 1. 定期审查
- **月度成本分析**: 识别成本增长趋势
- **服务使用优化**: 调整配置参数
- **功能使用统计**: 移除低使用率功能

### 2. 自动化优化
- **自动扩缩容**: 根据负载调整资源
- **定时任务**: 批量处理降低成本
- **缓存策略**: 减少重复计算

### 3. 成本分摊
```yaml
# 使用标签进行成本分摊
Tags:
  - Key: Project
    Value: SlackQuiz
  - Key: Environment  
    Value: Production
  - Key: CostCenter
    Value: Engineering
```

### 4. 替代方案评估
- **开源模型**: 考虑自托管模型降低推理成本
- **预训练题库**: 减少实时生成需求
- **缓存层**: Redis/ElastiCache 缓存热点数据

通过实施这些优化策略，可以将月度成本从 $7.83 降低到 $2.66，同时保持系统性能和用户体验。