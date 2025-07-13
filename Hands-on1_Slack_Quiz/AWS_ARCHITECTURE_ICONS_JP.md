# AWS公式アイコンを使用したアーキテクチャ図作成ガイド

## AWS公式アイコンダウンロード

### 1. AWS Architecture Icons
**ダウンロードURL**: https://aws.amazon.com/jp/architecture/icons/

### 2. 使用するアイコン一覧

| サービス | アイコンファイル名 | 日本語名称 |
|---------|------------------|-----------|
| Amazon API Gateway | `Arch_Amazon-API-Gateway_64.png` | Amazon API Gateway |
| AWS Lambda | `Arch_AWS-Lambda_64.png` | AWS Lambda |
| Amazon DynamoDB | `Arch_Amazon-DynamoDB_64.png` | Amazon DynamoDB |
| Amazon Bedrock | `Arch_Amazon-Bedrock_64.png` | Amazon Bedrock |
| AWS Secrets Manager | `Arch_AWS-Secrets-Manager_64.png` | AWS Secrets Manager |
| Amazon CloudWatch | `Arch_Amazon-CloudWatch_64.png` | Amazon CloudWatch |
| AWS KMS | `Arch_AWS-Key-Management-Service_64.png` | AWS KMS |
| AWS WAF | `Arch_AWS-WAF_64.png` | AWS WAF |
| AWS CloudTrail | `Arch_AWS-CloudTrail_64.png` | AWS CloudTrail |

## PowerPoint用アーキテクチャ図テンプレート

### スライド1: システム全体概要
```
タイトル: Amazon Q + Slack クイズアプリケーション システムアーキテクチャ

レイアウト:
┌─────────────────────────────────────────────────────────────┐
│                    Slack ワークスペース                      │
│  [Slack Logo] ユーザー → [Slack App Icon] Slackアプリ        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS POST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   AWS クラウド環境                           │
│                                                             │
│  [API Gateway Icon] Amazon API Gateway                     │
│           │                                                 │
│           ▼                                                 │
│  [Lambda Icon] AWS Lambda (Python 3.10)                   │
│           │                                                 │
│           ├─── [Bedrock Icon] Amazon Bedrock (Claude)      │
│           │                                                 │
│           ├─── [DynamoDB Icon] Amazon DynamoDB             │
│           │                                                 │
│           └─── [Secrets Manager Icon] AWS Secrets Manager  │
│                                                             │
│  [CloudWatch Icon] Amazon CloudWatch (監視・ログ)           │
└─────────────────────────────────────────────────────────────┘
```

### スライド2: データフロー詳細
```
タイトル: データフロー詳細図

処理フロー:
1. [User Icon] Slackユーザー
   ↓ /awsquiz コマンド
2. [API Gateway Icon] API Gateway
   ↓ リクエスト転送
3. [Lambda Icon] Lambda関数
   ├─ [Secrets Manager Icon] 署名検証
   ├─ [Bedrock Icon] 問題生成
   └─ [DynamoDB Icon] スコア保存
   ↓ Block Kit応答
4. [Slack Icon] Slack表示
```

### スライド3: セキュリティアーキテクチャ
```
タイトル: セキュリティ設計

セキュリティ層:
┌─────────────────────────────────────────────────────────────┐
│                  ネットワークセキュリティ                    │
│  [WAF Icon] AWS WAF + [Shield Icon] HTTPS/TLS              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────────────┐
│                アプリケーションセキュリティ                  │
│  🔍 署名検証 + ⏰ タイムスタンプ検証                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────────────┐
│                    データセキュリティ                        │
│  [KMS Icon] AWS KMS + [Secrets Manager Icon] 認証情報管理   │
└─────────────────────────────────────────────────────────────┘
```

## Draw.io用XMLテンプレート

### 基本アーキテクチャ図XML
```xml
<mxfile host="app.diagrams.net">
  <diagram name="AWS-Slack-Quiz-Architecture">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        
        <!-- Slack Layer -->
        <mxCell id="slack-user" value="Slackユーザー" style="shape=actor;whiteSpace=wrap;html=1;" vertex="1" parent="1">
          <mxGeometry x="50" y="50" width="60" height="80"/>
        </mxCell>
        
        <mxCell id="slack-app" value="Slackアプリ" style="shape=image;html=1;verticalAlign=top;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;imageAspect=0;aspect=fixed;image=https://cdn.worldvectorlogo.com/logos/slack-new-logo.svg" vertex="1" parent="1">
          <mxGeometry x="200" y="60" width="60" height="60"/>
        </mxCell>
        
        <!-- AWS API Gateway -->
        <mxCell id="api-gateway" value="Amazon API Gateway&#xa;REST API" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#FF4F8B;gradientDirection=north;fillColor=#BC1356;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.api_gateway;" vertex="1" parent="1">
          <mxGeometry x="400" y="60" width="78" height="78"/>
        </mxCell>
        
        <!-- AWS Lambda -->
        <mxCell id="lambda" value="AWS Lambda&#xa;Python 3.10" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F78E04;gradientDirection=north;fillColor=#D05C17;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.lambda;" vertex="1" parent="1">
          <mxGeometry x="400" y="200" width="78" height="78"/>
        </mxCell>
        
        <!-- Amazon Bedrock -->
        <mxCell id="bedrock" value="Amazon Bedrock&#xa;Claude 3 Haiku" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#4AB29A;gradientDirection=north;fillColor=#116D5B;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.bedrock;" vertex="1" parent="1">
          <mxGeometry x="600" y="120" width="78" height="78"/>
        </mxCell>
        
        <!-- Amazon DynamoDB -->
        <mxCell id="dynamodb" value="Amazon DynamoDB&#xa;QuizScoresテーブル" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#4D72F3;gradientDirection=north;fillColor=#3334B9;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.dynamodb;" vertex="1" parent="1">
          <mxGeometry x="600" y="200" width="78" height="78"/>
        </mxCell>
        
        <!-- AWS Secrets Manager -->
        <mxCell id="secrets" value="AWS Secrets Manager&#xa;認証情報管理" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#C7131F;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.secrets_manager;" vertex="1" parent="1">
          <mxGeometry x="600" y="280" width="78" height="78"/>
        </mxCell>
        
        <!-- Amazon CloudWatch -->
        <mxCell id="cloudwatch" value="Amazon CloudWatch&#xa;監視・ログ" style="sketch=0;points=[[0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0],[0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0],[0,0.25,0],[0,0.5,0],[0,0.75,0],[1,0.25,0],[1,0.5,0],[1,0.75,0]];outlineConnect=0;fontColor=#232F3E;gradientColor=#F54749;gradientDirection=north;fillColor=#C7131F;strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize=12;fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.cloudwatch_2;" vertex="1" parent="1">
          <mxGeometry x="200" y="280" width="78" height="78"/>
        </mxCell>
        
        <!-- Connections -->
        <mxCell id="conn1" value="HTTPS POST" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="slack-app" target="api-gateway">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="conn2" value="リクエスト転送" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="api-gateway" target="lambda">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="conn3" value="問題生成" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="lambda" target="bedrock">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="conn4" value="スコア保存" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="lambda" target="dynamodb">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="conn5" value="認証情報取得" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="lambda" target="secrets">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
        <mxCell id="conn6" value="ログ出力" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="lambda" target="cloudwatch">
          <mxGeometry relative="1" as="geometry"/>
        </mxCell>
        
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## Lucidchart用テンプレート

### 1. 新規図表作成
1. Lucidchartにログイン
2. 「新規作成」→「空白の図表」
3. 「AWS」アイコンライブラリを追加

### 2. 使用するAWSアイコン
- **Compute**: AWS Lambda
- **Networking**: Amazon API Gateway
- **Database**: Amazon DynamoDB
- **Machine Learning**: Amazon Bedrock
- **Security**: AWS Secrets Manager, AWS KMS
- **Management**: Amazon CloudWatch

### 3. レイアウト構成
```
レイヤー1: Slack (紫色背景)
  - Slackユーザーアイコン
  - Slackアプリアイコン

レイヤー2: AWS API層 (オレンジ色背景)
  - Amazon API Gateway

レイヤー3: AWS処理層 (青色背景)
  - AWS Lambda (中央)
  - Amazon Bedrock (右上)
  - Amazon DynamoDB (右下)
  - AWS Secrets Manager (左下)

レイヤー4: AWS監視層 (緑色背景)
  - Amazon CloudWatch
```

## 日本語ラベル一覧

### サービス名
- Amazon API Gateway → Amazon API Gateway
- AWS Lambda → AWS Lambda
- Amazon DynamoDB → Amazon DynamoDB
- Amazon Bedrock → Amazon Bedrock
- AWS Secrets Manager → AWS Secrets Manager
- Amazon CloudWatch → Amazon CloudWatch

### 機能説明
- REST API エンドポイント
- サーバーレス関数実行
- NoSQL データベース
- 生成AI/機械学習サービス
- 認証情報管理
- 監視・ログ記録

### データフロー
- HTTPS POST リクエスト
- リクエスト転送
- 問題生成リクエスト
- スコア保存・取得
- 認証情報取得
- ログ出力

この日本語版アーキテクチャ図を使用することで、日本のチームメンバーや関係者に対してシステム構成を明確に説明できます。