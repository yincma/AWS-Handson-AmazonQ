# Hands-on 4：Prompt-Driven Development——编写高效数据查询提示实现商业洞察

## 概览
在本实验中，你将通过提示工程（Prompt Engineering）让 Amazon Q 自动生成 Amazon Athena SQL，以分析存储在 S3 的点击流数据并生成商业 KPI。无需编写 SQL，即可快速获取数据洞察。

## 目标
1. 学习如何设计高质量、结构化的 SQL 生成提示。  
2. 理解 Amazon Q 在 RAG 场景中处理数据上下文的机制。  
3. 使用 QuickSight 将查询结果可视化。

## 数据集
- S3 路径：`s3://clickstream-demo/2024/`  
- 数据格式：压缩 JSON，每行一个访问事件，包含 `user_id`、`page`、`event_time`、`device` 等字段。

## 前置条件
- 已启用 Athena + Glue Data Catalog。
- Amazon Q Chat 权限 (Preview)。

## 步骤
1. **为数据集创建 Glue 表**  
   ```bash
   aws glue create-database --database-name clickstream_demo
   aws glue start-crawler --name clickstream-crawler
   ```
2. **编写第一条 Prompt：DAU 计算**  
   在 Q Chat 输入：
   > 数据表 `clickstream_demo.events` 按天分区(event_date)，请写一条 Athena SQL 统计 2024-03-10 的 DAU。

   Q 返回类似：
   ```sql
   SELECT COUNT(DISTINCT user_id) AS dau
   FROM clickstream_demo.events
   WHERE event_date = DATE '2024-03-10';
   ```
3. **改进 Prompt 引导窗口函数**  
   > 进一步写 SQL 计算最近 7 天 rolling DAU，并按日期升序输出。

4. **执行并保存结果**  
   在 Athena 控制台运行 SQL，保存结果到 `clickstream-results` S3 存储桶。
5. **QuickSight 可视化**  
   - 新建 Dataset 指向结果 S3 清单。  
   - 创建折线图显示 DAU 走势。
6. **更多提示示例**  
   - 留存率、平均会话时长。  
   - 设备/地域分布。  
   - 用户漏斗分析。
7. **提示优化技巧**  
   - 明确输出格式：`仅返回 SQL，无解释`。  
   - 使用表/列注释提供业务上下文。  
   - 控制扫描数据量，例如 `LIMIT 1000` 或 `WHERE event_date BETWEEN...`。

## 清理资源
- 删除 Athena 查询结果存储桶。  
- 删除 Glue 表及数据库。

## 参考资料
- Prompt Engineering Best Practices：<https://github.com/aws-samples/amazon-q-prompts>  
- Amazon Athena SQL 参考：<https://docs.aws.amazon.com/athena/latest/ug/> 