# 部署指南

## 前置要求

1. **AWS CLI 配置**
```bash
aws configure
# 输入 Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

2. **SAM CLI 安装**
```bash
# Windows (使用 Chocolatey)
choco install aws-sam-cli

# 或下载 MSI 安装包
# https://github.com/aws/aws-sam-cli/releases/latest
```

3. **Python 3.10 安装**
```bash
python --version  # 确认版本 >= 3.10
```

## Slack 应用配置

### 1. 创建 Slack 应用
1. 访问 https://api.slack.com/apps
2. 点击 "Create New App" → "From scratch"
3. 输入应用名称和选择工作区

### 2. 配置 Slash Commands
在 Slack 应用设置中：
1. 进入 "Slash Commands"
2. 创建 `/awsquiz` 命令
   - Request URL: `https://your-api-gateway-url/prod/slack/command`
   - Short Description: "AWS 云服务知识竞猜"
3. 创建 `/leaderboard` 命令
   - Request URL: `https://your-api-gateway-url/prod/slack/command`
   - Short Description: "查看排行榜"

### 3. 配置 Interactive Components
1. 进入 "Interactivity & Shortcuts"
2. 启用 Interactivity
3. Request URL: `https://your-api-gateway-url/prod/slack/interaction`

### 4. 获取密钥
- **Signing Secret**: 在 "Basic Information" → "App Credentials"
- **Bot Token**: 在 "OAuth & Permissions" → "Bot User OAuth Token"

## AWS Secrets Manager 配置

### 1. 存储 Slack Signing Secret
```bash
aws secretsmanager create-secret \
    --name "slack/signing-secret" \
    --description "Slack App Signing Secret" \
    --secret-string "your_signing_secret_here"
```

### 2. 存储 Slack Bot Token
```bash
aws secretsmanager create-secret \
    --name "slack/bot-token" \
    --description "Slack Bot OAuth Token" \
    --secret-string "xoxb-your-bot-token-here"
```

## 本地开发与测试

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 本地测试
```bash
# 构建应用
sam build

# 本地启动 API
sam local start-api --port 3000

# 测试 quiz 命令
sam local invoke SlackQuizFunction --event events/quiz_event.json

# 测试 leaderboard 命令  
sam local invoke SlackQuizFunction --event events/leaderboard_event.json
```

### 3. 本地调试
```bash
# 启动调试模式
sam local start-api --debug-port 5858 --port 3000

# 使用 VS Code 或其他 IDE 连接调试端口
```

## 生产部署

### 1. 首次部署
```bash
# 构建应用
sam build

# 引导式部署（首次）
sam deploy --guided
```

部署过程中会提示输入：
- Stack Name: `slack-aws-quiz`
- AWS Region: `us-east-1`
- Parameter SlackSigningSecret: `arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:slack/signing-secret`
- Parameter SlackBotToken: `arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT:secret:slack/bot-token`
- Confirm changes before deploy: `Y`
- Allow SAM CLI IAM role creation: `Y`
- Save parameters to samconfig.toml: `Y`

### 2. 后续部署
```bash
sam build && sam deploy
```

### 3. 获取 API 端点
```bash
aws cloudformation describe-stacks \
    --stack-name slack-aws-quiz \
    --query 'Stacks[0].Outputs[?OutputKey==`SlackQuizApi`].OutputValue' \
    --output text
```

## 验证部署

### 1. 检查 Lambda 函数
```bash
aws lambda list-functions --query 'Functions[?contains(FunctionName, `slack-aws-quiz`)]'
```

### 2. 检查 DynamoDB 表
```bash
aws dynamodb describe-table --table-name QuizScores
```

### 3. 测试 API 端点
```bash
curl -X POST https://your-api-gateway-url/prod/slack/command \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "command=/awsquiz&user_id=test_user"
```

## 监控与日志

### 1. CloudWatch 日志
```bash
# 查看 Lambda 日志
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/slack-aws-quiz"

# 实时查看日志
sam logs --stack-name slack-aws-quiz --tail
```

### 2. 设置告警
```bash
# 创建错误率告警
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

## 故障排除

### 常见问题

1. **签名验证失败**
   - 检查 Secrets Manager 中的 Signing Secret
   - 确认时间戳在 5 分钟内

2. **Bedrock 调用失败**
   - 确认 us-east-1 区域已启用 Claude 模型
   - 检查 IAM 权限

3. **DynamoDB 写入失败**
   - 检查表名环境变量
   - 验证 IAM 权限

4. **Slack 命令无响应**
   - 检查 API Gateway 端点 URL
   - 验证 Slack 应用配置

### 日志分析
```bash
# 过滤错误日志
aws logs filter-log-events \
    --log-group-name "/aws/lambda/slack-aws-quiz-SlackQuizFunction" \
    --filter-pattern "ERROR"

# 查看最近的调用
aws logs filter-log-events \
    --log-group-name "/aws/lambda/slack-aws-quiz-SlackQuizFunction" \
    --start-time $(date -d '1 hour ago' +%s)000
```