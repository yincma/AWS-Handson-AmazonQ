# 機能拡張ガイド

## 拡張機能概要

### 実装済み機能
- ✅ 基本問答システム
- ✅ スコア統計
- ✅ ランキング表示

### 拡張機能ロードマップ
- 🔄 トピック分類システム
- 🔄 毎日チャレンジモード
- 🔄 チーム競争機能
- 🔄 難易度レベルシステム
- 🔄 実績バッジシステム
- 🔄 学習パス推奨

## 1. トピック分類システム

### 1.1 データモデル拡張
```python
# DynamoDB テーブル構造を拡張
TOPIC_CATEGORIES = {
    'compute': {
        'name': 'EC2 & コンピュートサービス',
        'services': ['EC2', 'Lambda', 'ECS', 'EKS', 'Batch'],
        'icon': '💻'
    },
    'storage': {
        'name': 'S3 & ストレージサービス', 
        'services': ['S3', 'EBS', 'EFS', 'FSx'],
        'icon': '💾'
    },
    'database': {
        'name': 'データベースサービス',
        'services': ['RDS', 'DynamoDB', 'ElastiCache', 'Redshift'],
        'icon': '🗄️'
    },
    'networking': {
        'name': 'ネットワーク & CDN',
        'services': ['VPC', 'CloudFront', 'Route53', 'ELB'],
        'icon': '🌐'
    },
    'security': {
        'name': 'セキュリティ & アイデンティティ',
        'services': ['IAM', 'KMS', 'Secrets Manager', 'WAF'],
        'icon': '🔒'
    }
}
```

### 1.2 トピック選択インターフェース
```python
def create_topic_selection_blocks():
    """トピック選択インターフェースを作成"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🎯 *挑戦したい AWS サービストピックを選択してください：*"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": f"{topic['icon']} {topic['name']}"
                    },
                    "value": topic_key,
                    "action_id": f"topic_select_{topic_key}"
                }
                for topic_key, topic in TOPIC_CATEGORIES.items()
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🎲 ランダムトピック"},
                    "value": "random",
                    "action_id": "topic_select_random",
                    "style": "primary"
                }
            ]
        }
    ]
```

### 1.3 トピック統計機能
```python
def update_topic_stats(user_id, topic, is_correct):
    """トピック統計を更新"""
    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='''
            ADD topic_stats.#topic.correct :correct,
                topic_stats.#topic.total :one
            SET topic_stats.#topic.last_attempt = :timestamp
        ''',
        ExpressionAttributeNames={
            '#topic': topic
        },
        ExpressionAttributeValues={
            ':correct': 1 if is_correct else 0,
            ':one': 1,
            ':timestamp': int(time.time())
        }
    )

def get_topic_leaderboard(topic):
    """トピックランキングを取得"""
    response = table.scan(
        FilterExpression='attribute_exists(topic_stats.#topic)',
        ExpressionAttributeNames={'#topic': topic}
    )
    
    items = []
    for item in response['Items']:
        topic_data = item['topic_stats'][topic]
        accuracy = topic_data['correct'] / topic_data['total']
        items.append({
            'user_id': item['user_id'],
            'score': topic_data['correct'],
            'total': topic_data['total'],
            'accuracy': accuracy
        })
    
    return sorted(items, key=lambda x: (x['score'], x['accuracy']), reverse=True)[:10]
```

## 2. 毎日チャレンジモード

### 2.1 チャレンジデータモデル
```python
# 新しい DailyChallenge テーブル
DAILY_CHALLENGE_TABLE = {
    'TableName': 'DailyChallenge',
    'KeySchema': [
        {'AttributeName': 'challenge_date', 'KeyType': 'HASH'},
        {'AttributeName': 'user_id', 'KeyType': 'RANGE'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'challenge_date', 'AttributeType': 'S'},
        {'AttributeName': 'user_id', 'AttributeType': 'S'}
    ]
}

def create_daily_challenge():
    """毎日チャレンジを作成"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 特別なトピックの問題を生成
    challenge_prompt = f"""
    AWS 毎日チャレンジ問題を生成してください、難易度：中級
    日付：{today}
    要件：
    1. 現在人気の AWS サービスをカバー
    2. 実際の応用シナリオを含む
    3. ベストプラクティスの考慮を含む
    4. 詳細な解説を提供
    """
    
    question = generate_quiz_question(challenge_prompt)
    
    # 毎日チャレンジ問題を保存
    challenge_table.put_item(
        Item={
            'challenge_date': today,
            'question_data': question,
            'created_at': int(time.time())
        }
    )
    
    return question
```

### 2.2 チャレンジ参加追跡
```python
def participate_daily_challenge(user_id, answer, is_correct):
    """毎日チャレンジに参加"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 参加状況を記録
    challenge_table.put_item(
        Item={
            'challenge_date': today,
            'user_id': user_id,
            'answer': answer,
            'is_correct': is_correct,
            'completed_at': int(time.time())
        }
    )
    
    # 連続チャレンジ日数を更新
    if is_correct:
        update_challenge_streak(user_id)

def update_challenge_streak(user_id):
    """連続チャレンジ日数を更新"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 昨日の参加をチェック
    yesterday_record = challenge_table.get_item(
        Key={'challenge_date': yesterday, 'user_id': user_id}
    ).get('Item')
    
    if yesterday_record and yesterday_record.get('is_correct'):
        # 連続チャレンジ
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='ADD daily_streak :one',
            ExpressionAttributeValues={':one': 1}
        )
    else:
        # 連続日数をリセット
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET daily_streak = :one',
            ExpressionAttributeValues={':one': 1}
        )
```

## 3. チーム競争機能

### 3.1 チームデータモデル
```python
# チームテーブル構造
TEAM_TABLE = {
    'TableName': 'Teams',
    'KeySchema': [
        {'AttributeName': 'team_id', 'KeyType': 'HASH'}
    ],
    'AttributeDefinitions': [
        {'AttributeName': 'team_id', 'AttributeType': 'S'}
    ]
}

def create_team(team_name, creator_id):
    """チームを作成"""
    team_id = f"team_{int(time.time())}"
    
    team_table.put_item(
        Item={
            'team_id': team_id,
            'team_name': team_name,
            'creator_id': creator_id,
            'members': [creator_id],
            'total_score': 0,
            'created_at': int(time.time())
        }
    )
    
    # ユーザーのチーム情報を更新
    table.update_item(
        Key={'user_id': creator_id},
        UpdateExpression='SET team_id = :team_id',
        ExpressionAttributeValues={':team_id': team_id}
    )
    
    return team_id

def join_team(user_id, team_id):
    """チームに参加"""
    # チームの存在をチェック
    team = team_table.get_item(Key={'team_id': team_id}).get('Item')
    if not team:
        return False
    
    # チーム人数制限をチェック
    if len(team.get('members', [])) >= 10:
        return False
    
    # メンバーを追加
    team_table.update_item(
        Key={'team_id': team_id},
        UpdateExpression='SET members = list_append(members, :user)',
        ExpressionAttributeValues={':user': [user_id]}
    )
    
    # ユーザーのチーム情報を更新
    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='SET team_id = :team_id',
        ExpressionAttributeValues={':team_id': team_id}
    )
    
    return True
```

## 4. 難易度レベルシステム

### 4.1 難易度分類
```python
DIFFICULTY_LEVELS = {
    'beginner': {
        'name': '初級 🌱',
        'description': 'AWS 初心者に適している',
        'points': 1,
        'topics': ['基本概念', 'コアサービス紹介']
    },
    'intermediate': {
        'name': '中級 🚀', 
        'description': '一定の AWS 経験が必要',
        'points': 2,
        'topics': ['サービス設定', 'ベストプラクティス']
    },
    'advanced': {
        'name': '上級 🎯',
        'description': 'AWS エキスパートに適している',
        'points': 3,
        'topics': ['アーキテクチャ設計', 'パフォーマンス最適化']
    },
    'expert': {
        'name': 'エキスパート 👑',
        'description': '非常にチャレンジング',
        'points': 5,
        'topics': ['複雑なシナリオ', 'トラブルシューティング']
    }
}

def generate_difficulty_question(difficulty):
    """難易度に応じて問題を生成"""
    level_info = DIFFICULTY_LEVELS[difficulty]
    
    prompt = f"""
    AWS クラウドサービス問題を生成してください
    難易度レベル：{level_info['name']}
    トピック範囲：{', '.join(level_info['topics'])}
    
    要件：
    1. {difficulty}難易度要件に適合
    2. 問題は実際の応用価値を持つ
    3. 選択肢の設計が合理的で、一定の紛らわしさがある
    4. 明確な解説を提供
    """
    
    return generate_quiz_question(prompt)
```

## 5. 実績バッジシステム

### 5.1 バッジ定義
```python
ACHIEVEMENTS = {
    'first_correct': {
        'name': '初回正解',
        'description': '最初の問題に正解',
        'icon': '🎯',
        'condition': lambda stats: stats.get('score', 0) >= 1
    },
    'streak_5': {
        'name': '連勝達人',
        'description': '連続5問正解',
        'icon': '🔥',
        'condition': lambda stats: stats.get('current_streak', 0) >= 5
    },
    'topic_master': {
        'name': 'トピックエキスパート',
        'description': 'あるトピックで90%の正解率を達成',
        'icon': '🏆',
        'condition': lambda stats: any(
            topic_stats.get('correct', 0) / topic_stats.get('total', 1) >= 0.9 
            and topic_stats.get('total', 0) >= 10
            for topic_stats in stats.get('topic_stats', {}).values()
        )
    },
    'daily_warrior': {
        'name': '毎日の戦士',
        'description': '連続7日間毎日チャレンジに参加',
        'icon': '⚔️',
        'condition': lambda stats: stats.get('daily_streak', 0) >= 7
    },
    'team_player': {
        'name': 'チームスター',
        'description': 'チームに100点貢献',
        'icon': '🌟',
        'condition': lambda stats: stats.get('team_contribution', 0) >= 100
    }
}

def check_achievements(user_id):
    """ユーザーの新しい実績をチェック"""
    user_data = table.get_item(Key={'user_id': user_id}).get('Item', {})
    current_achievements = set(user_data.get('achievements', []))
    new_achievements = []
    
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id not in current_achievements:
            if achievement['condition'](user_data):
                new_achievements.append(achievement_id)
    
    if new_achievements:
        # ユーザーの実績を更新
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET achievements = list_append(if_not_exists(achievements, :empty), :new)',
            ExpressionAttributeValues={
                ':empty': [],
                ':new': new_achievements
            }
        )
    
    return new_achievements
```

## 6. 学習パス推奨

### 6.1 学習パス定義
```python
LEARNING_PATHS = {
    'cloud_practitioner': {
        'name': 'AWS クラウドプラクティショナー',
        'description': 'AWS 初心者向けの基礎パス',
        'topics': ['compute', 'storage', 'database', 'networking'],
        'estimated_time': '2-4週間',
        'prerequisites': []
    },
    'solutions_architect': {
        'name': 'AWS ソリューションアーキテクト',
        'description': 'システムアーキテクチャ設計専門パス',
        'topics': ['compute', 'storage', 'database', 'networking', 'security'],
        'estimated_time': '6-8週間',
        'prerequisites': ['cloud_practitioner']
    },
    'developer': {
        'name': 'AWS デベロッパー',
        'description': '開発とデプロイに焦点を当てたパス',
        'topics': ['compute', 'database', 'developer_tools'],
        'estimated_time': '4-6週間',
        'prerequisites': ['cloud_practitioner']
    }
}

def recommend_learning_path(user_id):
    """学習パスを推奨"""
    user_data = table.get_item(Key={'user_id': user_id}).get('Item', {})
    topic_stats = user_data.get('topic_stats', {})
    
    # ユーザーの強みと弱みを分析
    strengths = []
    weaknesses = []
    
    for topic, stats in topic_stats.items():
        if stats.get('total', 0) >= 5:  # 少なくとも5問回答
            accuracy = stats.get('correct', 0) / stats.get('total', 1)
            if accuracy >= 0.8:
                strengths.append(topic)
            elif accuracy < 0.5:
                weaknesses.append(topic)
    
    # パフォーマンスに基づいてパスを推奨
    if len(strengths) >= 3:
        return 'solutions_architect'
    elif 'compute' in strengths:
        return 'developer'
    else:
        return 'cloud_practitioner'
```

## 7. 拡張機能のデプロイ

### 7.1 SAM テンプレートの更新
```yaml
# 新しい DynamoDB テーブルを追加
DailyChallengeTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: DailyChallenge
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: challenge_date
        AttributeType: S
      - AttributeName: user_id
        AttributeType: S
    KeySchema:
      - AttributeName: challenge_date
        KeyType: HASH
      - AttributeName: user_id
        KeyType: RANGE

TeamsTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: Teams
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: team_id
        AttributeType: S
    KeySchema:
      - AttributeName: team_id
        KeyType: HASH

# 毎日チャレンジ生成のスケジュールタスクを追加
DailyChallengeSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: "毎日チャレンジ生成"
    ScheduleExpression: "cron(0 0 * * ? *)"  # 毎日深夜
    State: ENABLED
    Targets:
      - Arn: !GetAtt DailyChallengeFunction.Arn
        Id: "DailyChallengeTarget"

DailyChallengeFunction:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: .
    Handler: daily_challenge.lambda_handler
    Environment:
      Variables:
        CHALLENGE_TABLE_NAME: !Ref DailyChallengeTable
```

### 7.2 段階的デプロイ戦略
```bash
# ステージ1：基本拡張をデプロイ
sam deploy --parameter-overrides EnableExtensions=basic

# ステージ2：高度な機能を有効化
sam deploy --parameter-overrides EnableExtensions=advanced

# ステージ3：全機能デプロイ
sam deploy --parameter-overrides EnableExtensions=full
```

これらの拡張機能により、基本的な問答システムを機能豊富な学習プラットフォームに発展させ、個人化された学習体験とソーシャルインタラクション機能を提供できます。