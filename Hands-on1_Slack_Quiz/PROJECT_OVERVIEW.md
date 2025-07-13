# Amazon Q + Slack 互动云服务知识竞猜 - 项目总览

## 🎯 项目简介

这是一个基于 AWS Serverless 架构的 Slack 应用，通过 Amazon Q (Bedrock) 生成 AWS 云服务知识竞猜题目，为团队提供有趣的学习和互动体验。

## 📋 核心功能

### ✅ 已实现功能
- **`/awsquiz`** - 生成 AWS 云服务多选题（4选1）
- **智能题目生成** - 使用 Amazon Bedrock Claude 3 Haiku 模型
- **实时反馈** - 点击答案后立即显示正确/错误及解释
- **分数统计** - 自动记录用户答题分数和正确率
- **`/leaderboard`** - 显示前5名排行榜和个人排名
- **安全验证** - Slack 请求签名验证和防重放攻击

### 🔄 扩展功能（可选）
- **主题分类** - EC2、S3、Lambda 等服务分类题目
- **每日挑战** - 每日特色题目和连续挑战奖励
- **团队竞赛** - 团队创建、加入和团队排行榜
- **难度等级** - 初级到专家级自适应难度调整
- **成就系统** - 徽章奖励和学习里程碑
- **学习路径** - 个性化学习建议和进度跟踪

## 🏗️ 技术架构

```
Slack Client → API Gateway → Lambda → Bedrock (题目生成)
                                  ↓
                              DynamoDB (分数存储)
                                  ↓
                           Secrets Manager (密钥管理)
```

### 核心组件
- **AWS Lambda** (Python 3.10) - 主要业务逻辑处理
- **Amazon API Gateway** - REST API 端点和请求路由
- **Amazon DynamoDB** - 用户分数和统计数据存储
- **Amazon Bedrock** - Claude 3 Haiku 模型生成题目
- **AWS Secrets Manager** - Slack 密钥安全存储
- **Amazon CloudWatch** - 日志记录和监控

## 📊 成本分析

### 月度成本预估（100用户，15,000次调用）

| 服务 | 月度成本 | 占比 |
|------|----------|------|
| Amazon Bedrock | $6.375 | 82.1% |
| AWS Secrets Manager | $0.875 | 11.3% |
| AWS Lambda | $0.503 | 6.5% |
| Amazon API Gateway | $0.056 | 0.7% |
| Amazon DynamoDB | $0.011 | 0.1% |
| CloudWatch Logs | $0.008 | 0.1% |
| **总计** | **$7.83** | **100%** |

### 优化后成本
通过题库缓存和密钥缓存优化，可降低至 **$2.66/月**（节省66%）

## 🔒 安全特性

- **请求验证** - HMAC-SHA256 签名验证
- **防重放攻击** - 5分钟时间戳窗口检查
- **密钥管理** - AWS Secrets Manager 集中管理
- **数据加密** - 传输和存储全程加密
- **最小权限** - IAM 角色遵循最小权限原则
- **输入验证** - 严格的用户输入验证和清理
- **审计日志** - 完整的操作审计记录

## 📁 项目结构

```
slack-aws-quiz/
├── README.md                 # 项目说明
├── template.yaml            # SAM 部署模板
├── app.py                   # Lambda 主处理器
├── requirements.txt         # Python 依赖
├── samconfig.toml          # SAM 配置
├── events/                 # 测试事件
│   ├── quiz_event.json
│   └── leaderboard_event.json
├── docs/                   # 文档目录
│   ├── DEPLOYMENT.md       # 部署指南
│   ├── ARCHITECTURE.md     # 架构设计
│   ├── COST_ANALYSIS.md    # 成本分析
│   ├── SECURITY.md         # 安全最佳实践
│   └── EXTENSIONS.md       # 功能扩展
└── tests/                  # 单元测试
    └── test_app.py
```

## 🚀 快速开始

### 1. 前置要求
- AWS CLI 已配置
- SAM CLI 已安装
- Python 3.10+
- Slack 工作区管理员权限

### 2. 部署步骤
```bash
# 1. 克隆项目
git clone <repository-url>
cd slack-aws-quiz

# 2. 配置 Secrets Manager
aws secretsmanager create-secret \
    --name "slack/signing-secret" \
    --secret-string "your_signing_secret"

aws secretsmanager create-secret \
    --name "slack/bot-token" \
    --secret-string "xoxb-your-bot-token"

# 3. 构建和部署
sam build
sam deploy --guided

# 4. 配置 Slack 应用
# - 创建 Slash Commands: /awsquiz, /leaderboard
# - 设置 Interactive Components
# - 配置 Request URLs
```

### 3. 验证部署
```bash
# 测试 API 端点
curl -X POST https://your-api-url/prod/slack/command \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "command=/awsquiz&user_id=test_user"
```

## 📈 性能指标

### 目标性能
- **响应时间** ≤ 2秒
- **可用性** ≥ 99.9%
- **并发支持** 1000+ 用户
- **月度成本** ≤ $5 USD（优化后）

### 监控指标
- Lambda 调用次数和错误率
- API Gateway 响应时间
- DynamoDB 读写容量使用
- Bedrock 模型调用成本

## 🛠️ 开发和测试

### 本地开发
```bash
# 启动本地 API
sam local start-api --port 3000

# 本地测试
sam local invoke SlackQuizFunction --event events/quiz_event.json

# 实时日志
sam logs --stack-name slack-aws-quiz --tail
```

### 单元测试
```bash
python -m pytest tests/ -v
```

## 📚 文档索引

| 文档 | 描述 |
|------|------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | 详细部署指南和故障排除 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构和设计决策 |
| [COST_ANALYSIS.md](COST_ANALYSIS.md) | 成本分析和优化策略 |
| [SECURITY.md](SECURITY.md) | 安全最佳实践和合规性 |
| [EXTENSIONS.md](EXTENSIONS.md) | 功能扩展和路线图 |

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如遇问题，请：
1. 查看 [DEPLOYMENT.md](DEPLOYMENT.md) 故障排除部分
2. 检查 CloudWatch 日志
3. 提交 GitHub Issue

## 🎉 致谢

- AWS Serverless 团队提供的优秀工具
- Slack API 团队的详细文档
- Amazon Bedrock 团队的强大 AI 能力

---

**开始你的 AWS 学习之旅吧！** 🚀