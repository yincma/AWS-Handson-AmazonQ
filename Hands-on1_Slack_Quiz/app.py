import json
import os
import boto3
import hashlib
import hmac
import time
from urllib.parse import parse_qs
from decimal import Decimal

# AWS クライアント初期化
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
secrets_client = boto3.client('secretsmanager')

# 環境変数
TABLE_NAME = os.environ['QUIZ_TABLE_NAME']
SIGNING_SECRET_ARN = os.environ['SLACK_SIGNING_SECRET']
BOT_TOKEN_ARN = os.environ['SLACK_BOT_TOKEN']

table = dynamodb.Table(TABLE_NAME)

def get_secret(secret_arn):
    """Secrets Manager からシークレットを取得"""
    try:
        response = secrets_client.get_secret_value(SecretId=secret_arn)
        return response['SecretString']
    except Exception as e:
        print(f"シークレット取得エラー: {e}")
        return None

def verify_slack_request(event):
    """Slack リクエスト署名を検証"""
    try:
        signing_secret = get_secret(SIGNING_SECRET_ARN)
        if not signing_secret:
            return False
            
        timestamp = event['headers'].get('X-Slack-Request-Timestamp', '')
        signature = event['headers'].get('X-Slack-Signature', '')
        body = event.get('body', '')
        
        # タイムスタンプチェック（リプレイ攻撃防止）
        if abs(time.time() - int(timestamp)) > 300:
            return False
            
        # 署名検証
        sig_basestring = f"v0:{timestamp}:{body}"
        computed_signature = 'v0=' + hmac.new(
            signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(computed_signature, signature)
    except:
        return False

def generate_quiz_question():
    """Bedrock を使用して AWS クラウドサービス多選問題を生成"""
    prompt = """AWS クラウドサービスに関する単一選択問題を以下の形式で生成してください：
問題：[問題内容]
A. [選択肢A]
B. [選択肢B] 
C. [選択肢C]
D. [選択肢D]
正解：[A/B/C/D]
解説：[簡潔な解説]

要件：
1. 問題難易度は中程度、クラウドサービス初心者に適したレベル
2. AWS コアサービス（EC2、S3、Lambda、RDS等）をカバー
3. 選択肢は一定の紛らわしさがあるが答えは明確
4. 解説は簡潔でわかりやすいもの"""

    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        content = result['content'][0]['text']
        
        return parse_quiz_content(content)
    except Exception as e:
        print(f"クイズ生成エラー: {e}")
        return get_fallback_question()

def parse_quiz_content(content):
    """生成された問題内容を解析"""
    lines = content.strip().split('\n')
    question = ""
    options = []
    correct_answer = ""
    explanation = ""
    
    for line in lines:
        line = line.strip()
        if line.startswith('問題：'):
            question = line[3:]
        elif line.startswith(('A.', 'B.', 'C.', 'D.')):
            options.append(line)
        elif line.startswith('正解：'):
            correct_answer = line[3:].strip()
        elif line.startswith('解説：'):
            explanation = line[3:]
    
    return {
        'question': question,
        'options': options,
        'correct_answer': correct_answer,
        'explanation': explanation
    }

def get_fallback_question():
    """フォールバック問題"""
    return {
        'question': 'AWS Lambda の最大実行時間はどのくらいですか？',
        'options': [
            'A. 5分',
            'B. 15分', 
            'C. 30分',
            'D. 1時間'
        ],
        'correct_answer': 'B',
        'explanation': 'AWS Lambda 関数の最大実行時間は 15 分（900秒）です。'
    }

def create_quiz_blocks(quiz_data, user_id):
    """Slack Block Kit メッセージを作成"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🧠 *AWS クラウドサービス知識クイズ*\n\n*{quiz_data['question']}*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": option},
                    "value": json.dumps({
                        "answer": option[0],
                        "correct": quiz_data['correct_answer'],
                        "explanation": quiz_data['explanation'],
                        "user_id": user_id
                    }),
                    "action_id": f"quiz_answer_{option[0].lower()}"
                }
                for option in quiz_data['options']
            ]
        }
    ]

def update_user_score(user_id, is_correct):
    """ユーザースコアを更新"""
    try:
        if is_correct:
            response = table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='ADD score :inc, total_questions :one SET last_updated = :timestamp',
                ExpressionAttributeValues={
                    ':inc': Decimal('1'),
                    ':one': Decimal('1'),
                    ':timestamp': Decimal(str(int(time.time())))
                },
                ReturnValues='ALL_NEW'
            )
        else:
            response = table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='ADD total_questions :one SET last_updated = :timestamp',
                ExpressionAttributeValues={
                    ':one': Decimal('1'),
                    ':timestamp': Decimal(str(int(time.time())))
                },
                ReturnValues='ALL_NEW'
            )
        
        return response['Attributes']
    except Exception as e:
        print(f"スコア更新エラー: {e}")
        return None

def get_leaderboard():
    """ランキングボードを取得"""
    try:
        response = table.scan()
        items = response['Items']
        
        # スコアでソート
        sorted_items = sorted(items, key=lambda x: int(x.get('score', 0)), reverse=True)
        return sorted_items[:5]  # トップ5
    except Exception as e:
        print(f"ランキング取得エラー: {e}")
        return []

def get_user_rank(user_id):
    """ユーザー順位を取得"""
    try:
        response = table.scan()
        items = response['Items']
        
        # スコアでソート
        sorted_items = sorted(items, key=lambda x: int(x.get('score', 0)), reverse=True)
        
        for i, item in enumerate(sorted_items):
            if item['user_id'] == user_id:
                return i + 1, item
        
        return None, None
    except Exception as e:
        print(f"ユーザー順位取得エラー: {e}")
        return None, None

def handle_slash_command(body):
    """Slash Command を処理"""
    command = body.get('command', '')
    user_id = body.get('user_id', '')
    
    if command == '/awsquiz':
        quiz_data = generate_quiz_question()
        blocks = create_quiz_blocks(quiz_data, user_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response_type': 'ephemeral',
                'blocks': blocks
            })
        }
    
    elif command == '/leaderboard':
        leaderboard = get_leaderboard()
        user_rank, user_data = get_user_rank(user_id)
        
        leaderboard_text = "🏆 *AWS クイズランキング*\n\n"
        
        for i, item in enumerate(leaderboard):
            score = int(item.get('score', 0))
            total = int(item.get('total_questions', 0))
            accuracy = f"{(score/total*100):.1f}%" if total > 0 else "0%"
            leaderboard_text += f"{i+1}. <@{item['user_id']}> - {score}点 ({accuracy})\n"
        
        if user_rank:
            user_score = int(user_data.get('score', 0))
            user_total = int(user_data.get('total_questions', 0))
            user_accuracy = f"{(user_score/user_total*100):.1f}%" if user_total > 0 else "0%"
            leaderboard_text += f"\n📍 あなたの順位：第{user_rank}位 - {user_score}点 ({user_accuracy})"
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response_type': 'ephemeral',
                'text': leaderboard_text
            })
        }

def handle_interaction(payload):
    """ボタンインタラクションを処理"""
    action = payload['actions'][0]
    user_id = payload['user']['id']
    
    if action['action_id'].startswith('quiz_answer_'):
        answer_data = json.loads(action['value'])
        user_answer = answer_data['answer']
        correct_answer = answer_data['correct']
        explanation = answer_data['explanation']
        
        is_correct = user_answer == correct_answer
        user_data = update_user_score(user_id, is_correct)
        
        if is_correct:
            result_text = f"✅ *正解！* \n\n{explanation}"
        else:
            result_text = f"❌ *不正解！* 正解は {correct_answer} です\n\n{explanation}"
        
        if user_data:
            score = int(user_data.get('score', 0))
            total = int(user_data.get('total_questions', 0))
            accuracy = f"{(score/total*100):.1f}%" if total > 0 else "0%"
            result_text += f"\n\n📊 あなたの総スコア：{score}点 / {total}問 ({accuracy})"
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'response_type': 'ephemeral',
                'replace_original': True,
                'text': result_text
            })
        }

def lambda_handler(event, context):
    """Lambda メインハンドラー関数"""
    try:
        # リクエスト検証
        if not verify_slack_request(event):
            return {'statusCode': 401, 'body': 'Unauthorized'}
        
        # リクエストボディ解析
        if event.get('body'):
            if event['headers'].get('content-type', '').startswith('application/x-www-form-urlencoded'):
                # Slash Command
                body = parse_qs(event['body'])
                body = {k: v[0] if v else '' for k, v in body.items()}
                return handle_slash_command(body)
            else:
                # Interactive Component
                payload = json.loads(parse_qs(event['body'])['payload'][0])
                return handle_interaction(payload)
        
        return {'statusCode': 400, 'body': 'Bad Request'}
        
    except Exception as e:
        print(f"エラー: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }