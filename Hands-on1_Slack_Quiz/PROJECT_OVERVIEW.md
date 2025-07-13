# Amazon Q + Slack インタラクティブクラウドサービス知識クイズ - プロジェクト概要

## 🎯 プロジェクト紹介

これは AWS Serverless アーキテクチャベースの Slack アプリケーションで、Amazon Q (Bedrock) を通じて AWS クラウドサービス知識クイズ問題を生成し、チームに楽しい学習とインタラクション体験を提供します。

## 📋 コア機能

### ✅ 実装済み機能
- **`/awsquiz`** - AWS クラウドサービス多択問題生成（4択1）
- **インテリジェント問題生成** - Amazon Bedrock Claude 3 Haiku モデル使用
- **リアルタイムフィードバック** - 回答クリック後即座に正解/不正解と解説を表示
- **スコア統計** - ユーザーの回答スコアと正解率を自動記録
- **`/leaderboard`** - トップ5ランキングと個人順位表示
- **セキュリティ検証** - Slack リクエスト署名検証とリプレイ攻撃防止

### 🔄 拡張機能（オプション）
- **トピック分類** - EC2、S3、Lambda などサービス分類問題
- **毎日チャレンジ** - 毎日特色問題と連続チャレンジ報酬
- **チーム競争** - チーム作成、参加、チームランキング
- **難易度レベル** - 初級からエキスパート級まで適応的難易度調整
- **実績システム** - バッジ報酬と学習マイルストーン
- **学習パス** - 個人化学習提案と進捗追跡

## 🏗️ 技術アーキテクチャ

```
Slack Client → API Gateway → Lambda → Bedrock (問題生成)
                                  ↓
                              DynamoDB (スコア保存)
                                  ↓
                           Secrets Manager (キー管理)
```

### コアコンポーネント
- **AWS Lambda** (Python 3.10) - メインビジネスロジック処理
- **Amazon API Gateway** - REST API エンドポイントとリクエストルーティング
- **Amazon DynamoDB** - ユーザースコアと統計データ保存
- **Amazon Bedrock** - Claude 3 Haiku モデル問題生成
- **AWS Secrets Manager** - Slack キーセキュア保存
- **Amazon CloudWatch** - ログ記録と監視

## 📊 コスト分析

### 月間コスト予測（100ユーザー、15,000回呼び出し）

| サービス | 月間コスト | 割合 |
|------|----------|------|
| Amazon Bedrock | $6.375 | 82.1% |
| AWS Secrets Manager | $0.875 | 11.3% |
| AWS Lambda | $0.503 | 6.5% |
| Amazon API Gateway | $0.056 | 0.7% |
| Amazon DynamoDB | $0.011 | 0.1% |
| CloudWatch Logs | $0.008 | 0.1% |
| **合計** | **$7.83** | **100%** |

### 最適化後コスト
問題キャッシュとキーキャッシュ最適化により、**$2.66/月**まで削減可能（66%節約）

## 🔒 セキュリティ特性

- **リクエスト検証** - HMAC-SHA256 署名検証
- **リプレイ攻撃防止** - 5分間タイムスタンプウィンドウチェック
- **キー管理** - AWS Secrets Manager 集中管理
- **データ暗号化** - 転送時および保存時全過程暗号化
- **最小権限** - IAM ロール最小権限原則遵守
- **入力検証** - 厳格なユーザー入力検証とクリーニング
- **監査ログ** - 完全な操作監査記録

## 📁 プロジェクト構造

```
slack-aws-quiz/
├── README.md                 # プロジェクト説明
├── template.yaml            # SAM デプロイテンプレート
├── app.py                   # Lambda メインハンドラー
├── requirements.txt         # Python 依存関係
├── samconfig.toml          # SAM 設定
├── events/                 # テストイベント
│   ├── quiz_event.json
│   └── leaderboard_event.json
├── docs/                   # ドキュメントディレクトリ
│   ├── DEPLOYMENT.md       # デプロイガイド
│   ├── ARCHITECTURE.md     # アーキテクチャ設計
│   ├── COST_ANALYSIS.md    # コスト分析
│   ├── SECURITY.md         # セキュリティベストプラクティス
│   └── EXTENSIONS.md       # 機能拡張
└── tests/                  # 単体テスト
    └── test_app.py
```

## 🚀 クイックスタート

### 1. 前提条件
- AWS CLI 設定済み
- SAM CLI インストール済み
- Python 3.10+
- Slack ワークスペース管理者権限

### 2. デプロイ手順
```bash
# 1. プロジェクトクローン
git clone <repository-url>
cd slack-aws-quiz

# 2. Secrets Manager 設定
aws secretsmanager create-secret \
    --name "slack/signing-secret" \
    --secret-string "your_signing_secret"

aws secretsmanager create-secret \
    --name "slack/bot-token" \
    --secret-string "xoxb-your-bot-token"

# 3. ビルドとデプロイ
sam build
sam deploy --guided

# 4. Slack アプリ設定
# - Slash Commands 作成: /awsquiz, /leaderboard
# - Interactive Components 設定
# - Request URLs 設定
```

### 3. デプロイ検証
```bash
# API エンドポイントテスト
curl -X POST https://your-api-url/prod/slack/command \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "command=/awsquiz&user_id=test_user"
```

## 📈 パフォーマンス指標

### 目標パフォーマンス
- **レスポンス時間** ≤ 2秒
- **可用性** ≥ 99.9%
- **並行サポート** 1000+ ユーザー
- **月間コスト** ≤ $5 USD（最適化後）

### 監視指標
- Lambda 呼び出し回数とエラー率
- API Gateway レスポンス時間
- DynamoDB 読み書き容量使用
- Bedrock モデル呼び出しコスト

## 🛠️ 開発とテスト

### ローカル開発
```bash
# ローカル API 起動
sam local start-api --port 3000

# ローカルテスト
sam local invoke SlackQuizFunction --event events/quiz_event.json

# リアルタイムログ
sam logs --stack-name slack-aws-quiz --tail
```

### 単体テスト
```bash
python -m pytest tests/ -v
```

## 📚 ドキュメント索引

| ドキュメント | 説明 |
|------|------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | 詳細デプロイガイドとトラブルシューティング |
| [ARCHITECTURE.md](ARCHITECTURE.md) | システムアーキテクチャと設計決定 |
| [COST_ANALYSIS.md](COST_ANALYSIS.md) | コスト分析と最適化戦略 |
| [SECURITY.md](SECURITY.md) | セキュリティベストプラクティスとコンプライアンス |
| [EXTENSIONS.md](EXTENSIONS.md) | 機能拡張とロードマップ |

## 🤝 貢献ガイド

1. プロジェクトをフォーク
2. 機能ブランチ作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Request を開く

## 📄 ライセンス

このプロジェクトは MIT ライセンスを採用 - 詳細は [LICENSE](LICENSE) ファイルを参照。

## 🆘 サポート

問題が発生した場合：
1. [DEPLOYMENT.md](DEPLOYMENT.md) のトラブルシューティング部分を確認
2. CloudWatch ログをチェック
3. GitHub Issue を提出

## 🎉 謝辞

- AWS Serverless チームの優秀なツール提供
- Slack API チームの詳細なドキュメント
- Amazon Bedrock チームの強力な AI 能力

---

**AWS 学習の旅を始めましょう！** 🚀