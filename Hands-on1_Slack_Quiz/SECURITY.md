# 安全最佳实践

## 安全架构概览

### 安全层级
```
┌─────────────────────────────────────────────────────────────┐
│                    网络安全层                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  应用安全层                              │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │                数据安全层                            │ │ │
│  │  │  ┌─────────────────────────────────────────────────┐ │ │ │
│  │  │  │              身份与访问管理                      │ │ │ │
│  │  │  └─────────────────────────────────────────────────┘ │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 1. 身份与访问管理 (IAM)

### Lambda 执行角色
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
            # DynamoDB 最小权限
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
                - dynamodb:UpdateItem
                - dynamodb:Scan
              Resource: 
                - !GetAtt QuizScoresTable.Arn
                - !Sub "${QuizScoresTable.Arn}/index/*"
            
            # Bedrock 特定模型权限
            - Effect: Allow
              Action: bedrock:InvokeModel
              Resource: 
                - !Sub "arn:aws:bedrock:${AWS::Region}::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
            
            # Secrets Manager 特定密钥权限
            - Effect: Allow
              Action: secretsmanager:GetSecretValue
              Resource:
                - !Ref SlackSigningSecret
                - !Ref SlackBotToken
```

### 资源级权限控制
```python
# 在 Lambda 中实现额外的权限检查
def check_user_permissions(user_id, team_id):
    """验证用户是否有权限使用应用"""
    # 可以实现团队白名单、用户黑名单等逻辑
    allowed_teams = os.environ.get('ALLOWED_TEAMS', '').split(',')
    
    if allowed_teams and team_id not in allowed_teams:
        return False
    
    return True
```

## 2. 数据安全

### 2.1 传输加密
```yaml
# API Gateway 强制 HTTPS
SlackQuizApi:
  Type: AWS::Serverless::Api
  Properties:
    StageName: prod
    EndpointConfiguration:
      Type: EDGE
    MinimumCompressionSize: 1024
    # 强制 HTTPS
    Domain:
      DomainName: api.yourcompany.com
      CertificateArn: !Ref SSLCertificate
      SecurityPolicy: TLS_1_2
```

### 2.2 存储加密
```yaml
# DynamoDB 表加密
QuizScoresTable:
  Type: AWS::DynamoDB::Table
  Properties:
    SSESpecification:
      SSEEnabled: true
      KMSMasterKeyId: !Ref DynamoDBKMSKey
    PointInTimeRecoverySpecification:
      PointInTimeRecoveryEnabled: true

# KMS 密钥
DynamoDBKMSKey:
  Type: AWS::KMS::Key
  Properties:
    Description: "KMS Key for DynamoDB encryption"
    KeyPolicy:
      Statement:
        - Effect: Allow
          Principal:
            AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
          Action: "kms:*"
          Resource: "*"
        - Effect: Allow
          Principal:
            Service: dynamodb.amazonaws.com
          Action:
            - kms:Decrypt
            - kms:GenerateDataKey
          Resource: "*"
```

### 2.3 数据脱敏
```python
import hashlib

def anonymize_user_data(user_id):
    """对用户 ID 进行哈希处理"""
    salt = os.environ.get('USER_ID_SALT', 'default_salt')
    return hashlib.sha256(f"{user_id}{salt}".encode()).hexdigest()[:16]

def log_user_action(user_id, action):
    """记录用户操作时脱敏处理"""
    anonymized_id = anonymize_user_data(user_id)
    logger.info(f"User {anonymized_id} performed action: {action}")
```

## 3. 应用安全

### 3.1 Slack 请求验证
```python
import hmac
import hashlib
import time

def verify_slack_signature(event):
    """严格的 Slack 签名验证"""
    try:
        # 获取请求头
        timestamp = event['headers'].get('X-Slack-Request-Timestamp')
        signature = event['headers'].get('X-Slack-Signature')
        body = event.get('body', '')
        
        if not timestamp or not signature:
            logger.warning("Missing required headers")
            return False
        
        # 时间戳验证（防重放攻击）
        current_time = int(time.time())
        request_time = int(timestamp)
        
        if abs(current_time - request_time) > 300:  # 5分钟窗口
            logger.warning(f"Request timestamp too old: {current_time - request_time}s")
            return False
        
        # 签名验证
        signing_secret = get_secret(SIGNING_SECRET_ARN)
        if not signing_secret:
            logger.error("Failed to retrieve signing secret")
            return False
        
        sig_basestring = f"v0:{timestamp}:{body}"
        computed_signature = 'v0=' + hmac.new(
            signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # 使用安全的字符串比较
        is_valid = hmac.compare_digest(computed_signature, signature)
        
        if not is_valid:
            logger.warning("Invalid signature")
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False
```

### 3.2 输入验证与清理
```python
import re
from html import escape

def validate_and_sanitize_input(user_input):
    """验证和清理用户输入"""
    if not user_input:
        return ""
    
    # 长度限制
    if len(user_input) > 1000:
        raise ValueError("Input too long")
    
    # 移除危险字符
    sanitized = re.sub(r'[<>"\']', '', user_input)
    
    # HTML 转义
    sanitized = escape(sanitized)
    
    return sanitized.strip()

def validate_slack_payload(payload):
    """验证 Slack 载荷结构"""
    required_fields = ['user', 'team', 'channel']
    
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")
    
    # 验证用户 ID 格式
    user_id = payload['user']['id']
    if not re.match(r'^U[A-Z0-9]{8,}$', user_id):
        raise ValueError("Invalid user ID format")
    
    return True
```

### 3.3 错误处理与信息泄露防护
```python
def safe_error_response(error_msg, user_facing_msg="操作失败，请稍后重试"):
    """安全的错误响应，避免信息泄露"""
    # 记录详细错误到日志
    logger.error(f"Internal error: {error_msg}")
    
    # 返回通用错误信息给用户
    return {
        'statusCode': 500,
        'body': json.dumps({
            'response_type': 'ephemeral',
            'text': user_facing_msg
        })
    }

def lambda_handler(event, context):
    try:
        # 主要逻辑
        return process_request(event)
    except ValueError as e:
        # 用户输入错误
        return safe_error_response(str(e), "输入格式不正确")
    except Exception as e:
        # 系统错误
        return safe_error_response(str(e))
```

## 4. 网络安全

### 4.1 VPC 配置（可选增强安全）
```yaml
# 如需更高安全性，可将 Lambda 部署到 VPC
VPCConfig:
  Type: AWS::EC2::VPC
  Properties:
    CidrBlock: 10.0.0.0/16
    EnableDnsHostnames: true
    EnableDnsSupport: true

PrivateSubnet:
  Type: AWS::EC2::Subnet
  Properties:
    VpcId: !Ref VPCConfig
    CidrBlock: 10.0.1.0/24
    AvailabilityZone: !Select [0, !GetAZs '']

# Lambda VPC 配置
SlackQuizFunction:
  Type: AWS::Serverless::Function
  Properties:
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds:
        - !Ref PrivateSubnet
```

### 4.2 WAF 保护
```yaml
WebACL:
  Type: AWS::WAFv2::WebACL
  Properties:
    Name: SlackQuizWAF
    Scope: REGIONAL
    DefaultAction:
      Allow: {}
    Rules:
      # 限制请求频率
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
      
      # 阻止已知恶意 IP
      - Name: IPReputationRule
        Priority: 2
        Statement:
          ManagedRuleGroupStatement:
            VendorName: AWS
            Name: AWSManagedRulesAmazonIpReputationList
        OverrideAction:
          None: {}
        VisibilityConfig:
          SampledRequestsEnabled: true
          CloudWatchMetricsEnabled: true
          MetricName: IPReputationRule

# 关联 WAF 到 API Gateway
WebACLAssociation:
  Type: AWS::WAFv2::WebACLAssociation
  Properties:
    ResourceArn: !Sub "${SlackQuizApi}/stages/prod"
    WebACLArn: !GetAtt WebACL.Arn
```

## 5. 密钥管理

### 5.1 Secrets Manager 最佳实践
```yaml
# Slack Signing Secret
SlackSigningSecret:
  Type: AWS::SecretsManager::Secret
  Properties:
    Name: slack/signing-secret
    Description: "Slack App Signing Secret"
    SecretString: !Ref SigningSecretValue
    KmsKeyId: !Ref SecretsKMSKey
    ReplicaRegions:
      - Region: us-west-2
        KmsKeyId: !Ref SecretsKMSKeyWest

# 自动轮换配置
SlackTokenRotation:
  Type: AWS::SecretsManager::RotationSchedule
  Properties:
    SecretId: !Ref SlackBotToken
    RotationLambdaArn: !GetAtt TokenRotationFunction.Arn
    RotationInterval: 30  # 30天轮换一次
```

### 5.2 密钥访问审计
```python
def audit_secret_access(secret_arn, user_context):
    """审计密钥访问"""
    cloudtrail_event = {
        'eventTime': datetime.utcnow().isoformat(),
        'eventName': 'GetSecretValue',
        'eventSource': 'secretsmanager.amazonaws.com',
        'userIdentity': user_context,
        'resources': [{'ARN': secret_arn}]
    }
    
    # 发送到 CloudWatch Logs
    logger.info(f"Secret access audit: {json.dumps(cloudtrail_event)}")
```

## 6. 监控与审计

### 6.1 安全监控
```yaml
# CloudWatch 安全告警
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

  - AlarmName: DynamoDBThrottles
    MetricName: ThrottledRequests
    Namespace: AWS/DynamoDB
    Threshold: 1
    ComparisonOperator: GreaterThanOrEqualToThreshold
```

### 6.2 审计日志
```python
import json
from datetime import datetime

def create_audit_log(event_type, user_id, details):
    """创建审计日志"""
    audit_record = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': anonymize_user_data(user_id),
        'source_ip': get_source_ip(),
        'user_agent': get_user_agent(),
        'details': details,
        'request_id': context.aws_request_id
    }
    
    # 发送到专用的审计日志组
    logger.info(f"AUDIT: {json.dumps(audit_record)}")

# 使用示例
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

## 7. 合规性考虑

### 7.1 数据保护法规
```python
# GDPR 合规 - 数据删除
def delete_user_data(user_id):
    """删除用户数据（GDPR 合规）"""
    try:
        # 删除 DynamoDB 中的用户数据
        table.delete_item(Key={'user_id': user_id})
        
        # 记录删除操作
        create_audit_log(
            event_type='USER_DATA_DELETED',
            user_id=user_id,
            details={'reason': 'GDPR_REQUEST'}
        )
        
        return True
    except Exception as e:
        logger.error(f"Failed to delete user data: {e}")
        return False

# 数据导出（GDPR 合规）
def export_user_data(user_id):
    """导出用户数据"""
    try:
        response = table.get_item(Key={'user_id': user_id})
        user_data = response.get('Item', {})
        
        # 移除内部字段
        export_data = {
            'user_id': user_data.get('user_id'),
            'score': int(user_data.get('score', 0)),
            'total_questions': int(user_data.get('total_questions', 0)),
            'last_updated': user_data.get('last_updated')
        }
        
        return export_data
    except Exception as e:
        logger.error(f"Failed to export user data: {e}")
        return None
```

### 7.2 数据保留策略
```yaml
# DynamoDB TTL 配置
QuizScoresTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TimeToLiveSpecification:
      AttributeName: ttl
      Enabled: true

# CloudWatch Logs 保留期
LogRetentionPolicy:
  Type: AWS::Logs::LogGroup
  Properties:
    LogGroupName: !Sub "/aws/lambda/${SlackQuizFunction}"
    RetentionInDays: 90  # 90天保留期
```

## 8. 安全检查清单

### 部署前检查
- [ ] IAM 权限遵循最小权限原则
- [ ] 所有密钥存储在 Secrets Manager
- [ ] 启用传输和存储加密
- [ ] 配置 WAF 规则
- [ ] 设置监控和告警
- [ ] 实施输入验证
- [ ] 配置错误处理

### 运行时检查
- [ ] 定期审查访问日志
- [ ] 监控异常活动
- [ ] 检查成本异常
- [ ] 验证备份完整性
- [ ] 测试灾难恢复流程

### 定期安全审计
- [ ] 季度权限审查
- [ ] 年度渗透测试
- [ ] 依赖项安全扫描
- [ ] 合规性评估

通过实施这些安全最佳实践，可以确保 Slack Quiz 应用在保护用户数据、防范安全威胁和满足合规要求方面达到企业级标准。