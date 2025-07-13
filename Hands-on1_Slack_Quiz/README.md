# Amazon Q + Slack インタラクティブクラウドサービス知識クイズ

## プロジェクト概要
AWS Serverless アーキテクチャベースの Slack アプリケーション。AWS クラウドサービス知識クイズ機能を提供します。

## 機能特性
- `/awsquiz` - AWS クラウドサービス多択問題生成
- `/leaderboard` - ランキング表示と個人順位確認
- リアルタイムスコア統計とフィードバック
- トピック分類と毎日チャレンジ対応

## 技術スタック
- AWS Lambda (Python 3.10)
- Amazon API Gateway
- Amazon DynamoDB
- AWS Secrets Manager
- Amazon Bedrock
- AWS SAM

## ディレクトリ構造
```
slack-aws-quiz/
├── template.yaml           # SAM テンプレート
├── app.py                 # Lambda ハンドラー
├── requirements.txt       # Python 依存関係
├── samconfig.toml        # SAM 設定
├── events/               # テストイベント
│   ├── quiz_event.json
│   └── leaderboard_event.json
├── tests/                # 単体テスト
│   └── test_app.py
└── README.md
```

## デプロイ要件
- AWS CLI 設定
- SAM CLI インストール
- Python 3.10
- Slack アプリケーション設定