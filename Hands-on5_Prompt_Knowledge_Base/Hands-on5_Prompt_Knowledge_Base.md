# Hands-on 5：Prompt-Driven Development——构建自定义知识库并提升问答准确率

## 概览
本实验演示如何借助 Amazon Q Knowledge Bases 将企业政策文档存储在 S3 的 PDF/Markdown 转化为向量索引，随后通过 Q Chat 进行问答，以提升答案的专业性和准确率。

## 目标
1. 掌握创建 Amazon Q Knowledge Base 的流程。  
2. 学习使用 Prompt 调整检索范围、答案格式与置信度。  
3. 理解 RAG（Retrieval-Augmented Generation）在企业问答场景中的作用。

## 数据准备
- 将若干公司政策文档（PDF/MD）上传至 `s3://corp-policy-docs/raw/`。

## 前置条件
- AWS 账户 (us-east-1)，启用 Amazon Bedrock 与 Amazon OpenSearch Serverless。  
- 拥有 CreateRole 权限，便于知识库自动创建 IAM Role。  
- 已订阅 Amazon Q Preview。

## 步骤
1. **创建知识库**  
   - 打开 Amazon Q Console → **Knowledge Bases → Create**。  
   - 选择 **S3** 作为数据源，Bucket 指向 `corp-policy-docs/raw/`。  
   - 向量存储选择 **OpenSearch Serverless** 集群，维度 1536。  
   - 勾选 **Auto-sync**，Cron 每日 00:00 UTC。
2. **等待向量化完成**，状态变为 `Active` 后测试：
   在测试面板输入：
   > 公司远程办公政策适用于兼职员工吗？
3. **提示调优**  
   - 要求引用出处：`请在答案末尾附上文档标题与段落编号`。
   - 设置响应风格：`使用正式、简洁语气`。
4. **集成 Slack**  
   - 在 Q Console → Integrations 选择 **Slack**，将此知识库绑定到指定频道：`#policy-info`。
5. **监控与评估**  
   - 使用 Q Analytics 查看命中率、平均响应时间。  
   - 调整 `Top-K` 或重新分段改善效果。
6. **清理资源**  
   - 删除 Knowledge Base 与 OpenSearch Collection。  
   - 清空 S3 Bucket。

## 成本预估
- Bedrock 模型调用：按真实调用量计费。  
- OpenSearch Vector 引擎：0.12 USD/vCPU-Hour + 存储费。  
- S3 存储：0.023 USD/GB/月。

## 参考资料
- Amazon Q Knowledge Bases 用户指南：<https://docs.aws.amazon.com/amazonq/latest/userguide/knowledge-bases.html>  
- RAG 设计模式：<https://aws.amazon.com/blogs/machine-learning/> 