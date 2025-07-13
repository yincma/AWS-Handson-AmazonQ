# デプロイガイド

## 前提条件

1. **AWS CLI 設定**
```bash
aws configure
# Access Key ID, Secret Access Key, Region (us-east-1), Output format (json) を入力
```

2. **SAM CLI インストール**
```bash
# Windows (Chocolatey使用)
choco install aws-sam-cli

# または MSI インストールパッケージをダウンロード
# https://github.com/aws/aws-sam-cli/releases/latest
```

3. **Python 3.10 インストール**
```bash
python --version  # バージョン >= 3.10 を確認
```

## Slack アプリケーション設定

### 1. Slack アプリ作成
1. https://api.slack.com/apps にアクセス
2. "Create New App" → "From scratch" をクリック
3. アプリ名とワークスペースを入力

### 2. Slash Commands 設定
Slack アプリ設定で：
1. "Slash Commands" に移動
2. `/awsquiz` コマンド作成
   - Request URL: `https://your-api-gateway-url/prod/slack/command`
   - Short Description: "AWS クラウドサービス知識クイズ"
3. `/leaderboard` コマンド作成
   - Request URL: `https://your-api-gateway-url/prod/slack/command`
   - Short Description: "ランキング表示"

### 3. Interactive Components 設定
1. "Interactivity & Shortcuts" に移動
2. Interactivity を有効化
3. Request URL: `https://your-api-gateway-url/prod/slack/interaction`

### 4. 認証情報取得
- **Signing Secret**: "Basic Information" → "App Credentials" で確認
- **Bot Token**: "OAuth & Permissions" → "Bot User OAuth Token" で確認

## AWS Secrets Manager 設定

### 1. Slack Signing Secret を保存
```bash
aws secretsmanager create-secret \
    --name "slack/signing-secret" \
    --description "Slack App Signing Secret" \
    --secret-string "your_signing_secret_here"
```

### 2. Slack Bot Token を保存
```bash
aws secretsmanager create-secret \
    --name "slack/bot-token" \
    --description "Slack Bot OAuth Token" \
    --secret-string "xoxb-your-bot-token-here"
```

## ローカル開発とテスト

### 1. 依存関係インストール
```bash
pip install -r requirements.txt
```

### 2. ローカルテスト
```bash
# アプリケーションをビルド
sam build

# ローカル API を起動
sam local start-api --port 3000

# quiz コマンドをテスト
sam local invoke SlackQuizFunction --event events/quiz_event.json

# leaderboard コマンドをテスト  
sam local invoke SlackQuizFunction --event events/leaderboard_event.json
```

### 3. ローカルデバッグ
```bash
# デバッグモードで起動
sam local start-api --debug-port 5858 --port 3000

# VS Code または他の IDE でデバッグポートに接続
```

## 本番デプロイ

### 1. 初回デプロイ
```bash
# アプリケーションをビルド
sam build

# ガイド付きデプロイ（初回）
sam deploy --guided
```

デプロイ中に以下の入力が求められます：
- Stack Name: `slack-aws-quiz`
- AWS Region: `us-east-1`
- Parameter SlackSigningSecret: `arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:slack/signing-secret`
- Parameter SlackBotToken: `arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:slack/bot-token`
- Confirm changes before deploy: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Save parameters to samconfig.toml: `Y`

### 2. 後続デプロイ
```bash
sam build && sam deploy
```

### 3. API エンドポイント取得
```bash
aws cloudformation describe-stacks \
    --stack-name slack-aws-quiz \
    --query 'Stacks[0].Outputs[?OutputKey==`SlackQuizApi`].OutputValue' \
    --output text
```

## デプロイ検証

### 1. Lambda 関数確認
```bash
aws lambda list-functions --query 'Functions[?contains(FunctionName, `slack-aws-quiz`)]'
```

### 2. DynamoDB テーブル確認
```bash
aws dynamodb describe-table --table-name QuizScores
```

### 3. API エンドポイントテスト
```bash
curl -X POST https://your-api-gateway-url/prod/slack/command \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "command=/awsquiz&user_id=test_user"
```

## 監視とログ

### 1. CloudWatch ログ
```bash
# Lambda ログを確認
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/slack-aws-quiz"

# リアルタイムでログを確認
sam logs --stack-name slack-aws-quiz --tail
```

### 2. アラート設定
```bash
# エラー率アラートを作成
aws cloudwatch put-metric-alarm \
    --alarm-name "SlackQuiz-ErrorRate" \
    --alarm-description "Lambda error rate > 5%" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold
```

## トラブルシューティング

### よくある問題

1. **署名検証失敗**
   - Secrets Manager の Signing Secret を確認
   - タイムスタンプが 5 分以内であることを確認

2. **Bedrock 呼び出し失敗**
   - us-east-1 リージョンで Claude モデルが有効化されていることを確認
   - IAM 権限を確認

3. **DynamoDB 書き込み失敗**
   - テーブル名環境変数を確認
   - IAM 権限を検証

4. **Slack コマンド無応答**
   - API Gateway エンドポイント URL を確認
   - Slack アプリ設定を検証

### ログ分析
```bash
# エラーログをフィルタリング
aws logs filter-log-events \
    --log-group-name "/aws/lambda/slack-aws-quiz-SlackQuizFunction" \
    --filter-pattern "ERROR"

# 最近の呼び出しを確認
aws logs filter-log-events \
    --log-group-name "/aws/lambda/slack-aws-quiz-SlackQuizFunction" \
    --start-time $(date -d '1 hour ago' +%s)000
```