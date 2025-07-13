# Hands-on 2：Amazon Q Code Assistant 打造实时情感分析可视化仪表盘

## 概览
本实验演示如何借助 Amazon Q Code Assistant 在 VS Code 中快速生成一套 Serverless 架构，实现对社交媒体流数据的实时情感分析，并将分析结果通过 Amplify Web App 实时可视化。

## 目标
1. 熟悉 Amazon Q Code Assistant 的代码生成、解释与重构能力。  
2. 学习使用 **Kinesis Data Streams + Lambda + Comprehend + Timestream** 实现实时数据处理流水线。  
3. 构建基于 **AWS Amplify** 的前端应用，实时展示情感分布图表。

## 架构
```
Twitter/Kafka ➜ Kinesis Data Streams ➜ Lambda (调用 Amazon Comprehend)
                                              ↘ Timestream (存储)
Timestream ➜ Amplify App (API Gateway + AppSync) ➜ 前端 React 图表
```

## 前置条件
- AWS 账户（us-east-1），已开启 Amazon Comprehend 与 Timestream。
- 本地安装 VS Code + Amazon Q 插件（Preview）。
- 已安装 AWS CLI、SAM CLI、Amplify CLI。
- 拥有可访问社交媒体流（可使用 Twitter API v2 或模拟器脚本）。

## 步骤
1. **在 VS Code 中初始化项目**  
   打开 VS Code → Amazon Q 面板，输入 `创建一个 Serverless 项目，用 Kinesis 处理推文并做情感分析`。Q 将生成:
   - `template.yaml` (SAM) 声明 Kinesis、Lambda、Timestream。  
   - `producer.py` 推文 Producer。  
   - `processor.py` Lambda 处理器。  
   - `amplify/` 前端骨架。
2. **审阅与调整代码**  
   使用 Q 解释关键片段，如 `processor.py` 中调用 `Comprehend.detectSentiment`。
3. **部署后端资源**  
   ```bash
   sam build && sam deploy --guided
   ```
4. **初始化 Amplify 应用**  
   ```bash
   amplify init
   amplify add api   # GraphQL/AppSync
   amplify add hosting
   amplify push
   ```
   Q 可自动生成 React 组件：`SentimentChart.jsx`（使用 `recharts`）。
5. **启动 Producer**  
   ```bash
   python producer.py --stream_name TwitterStream --bearer_token <TOKEN>
   ```
6. **实时查看可视化页面**  
   Amplify 部署完毕后自动弹出托管 URL，打开即可看到情感分布随时间动态刷新。
7. **扩展**  
   - 支持多语言情感分析。  
   - 新增热点关键字词云。  
   - 使用 CloudFront + Lambda@Edge 做全球加速。
8. **清理资源**  
   ```bash
   amplify delete
   sam delete
   aws timestream-write delete-database --database-name SentimentDB
   ```

## 费用预估
- Amazon Comprehend：0.0001 USD/文本块。  
- Kinesis & Timestream：取决于流量与存储，实验级别 < 5 USD。  
- Amplify Hosting：5 USD/GB/月 egress + 构建费用。

## 参考资料
- Amazon Q Code Assistant：<https://aws.amazon.com/amazonq/code/>  
- AWS Serverless Patterns Collection：<https://serverlessland.com/patterns/>  
- Amazon Timestream 入门：<https://docs.aws.amazon.com/timestream/latest/developerguide/> 