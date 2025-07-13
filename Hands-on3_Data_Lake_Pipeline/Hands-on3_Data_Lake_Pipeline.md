# Hands-on 3：利用 Amazon Q 自动搭建数据湖与交互式分析管道

## 概览
本实验展示如何使用 Amazon Q 一键生成并部署数据湖基础设施，包含 S3 分区区层、Glue Crawler、ETL Lambda 以及 Athena + QuickSight 的可视化分析管道。

## 目标
1. 体验 Amazon Q 生成 CloudFormation/SAM/CDK 代码的能力。  
2. 搭建标准 "Landing ➜ Raw ➜ Clean" 数据湖分区结构。  
3. 使用 Athena 对清洗后的数据进行交互式分析，并在 QuickSight 中制作 KPI Dashboard。

## 架构
```
数据源 (CSV/JSON) ➜ S3 Landing Bucket
                Lambda (清洗、转换) ➜ S3 Raw
                                     ➜ Glue Crawler (自动建表) ➜ Athena 查询
Athena 结果 ➜ QuickSight Dashboard
```

## 前置条件
- AWS 账户（us-east-1）并已授予 Lake Formation & Glue 权限。
- 本地安装 AWS CLI、CDK v2、Amazon Q Plugin (VS Code 或 AWS Console 内)。
- 准备示例数据集（如电商订单明细 CSV）。

## 步骤
1. **让 Amazon Q 生成 CDK 项目**  
   在 Amazon Q Chat 中输入：
   > 帮我用 TypeScript CDK 建立一个名为 `DataLakeStack` 的项目，包含 Landing/Raw/Clean 三层 S3，Glue Crawler 及 ETL Lambda。

   Q 输出 `cdk.json`、`lib/DataLakeStack.ts` 等文件。
2. **本地拉取并安装依赖**  
   ```bash
   git clone <Q 生成的 repo>
   cd data-lake
   npm install
   ```
3. **部署基础设施**  
   ```bash
   cdk deploy
   ```
4. **上传示例数据**  
   ```bash
   aws s3 cp sample_orders.csv s3://<landing-bucket>/2024/01/01/
   ```
5. **Glue Crawler 建表**  
   Crawler 周期性扫描 `s3://<raw-bucket>`，自动生成 `orders_raw` 表。
6. **Athena 分析**  
   示例查询：
   ```sql
   SELECT customer_id, SUM(total_amount) AS revenue
   FROM orders_clean
   WHERE order_date BETWEEN DATE '2024-01-01' AND DATE '2024-01-31'
   GROUP BY customer_id
   ORDER BY revenue DESC
   LIMIT 10;
   ```
7. **QuickSight Dashboard**  
   - 在 QuickSight 新建 Dataset，选择 Athena `orders_clean`。  
   - 创建收入 Top10 可视化及趋势图。  
   - 与团队分享 Dashboard 链接。
8. **扩展**  
   - 使用 Amazon EventBridge + Step Functions 取代 Lambda 清洗流程。  
   - 引入数据版本控制 (LakeFS)。
9. **清理资源**  
   ```bash
   cdk destroy
   aws quicksight delete-dashboard --dashboard-id DataLakeKPI
   ```

## 费用预估
- S3 存储：0.023 USD/GB/月。  
- Glue Crawler：0.44 USD/CUH。  
- Athena 查询：5 USD/TB 扫描。  
- QuickSight：同 Hands-on 1。

## 参考资料
- AWS Lake House Reference：<https://aws.amazon.com/architecture/lake-house/>  
- AWS CDK 文档：<https://docs.aws.amazon.com/cdk/v2/guide/> 