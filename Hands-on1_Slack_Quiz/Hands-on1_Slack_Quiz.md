# Hands-on 1：构建 Amazon Q + Slack 互动云服务知识竞猜小游戏

## 概览
本实验将引导你使用 Amazon Q 的 Slack 集成快速打造一款 "AWS 云服务知识竞猜" 小游戏。用户在 Slack 中输入 `/awsquiz` Slash 命令后，Amazon Q 会自动生成多选题并提供按钮供答题；系统实时记录分数，并通过 Slack Bot 直接反馈给用户，互动及时。

## 目标
1. 体验 Amazon Q 在 Slack 中的问答与内容生成能力。
2. 学习如何将 Amazon Q 的输出与 Lambda、DynamoDB 等 AWS Serverless 服务结合，构建互动式应用。
3. 学习如何通过 Lambda + DynamoDB 实现一个简单的分数查询/排行榜功能。

## 架构
```
用户 ➜ Slack Slash Command (/awsquiz) ➜ Amazon Q Chat (Slack 集成) ➜ AWS Lambda (题目逻辑 & 分数计算) ➜ Amazon DynamoDB (分数存储)
                                                                                    ↘ Slack Message (返回结果与分数)
```

## 前置条件
- 拥有管理员权限的 AWS 账户，已在 AWS Region **us-east-1** 启用 Amazon Q (Preview)。
- 一个可安装自定义应用的 Slack Workspace，以及对应的管理员权限。
- 已安装及配置 **AWS CLI**、**SAM CLI** 与 **Node.js 18+** 或 **Python 3.10+**。

## 步骤
1. **启用 Amazon Q Slack 集成**  
   在 Amazon Q 控制台 > Integrations，选择 **Slack** 并按照向导完成 OAuth 安装，记下 **Signing Secret** 与 **Bot Token**。
2. **创建 Slash 命令 `/awsquiz`**  
   在 Slack App 配置中添加 Slash Command，Request URL 指向稍后部署的 API Gateway 端点，例如 `https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/quiz`。
3. **初始化 Serverless 项目**  
   ```bash
   sam init --runtime python3.10 --name awsquiz
   cd awsquiz
   ```
4. **编写 Lambda 处理器** (`app.py`)：
   - 解析 Slash 命令 payload。
   - 调用 Amazon Q Chat API（`BedrockRuntime.invoke_model`）生成题目与选项。
   - 使用 Slack Block Kit 构造带按钮的消息并回应。
   - 处理互动回调，计算得分并写入 DynamoDB，然后调用 Slack API 将实时分数反馈给用户。
5. **配置 DynamoDB 表**  
   在 `template.yaml` 中声明 `QuizScores` 表，主键为 `user_id`；读取/写入容量模式选用 On-Demand 以降低成本。
6. **部署基础设施**  
   ```bash
   sam build && sam deploy --guided
   ```
7. **试玩与验证**  
   - 在 Slack 中输入 `/awsquiz`，答题并查看得分。
   - 答题并查看 Slack 是否收到了实时的分数反馈消息。
8. **扩展思路**  
   - 引入主题分类（EC2、S3、Serverless 等）。  
   - 增加 “每日挑战” 功能。  
   - 实现 `/leaderboard` Slash 命令：该命令触发 Lambda 查询 DynamoDB `QuizScores` 表中分数最高的前 5 名用户，并将结果格式化为文本消息发回 Slack 频道。
   - 将排行榜嵌入公司内网门户。
9. **清理资源**  
    ```bash
    sam delete
    ```
    > 注意: 如果 DynamoDB 表是在 `template.yaml` 中定义的，`sam delete` 会自动将其删除。如果表是手动创建的，则需要额外运行 `aws dynamodb delete-table --table-name QuizScores`。

## 费用预估
- Amazon Q Slack 集成：Preview 阶段免费（请关注正式发布后的定价）。  
- Lambda 与 API Gateway：< 1 USD/月（低调用量）。  
- DynamoDB On-Demand：≈ 0.6 USD/100 万写/读请求。  

## 参考资料
- Amazon Q 官方文档：<https://docs.aws.amazon.com/ja_jp/amazonq/>  
- Slack App 开发者指南：<https://api.slack.com/docs>  
- AWS Serverless Application Model：<https://docs.aws.amazon.com/serverless-application-model/> 