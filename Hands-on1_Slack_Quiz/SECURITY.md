# セキュリティベストプラクティス

## セキュリティアーキテクチャ概要

### セキュリティレイヤー
```
┌─────────────────────────────────────────────────────────────┐
│                    ネットワークセキュリティ層                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  アプリケーションセキュリティ層          │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │                データセキュリティ層                  │ │ │
│  │  │  ┌─────────────────────────────────────────────────┐ │ │ │
│  │  │  │              アイデンティティとアクセス管理      │ │ │ │
│  │  │  └─────────────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 1. アイデンティティとアクセス管理 (IAM)

### Lambda 実行ロール
```yaml
SlackQuizExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: SlackQuizLambdaRole
    AssumeRolePolicyDocument:
      Version: '2012-10-17'
      Statement:
        - Effect: Allow
          Principal:
            Service: lambda.amazonaws.com
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
    Policies:
      - PolicyName: SlackQuizPolicy
        PolicyDocument:
          Version: '2012-10-17'
          Statement:
            # DynamoDB 最小権限
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
                - dynamodb:UpdateItem
                - dynamodb:Scan
              Resource: 
                - !GetAtt QuizScoresTable.Arn
                - !Sub "${QuizScoresTable.Arn}/index/*"
            
            # Bedrock 特定モデル権限
            - Effect: Allow
              Action: bedrock:InvokeModel
              Resource: 
                - !Sub "arn:aws:bedrock:${AWS::Region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            
            # Secrets Manager 特定シークレット権限
            - Effect: Allow
              Action: secretsmanager:GetSecretValue
              Resource:
                - !Ref SlackSigningSecret
                - !Ref SlackBotToken
```

## 2. データセキュリティ

### 2.1 転送時暗号化
```yaml
# API Gateway HTTPS 強制
SlackQuizApi:
  Type: AWS::Serverless::Api
  Properties:
    StageName: prod
    EndpointConfiguration:
      Type: EDGE
    MinimumCompressionSize: 1024
    # HTTPS 強制
    Domain:
      DomainName: api.yourcompany.com
      CertificateArn: !Ref SSLCertificate
      SecurityPolicy: TLS_1_2
```

### 2.2 保存時暗号化
```yaml
# DynamoDB テーブル暗号化
QuizScoresTable:
  Type: AWS::DynamoDB::Table
  Properties:
    SSESpecification:
      SSEEnabled: true
      KMSMasterKeyId: !Ref DynamoDBKMSKey
    PointInTimeRecoverySpecification:
      PointInTimeRecoveryEnabled: true

# KMS キー
DynamoDBKMSKey:
  Type: AWS::KMS::Key
  Properties:
    Description: "DynamoDB暗号化用KMSキー"
    KeyPolicy:
      Statement:
        - Effect: Allow
          Principal:
            AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
          Action: "kms:*"
          Resource: "*"
```

## 3. アプリケーションセキュリティ

### 3.1 Slack リクエスト検証
```python
import hmac
import hashlib
import time

def verify_slack_signature(event):
    """厳密な Slack 署名検証"""
    try:
        # リクエストヘッダー取得
        timestamp = event['headers'].get('X-Slack-Request-Timestamp')
        signature = event['headers'].get('X-Slack-Signature')
        body = event.get('body', '')
        
        if not timestamp or not signature:
            logger.warning("必要なヘッダーが不足")
            return False
        
        # タイムスタンプ検証（リプレイ攻撃防止）
        current_time = int(time.time())
        request_time = int(timestamp)
        
        if abs(current_time - request_time) > 300:  # 5分間ウィンドウ
            logger.warning(f"リクエストタイムスタンプが古すぎます: {current_time - request_time}秒")
            return False
        
        # 署名検証
        signing_secret = get_secret(SIGNING_SECRET_ARN)
        if not signing_secret:
            logger.error("署名シークレットの取得に失敗")
            return False
        
        sig_basestring = f"v0:{timestamp}:{body}"
        computed_signature = 'v0=' + hmac.new(
            signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # 安全な文字列比較を使用
        is_valid = hmac.compare_digest(computed_signature, signature)
        
        if not is_valid:
            logger.warning("無効な署名")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"署名検証エラー: {e}")
        return False
```

### 3.2 入力検証とサニタイゼーション
```python
import re
from html import escape

def validate_and_sanitize_input(user_input):
    """ユーザー入力の検証とサニタイゼーション"""
    if not user_input:
        return ""
    
    # 長さ制限
    if len(user_input) > 1000:
        raise ValueError("入力が長すぎます")
    
    # 危険な文字を除去
    sanitized = re.sub(r'[<>"\\']', '', user_input)
    
    # HTMLエスケープ
    sanitized = escape(sanitized)
    
    return sanitized.strip()

def validate_slack_payload(payload):
    """Slack ペイロード構造の検証"""
    required_fields = ['user', 'team', 'channel']
    
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"必須フィールドが不足: {field}")
    
    # ユーザーID形式の検証
    user_id = payload['user']['id']
    if not re.match(r'^U[A-Z0-9]{8,}$', user_id):
        raise ValueError("無効なユーザーID形式")
    
    return True
```

## 4. ネットワークセキュリティ

### 4.1 WAF 保護
```yaml
WebACL:
  Type: AWS::WAFv2::WebACL
  Properties:
    Name: SlackQuizWAF
    Scope: REGIONAL
    DefaultAction:
      Allow: {}
    Rules:
      # リクエスト頻度制限
      - Name: RateLimitRule
        Priority: 1
        Statement:
          RateBasedStatement:
            Limit: 1000
            AggregateKeyType: IP
        Action:
          Block: {}
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: RateLimitRule

# WAF を API Gateway に関連付け
WebACLAssociation:
  Type: AWS::WAFv2::WebACLAssociation
  Properties:
    ResourceArn: !Sub "${SlackQuizApi}/stages/prod"
    WebACLArn: !GetAtt WebACL.Arn
```

## 5. シークレット管理

### 5.1 Secrets Manager ベストプラクティス
```yaml
# Slack 署名シークレット
SlackSigningSecret:
  Type: AWS::SecretsManager::Secret
  Properties:
    Name: slack/signing-secret
    Description: "Slack アプリ署名シークレット"
    SecretString: !Ref SigningSecretValue
    KmsKeyId: !Ref SecretsKMSKey
    ReplicaRegions:
      - Region: us-west-2
        KmsKeyId: !Ref SecretsKMSKeyWest

# 自動ローテーション設定
SlackTokenRotation:
  Type: AWS::SecretsManager::RotationSchedule
  Properties:
    SecretId: !Ref SlackBotToken
    RotationLambdaArn: !GetAtt TokenRotationFunction.Arn
    RotationInterval: 30  # 30日ごとにローテーション
```

## 6. 監視と監査

### 6.1 セキュリティ監視
```yaml
# CloudWatch セキュリティアラーム
SecurityAlarms:
  - AlarmName: UnauthorizedAPIAccess
    MetricName: 4XXError
    Namespace: AWS/ApiGateway
    Threshold: 10
    ComparisonOperator: GreaterThanThreshold
    
  - AlarmName: LambdaErrors
    MetricName: Errors
    Namespace: AWS/Lambda
    Threshold: 5
    ComparisonOperator: GreaterThanThreshold
```

### 6.2 監査ログ
```python
import json
from datetime import datetime

def create_audit_log(event_type, user_id, details):
    """監査ログの作成"""
    audit_record = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': anonymize_user_data(user_id),
        'source_ip': get_source_ip(),
        'user_agent': get_user_agent(),
        'details': details,
        'request_id': context.aws_request_id
    }
    
    # 専用の監査ロググループに送信
    logger.info(f"AUDIT: {json.dumps(audit_record)}")

# 使用例
create_audit_log(
    event_type='QUIZ_ANSWERED',
    user_id=user_id,
    details={
        'question_id': question_id,
        'answer': answer,
        'is_correct': is_correct
    }
)
```

## 7. コンプライアンス考慮事項

### 7.1 データ保護規制
```python
# GDPR 準拠 - データ削除
def delete_user_data(user_id):
    """ユーザーデータの削除（GDPR準拠）"""
    try:
        # DynamoDB からユーザーデータを削除
        table.delete_item(Key={'user_id': user_id})
        
        # 削除操作を記録
        create_audit_log(
            event_type='USER_DATA_DELETED',
            user_id=user_id,
            details={'reason': 'GDPR_REQUEST'}
        )
        
        return True
    except Exception as e:
        logger.error(f"ユーザーデータの削除に失敗: {e}")
        return False

# データエクスポート（GDPR準拠）
def export_user_data(user_id):
    """ユーザーデータのエクスポート"""
    try:
        response = table.get_item(Key={'user_id': user_id})
        user_data = response.get('Item', {})
        
        # 内部フィールドを除去
        export_data = {
            'user_id': user_data.get('user_id'),
            'score': int(user_data.get('score', 0)),
            'total_questions': int(user_data.get('total_questions', 0)),
            'last_updated': user_data.get('last_updated')
        }
        
        return export_data
    except Exception as e:
        logger.error(f"ユーザーデータのエクスポートに失敗: {e}")
        return None
```

## 8. セキュリティチェックリスト

### デプロイ前チェック
- [ ] IAM 権限が最小権限の原則に従っている
- [ ] すべてのシークレットが Secrets Manager に保存されている
- [ ] 転送時および保存時の暗号化が有効
- [ ] WAF ルールが設定されている
- [ ] 監視とアラートが設定されている
- [ ] 入力検証が実装されている
- [ ] エラーハンドリングが設定されている

### 運用時チェック
- [ ] アクセスログの定期的な確認
- [ ] 異常なアクティビティの監視
- [ ] コスト異常のチェック
- [ ] バックアップの整合性確認
- [ ] 災害復旧手順のテスト

### 定期的なセキュリティ監査
- [ ] 四半期ごとの権限レビュー
- [ ] 年次ペネトレーションテスト
- [ ] 依存関係のセキュリティスキャン
- [ ] コンプライアンス評価

これらのセキュリティベストプラクティスを実装することで、Slack クイズアプリケーションがユーザーデータの保護、セキュリティ脅威の防止、コンプライアンス要件の満足において企業レベルの標準を達成できます。