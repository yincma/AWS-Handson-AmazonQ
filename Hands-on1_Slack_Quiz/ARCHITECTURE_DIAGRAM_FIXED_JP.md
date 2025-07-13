# Amazon Q + Slack クイズアプリケーション アーキテクチャ図

## システム全体アーキテクチャ

```mermaid
graph TB
    classDef slackStyle fill:#4A154B,stroke:#4A154B,stroke-width:2px,color:#fff
    classDef awsService fill:#FF9900,stroke:#FF9900,stroke-width:2px,color:#fff
    classDef database fill:#3F48CC,stroke:#3F48CC,stroke-width:2px,color:#fff
    classDef security fill:#DD344C,stroke:#DD344C,stroke-width:2px,color:#fff
    classDef ai fill:#01A88D,stroke:#01A88D,stroke-width:2px,color:#fff

    subgraph "Slack ワークスペース"
        SlackUser["Slackユーザー"]
        SlackApp["Slackアプリ"]
    end

    subgraph "AWS API Gateway"
        APIGateway["REST API Gateway"]
    end

    subgraph "AWS Lambda"
        LambdaFunction["Lambda関数 Python 3.10"]
    end

    subgraph "Amazon Bedrock"
        BedrockClaude["Claude 3 Haiku"]
    end

    subgraph "データストレージ"
        DynamoDB["DynamoDB テーブル"]
    end

    subgraph "セキュリティ管理"
        SecretsManager["Secrets Manager"]
    end

    subgraph "監視ログ"
        CloudWatch["CloudWatch"]
    end

    SlackUser --> SlackApp
    SlackApp -->|HTTPS POST| APIGateway
    APIGateway --> LambdaFunction
    
    LambdaFunction -->|署名検証| SecretsManager
    LambdaFunction -->|問題生成| BedrockClaude
    LambdaFunction -->|スコア保存| DynamoDB
    LambdaFunction -->|ログ出力| CloudWatch
    
    LambdaFunction -->|レスポンス| APIGateway
    APIGateway -->|JSON応答| SlackApp
    SlackApp --> SlackUser

    class SlackUser,SlackApp slackStyle
    class APIGateway,LambdaFunction awsService
    class DynamoDB database
    class SecretsManager security
    class BedrockClaude ai
    class CloudWatch awsService
```

## データフロー詳細図

```mermaid
sequenceDiagram
    participant U as Slackユーザー
    participant S as Slackアプリ
    participant A as API Gateway
    participant L as Lambda関数
    participant SM as Secrets Manager
    participant B as Bedrock Claude
    participant D as DynamoDB
    participant C as CloudWatch

    Note over U,C: awsquiz コマンド実行フロー

    U->>S: awsquiz コマンド入力
    S->>A: POST slack command
    A->>L: リクエスト転送
    
    L->>SM: 署名シークレット取得
    SM-->>L: シークレット返却
    L->>L: 署名検証実行
    
    alt 署名検証成功
        L->>B: クイズ問題生成リクエスト
        B-->>L: 問題選択肢解答返却
        L->>L: Block Kit UI構築
        L-->>A: クイズ表示レスポンス
        A-->>S: JSON応答
        S-->>U: クイズ問題表示
        
        U->>S: 答えボタンクリック
        S->>A: POST slack interaction
        A->>L: インタラクション処理
        
        L->>D: ユーザースコア更新
        D-->>L: 更新結果返却
        L->>L: 結果メッセージ構築
        L-->>A: 結果表示レスポンス
        A-->>S: JSON応答
        S-->>U: 正解不正解スコア表示
        
    else 署名検証失敗
        L-->>A: 401 Unauthorized
        A-->>S: エラー応答
    end
    
    L->>C: ログ記録
    Note over L,C: 全ての処理でログ出力
```

## セキュリティアーキテクチャ図

```mermaid
graph TB
    subgraph "セキュリティ層"
        subgraph "ネットワークセキュリティ"
            HTTPS["HTTPS TLS暗号化通信"]
            WAF["AWS WAF"]
        end
        
        subgraph "アプリケーションセキュリティ"
            SigVerify["署名検証 HMAC-SHA256"]
            TimeCheck["タイムスタンプ検証"]
            InputValid["入力検証"]
        end
        
        subgraph "データセキュリティ"
            Encryption["暗号化"]
            KMS["AWS KMS"]
        end
        
        subgraph "アクセス制御"
            IAM["IAM ロール"]
            SecretsMgr["Secrets Manager"]
        end
    end

    subgraph "監査コンプライアンス"
        CloudTrail["CloudTrail API記録"]
        AuditLog["監査ログ"]
        GDPR["GDPR対応"]
    end

    HTTPS --> SigVerify
    SigVerify --> TimeCheck
    TimeCheck --> InputValid
    InputValid --> Encryption
    Encryption --> KMS
    IAM --> SecretsMgr
    
    CloudTrail --> AuditLog
    AuditLog --> GDPR
```

## コスト最適化アーキテクチャ

```mermaid
graph TB
    subgraph "コスト最適化戦略"
        subgraph "Bedrock最適化"
            Cache["問題キャッシュ"]
            Batch["バッチ生成"]
        end
        
        subgraph "Lambda最適化"
            Memory["メモリ調整"]
            Timeout["タイムアウト"]
            Concurrent["同時実行制御"]
        end
        
        subgraph "DynamoDB最適化"
            OnDemand["オンデマンド課金"]
            TTL["TTL設定"]
        end
        
        subgraph "Secrets Manager最適化"
            SecretCache["シークレットキャッシュ"]
        end
    end

    subgraph "コスト監視"
        Budget["予算アラート"]
        Anomaly["異常検出"]
        Metrics["使用量メトリクス"]
    end

    Cache --> Budget
    Batch --> Budget
    SecretCache --> Anomaly
    OnDemand --> Metrics
```

## 拡張機能アーキテクチャ

```mermaid
graph TB
    subgraph "基本機能"
        BasicQuiz["基本クイズ"]
        BasicScore["基本スコア"]
        BasicRanking["基本ランキング"]
    end

    subgraph "拡張機能レベル1"
        TopicSystem["トピック分類"]
        DailyChallenge["毎日チャレンジ"]
    end

    subgraph "拡張機能レベル2"
        TeamCompetition["チーム競争"]
        DifficultyLevel["難易度レベル"]
    end

    subgraph "拡張機能レベル3"
        Achievement["実績システム"]
        LearningPath["学習パス"]
    end

    subgraph "追加データストア"
        TopicTable["トピック統計テーブル"]
        ChallengeTable["毎日チャレンジテーブル"]
        TeamTable["チームテーブル"]
        AchievementTable["実績テーブル"]
    end

    BasicQuiz --> TopicSystem
    BasicScore --> DailyChallenge
    BasicRanking --> TeamCompetition
    
    TopicSystem --> DifficultyLevel
    DailyChallenge --> Achievement
    TeamCompetition --> LearningPath
    
    TopicSystem --> TopicTable
    DailyChallenge --> ChallengeTable
    TeamCompetition --> TeamTable
    Achievement --> AchievementTable
```

## AWS公式アイコン使用ガイド

### 使用したAWSサービスアイコン
- **Amazon API Gateway**: REST APIエンドポイント
- **AWS Lambda**: サーバーレス関数実行
- **Amazon DynamoDB**: NoSQLデータベース
- **Amazon Bedrock**: 生成AI機械学習
- **AWS Secrets Manager**: 認証情報管理
- **Amazon CloudWatch**: 監視ログ記録
- **AWS KMS**: 暗号化キー管理
- **AWS WAF**: Webアプリケーションファイアウォール
- **AWS CloudTrail**: API監査ログ

### アーキテクチャ図の特徴
1. **日本語ラベル**: すべてのコンポーネントが日本語で説明
2. **視覚的階層**: 機能別にグループ化された明確な構造
3. **データフロー**: 矢印で示された明確な処理の流れ
4. **セキュリティ重視**: セキュリティ層が明確に分離
5. **拡張性**: 将来の機能拡張を考慮した設計

この架構図は、AWS Well-Architected Frameworkの5つの柱（運用性、セキュリティ、信頼性、パフォーマンス効率、コスト最適化）に基づいて設計されています。