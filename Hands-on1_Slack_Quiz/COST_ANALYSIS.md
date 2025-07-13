# コスト分析と最適化

## 月間コスト予測

### 基本前提
- **アクティブユーザー**: 100人
- **日常使用**: 1人あたり平均 5 回のクイズ
- **月間総呼び出し**: 100 × 5 × 30 = 15,000 回
- **平均レスポンス時間**: 2秒
- **データストレージ**: 100 ユーザーレコード

### 詳細コスト分解

#### 1. AWS Lambda
```
呼び出し回数: 15,000 回/月
実行時間: 15,000 × 2秒 = 30,000 GB-秒
メモリ設定: 256MB (0.25GB)

コスト計算:
- リクエスト料金: 15,000 × $0.0000002 = $0.003
- コンピュート料金: 30,000 × $0.0000166667 = $0.50
- 月間小計: $0.503
```

#### 2. Amazon API Gateway
```
API 呼び出し: 15,000 回/月
データ転送: 15,000 × 2KB = 30MB

コスト計算:
- API 呼び出し料金: 15,000 × $0.0000035 = $0.053
- データ転送料金: 30MB × $0.09/GB = $0.003
- 月間小計: $0.056
```

#### 3. Amazon DynamoDB
```
保存データ: 100 ユーザー × 1KB = 100KB ≈ 0.0001GB
読み取り操作: 15,000 回 (強整合性読み取り)
書き込み操作: 15,000 回

コスト計算:
- ストレージ料金: 0.0001GB × $0.25 = $0.000025
- 読み取り料金: 15,000 × $0.000000125 = $0.0019
- 書き込み料金: 15,000 × $0.000000625 = $0.0094
- 月間小計: $0.011
```

#### 4. Amazon Bedrock (Claude 3 Haiku)
```
入力トークン: 15,000 × 200 = 3,000,000 トークン
出力トークン: 15,000 × 300 = 4,500,000 トークン

コスト計算:
- 入力料金: 3M × $0.00025/1K = $0.75
- 出力料金: 4.5M × $0.00125/1K = $5.625
- 月間小計: $6.375
```

#### 5. AWS Secrets Manager
```
シークレット数: 2個 (Signing Secret + Bot Token)
API 呼び出し: 15,000 回 (Lambda 呼び出しごと)

コスト計算:
- シークレット保存: 2 × $0.40 = $0.80
- API 呼び出し: 15,000 × $0.05/10,000 = $0.075
- 月間小計: $0.875
```

#### 6. CloudWatch Logs
```
ログデータ: 15,000 × 1KB = 15MB
保存期間: 7日

コスト計算:
- ログ取り込み: 15MB × $0.50/GB = $0.0075
- ログ保存: 15MB × 7日 × $0.03/GB/月 = $0.0001
- 月間小計: $0.008
```

### 総コスト集計

| サービス | 月間コスト | 割合 |
|------|----------|------|
| Amazon Bedrock | $6.375 | 82.1% |
| AWS Secrets Manager | $0.875 | 11.3% |
| AWS Lambda | $0.503 | 6.5% |
| Amazon API Gateway | $0.056 | 0.7% |
| Amazon DynamoDB | $0.011 | 0.1% |
| CloudWatch Logs | $0.008 | 0.1% |
| **合計** | **$7.828** | **100%** |

## コスト最適化戦略

### 1. Bedrock コスト最適化 (最大節約ポテンシャル)

#### 戦略 A: 問題キャッシュ
```python
# 問題キャッシュを実装し、Bedrock 呼び出しを削減
QUESTION_CACHE = []
CACHE_SIZE = 50

def get_cached_question():
    if len(QUESTION_CACHE) < 10:
        # 問題をバッチ生成
        questions = generate_batch_questions(10)
        QUESTION_CACHE.extend(questions)
    
    return QUESTION_CACHE.pop()

# 予想節約: 70% Bedrock コスト = $4.46/月
```

#### 戦略 B: 事前生成問題バンク
```yaml
# EventBridge を使用して定期的に問題バンクを生成
QuestionGeneratorSchedule:
  Type: AWS::Events::Rule
  Properties:
    ScheduleExpression: "rate(1 hour)"
    Targets:
      - Arn: !GetAtt QuestionGeneratorFunction.Arn

# 予想節約: 80% Bedrock コスト = $5.10/月
```

### 2. Secrets Manager 最適化

#### 戦略: Lambda 環境変数キャッシュ
```python
import os
from functools import lru_cache

@lru_cache(maxsize=2)
def get_cached_secret(secret_arn):
    # シークレットをキャッシュし、API 呼び出しを削減
    return secrets_client.get_secret_value(SecretId=secret_arn)

# 予想節約: 90% API 呼び出し料金 = $0.068/月
```

### 3. Lambda 最適化

#### 戦略 A: メモリ調整
```yaml
# 異なるメモリ設定のコストパフォーマンステスト
MemoryConfigurations:
  - 128MB: 実行時間 3秒, コスト $0.75
  - 256MB: 実行時間 2秒, コスト $0.50  # 現在の設定
  - 512MB: 実行時間 1.5秒, コスト $0.75

# 現在の設定が最適、調整不要
```

#### 戦略 B: 予約済み同時実行
```yaml
# 安定した負荷に対して予約済み同時実行を使用
ReservedConcurrency: 10
ProvisionedConcurrency: 5

# 高頻度使用シナリオでのみ検討
```

### 4. DynamoDB 最適化

#### 戦略: データライフサイクル管理
```python
# TTL を設定して古いデータを自動クリーンアップ
table.update_item(
    Key={'user_id': user_id},
    UpdateExpression='SET #ttl = :ttl',
    ExpressionAttributeNames={'#ttl': 'ttl'},
    ExpressionAttributeValues={':ttl': int(time.time()) + 86400 * 365}  # 1年
)
```

## 最適化後コスト予測

### すべての最適化戦略実施後

| サービス | 元コスト | 最適化後 | 節約 |
|------|--------|--------|------|
| Amazon Bedrock | $6.375 | $1.275 | $5.10 |
| AWS Secrets Manager | $0.875 | $0.807 | $0.068 |
| AWS Lambda | $0.503 | $0.503 | $0 |
| その他サービス | $0.075 | $0.075 | $0 |
| **合計** | **$7.828** | **$2.66** | **$5.168** |

**最適化効果**: コスト 66% 削減、月間総コスト $2.66

## 異なる規模でのコスト予測

### 小規模 (50 ユーザー)
```
月間呼び出し: 7,500 回
予想コスト: $1.33/月
```

### 中規模 (500 ユーザー)  
```
月間呼び出し: 75,000 回
予想コスト: $13.30/月
```

### 大規模 (2000 ユーザー)
```
月間呼び出し: 300,000 回
予想コスト: $53.20/月
```

## コスト監視とアラート

### 1. コスト予算設定
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

### 2. コスト異常検出
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

### 3. リアルタイムコスト監視
```python
# Lambda 関数にコスト追跡を追加
import boto3

def track_bedrock_usage(input_tokens, output_tokens):
    cloudwatch = boto3.client('cloudwatch')
    
    # トークン使用量を記録
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

## コスト最適化ベストプラクティス

### 1. 定期的な見直し
- **月次コスト分析**: コスト増加傾向の特定
- **サービス使用最適化**: 設定パラメータの調整
- **機能使用統計**: 低使用率機能の削除

### 2. 自動化最適化
- **自動スケーリング**: 負荷に応じたリソース調整
- **スケジュールタスク**: バッチ処理によるコスト削減
- **キャッシュ戦略**: 重複計算の削減

### 3. コスト配分
```yaml
# タグを使用したコスト配分
Tags:
  - Key: Project
    Value: SlackQuiz
  - Key: Environment  
    Value: Production
  - Key: CostCenter
    Value: Engineering
```

### 4. 代替案評価
- **オープンソースモデル**: 自己ホスト型モデルで推論コスト削減を検討
- **事前訓練問題バンク**: リアルタイム生成需要の削減
- **キャッシュ層**: Redis/ElastiCache でホットデータをキャッシュ

これらの最適化戦略を実施することで、月間コストを $7.83 から $2.66 に削減し、システムパフォーマンスとユーザーエクスペリエンスを維持できます。