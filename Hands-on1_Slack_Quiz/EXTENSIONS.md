# 功能扩展指南

## 扩展功能概览

### 已实现功能
- ✅ 基础问答系统
- ✅ 分数统计
- ✅ 排行榜显示

### 扩展功能路线图
- 🔄 主题分类系统
- 🔄 每日挑战模式
- 🔄 团队竞赛功能
- 🔄 难度等级系统
- 🔄 成就徽章系统
- 🔄 学习路径推荐

## 1. 主题分类系统

### 1.1 数据模型扩展
```python
# 扩展 DynamoDB 表结构
TOPIC_CATEGORIES = {
    'compute': {
        'name': 'EC2 & 计算服务',
        'services': ['EC2', 'Lambda', 'ECS', 'EKS', 'Batch'],
        'icon': '💻'
    },
    'storage': {
        'name': 'S3 & 存储服务', 
        'services': ['S3', 'EBS', 'EFS', 'FSx'],
        'icon': '💾'
    },
    'database': {
        'name': '数据库服务',
        'services': ['RDS', 'DynamoDB', 'ElastiCache', 'Redshift'],
        'icon': '🗄️'
    },
    'networking': {
        'name': '网络 & CDN',
        'services': ['VPC', 'CloudFront', 'Route53', 'ELB'],
        'icon': '🌐'
    },
    'security': {
        'name': '安全 & 身份',
        'services': ['IAM', 'KMS', 'Secrets Manager', 'WAF'],
        'icon': '🔒'
    }
}
```

### 1.2 主题选择界面
```python
def create_topic_selection_blocks():
    """创建主题选择界面"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🎯 *选择你想挑战的 AWS 服务主题：*"
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
                    "text": {"type": "plain_text", "text": "🎲 随机主题"},
                    "value": "random",
                    "action_id": "topic_select_random",
                    "style": "primary"
                }
            ]
        }
    ]
```

### 1.3 主题统计功能
```python
def update_topic_stats(user_id, topic, is_correct):
    """更新主题统计"""
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
    """获取主题排行榜"""
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

## 2. 每日挑战模式

### 2.1 挑战数据模型
```python
# 新增 DailyChallenge 表
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
    """创建每日挑战"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 生成特殊主题的题目
    challenge_prompt = f"""
    生成一道 AWS 每日挑战题，难度：中等
    日期：{today}
    要求：
    1. 涵盖当前热门的 AWS 服务
    2. 具有实际应用场景
    3. 包含最佳实践考量
    4. 提供详细解释
    """
    
    question = generate_quiz_question(challenge_prompt)
    
    # 存储每日挑战题目
    challenge_table.put_item(
        Item={
            'challenge_date': today,
            'question_data': question,
            'created_at': int(time.time())
        }
    )
    
    return question
```

### 2.2 挑战参与追踪
```python
def participate_daily_challenge(user_id, answer, is_correct):
    """参与每日挑战"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 记录参与情况
    challenge_table.put_item(
        Item={
            'challenge_date': today,
            'user_id': user_id,
            'answer': answer,
            'is_correct': is_correct,
            'completed_at': int(time.time())
        }
    )
    
    # 更新连续挑战天数
    if is_correct:
        update_challenge_streak(user_id)

def update_challenge_streak(user_id):
    """更新连续挑战天数"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 检查昨天是否参与
    yesterday_record = challenge_table.get_item(
        Key={'challenge_date': yesterday, 'user_id': user_id}
    ).get('Item')
    
    if yesterday_record and yesterday_record.get('is_correct'):
        # 连续挑战
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='ADD daily_streak :one',
            ExpressionAttributeValues={':one': 1}
        )
    else:
        # 重置连续天数
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET daily_streak = :one',
            ExpressionAttributeValues={':one': 1}
        )
```

### 2.3 每日挑战排行榜
```python
def get_daily_challenge_leaderboard():
    """获取每日挑战排行榜"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    response = challenge_table.query(
        KeyConditionExpression='challenge_date = :date',
        ExpressionAttributeValues={':date': today}
    )
    
    participants = []
    for item in response['Items']:
        if item.get('is_correct'):
            participants.append({
                'user_id': item['user_id'],
                'completed_at': item['completed_at']
            })
    
    # 按完成时间排序（越早越好）
    participants.sort(key=lambda x: x['completed_at'])
    
    return participants[:10]  # 前10名
```

## 3. 团队竞赛功能

### 3.1 团队数据模型
```python
# 团队表结构
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
    """创建团队"""
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
    
    # 更新用户的团队信息
    table.update_item(
        Key={'user_id': creator_id},
        UpdateExpression='SET team_id = :team_id',
        ExpressionAttributeValues={':team_id': team_id}
    )
    
    return team_id

def join_team(user_id, team_id):
    """加入团队"""
    # 检查团队是否存在
    team = team_table.get_item(Key={'team_id': team_id}).get('Item')
    if not team:
        return False
    
    # 检查团队人数限制
    if len(team.get('members', [])) >= 10:
        return False
    
    # 添加成员
    team_table.update_item(
        Key={'team_id': team_id},
        UpdateExpression='SET members = list_append(members, :user)',
        ExpressionAttributeValues={':user': [user_id]}
    )
    
    # 更新用户团队信息
    table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='SET team_id = :team_id',
        ExpressionAttributeValues={':team_id': team_id}
    )
    
    return True
```

### 3.2 团队竞赛逻辑
```python
def update_team_score(user_id, points):
    """更新团队分数"""
    # 获取用户的团队ID
    user_data = table.get_item(Key={'user_id': user_id}).get('Item', {})
    team_id = user_data.get('team_id')
    
    if team_id:
        team_table.update_item(
            Key={'team_id': team_id},
            UpdateExpression='ADD total_score :points',
            ExpressionAttributeValues={':points': points}
        )

def get_team_leaderboard():
    """获取团队排行榜"""
    response = team_table.scan()
    teams = response['Items']
    
    # 按总分排序
    teams.sort(key=lambda x: x.get('total_score', 0), reverse=True)
    
    return teams[:10]

def create_team_challenge_blocks():
    """创建团队挑战界面"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "🏆 *团队挑战模式*\n选择你的行动："
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "🆕 创建团队"},
                    "value": "create_team",
                    "action_id": "team_create"
                },
                {
                    "type": "button", 
                    "text": {"type": "plain_text", "text": "🔍 加入团队"},
                    "value": "join_team",
                    "action_id": "team_join"
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "📊 团队排行榜"},
                    "value": "team_leaderboard",
                    "action_id": "team_leaderboard"
                }
            ]
        }
    ]
```

## 4. 难度等级系统

### 4.1 难度分级
```python
DIFFICULTY_LEVELS = {
    'beginner': {
        'name': '初级 🌱',
        'description': '适合 AWS 初学者',
        'points': 1,
        'topics': ['基础概念', '核心服务介绍']
    },
    'intermediate': {
        'name': '中级 🚀', 
        'description': '需要一定 AWS 经验',
        'points': 2,
        'topics': ['服务配置', '最佳实践']
    },
    'advanced': {
        'name': '高级 🎯',
        'description': '适合 AWS 专家',
        'points': 3,
        'topics': ['架构设计', '性能优化']
    },
    'expert': {
        'name': '专家 👑',
        'description': '极具挑战性',
        'points': 5,
        'topics': ['复杂场景', '故障排除']
    }
}

def generate_difficulty_question(difficulty):
    """根据难度生成题目"""
    level_info = DIFFICULTY_LEVELS[difficulty]
    
    prompt = f"""
    生成一道 AWS 云服务题目
    难度等级：{level_info['name']}
    主题范围：{', '.join(level_info['topics'])}
    
    要求：
    1. 符合{difficulty}难度要求
    2. 题目具有实际应用价值
    3. 选项设计合理，有一定迷惑性
    4. 提供清晰的解释说明
    """
    
    return generate_quiz_question(prompt)
```

### 4.2 自适应难度调整
```python
def calculate_user_level(user_id):
    """计算用户当前等级"""
    user_data = table.get_item(Key={'user_id': user_id}).get('Item', {})
    
    total_score = user_data.get('score', 0)
    total_questions = user_data.get('total_questions', 0)
    
    if total_questions < 10:
        return 'beginner'
    
    accuracy = total_score / total_questions
    
    if accuracy >= 0.8 and total_score >= 50:
        return 'expert'
    elif accuracy >= 0.7 and total_score >= 25:
        return 'advanced'
    elif accuracy >= 0.6 and total_score >= 10:
        return 'intermediate'
    else:
        return 'beginner'

def suggest_next_difficulty(user_id):
    """推荐下一题难度"""
    current_level = calculate_user_level(user_id)
    
    # 获取最近5题的表现
    recent_performance = get_recent_performance(user_id, 5)
    recent_accuracy = sum(recent_performance) / len(recent_performance) if recent_performance else 0
    
    if recent_accuracy >= 0.8:
        # 表现良好，可以提升难度
        levels = list(DIFFICULTY_LEVELS.keys())
        current_index = levels.index(current_level)
        if current_index < len(levels) - 1:
            return levels[current_index + 1]
    elif recent_accuracy < 0.5:
        # 表现不佳，降低难度
        levels = list(DIFFICULTY_LEVELS.keys())
        current_index = levels.index(current_level)
        if current_index > 0:
            return levels[current_index - 1]
    
    return current_level
```

## 5. 成就徽章系统

### 5.1 徽章定义
```python
ACHIEVEMENTS = {
    'first_correct': {
        'name': '初出茅庐',
        'description': '答对第一道题',
        'icon': '🎯',
        'condition': lambda stats: stats.get('score', 0) >= 1
    },
    'streak_5': {
        'name': '连胜达人',
        'description': '连续答对5题',
        'icon': '🔥',
        'condition': lambda stats: stats.get('current_streak', 0) >= 5
    },
    'topic_master': {
        'name': '主题专家',
        'description': '在某个主题达到90%正确率',
        'icon': '🏆',
        'condition': lambda stats: any(
            topic_stats.get('correct', 0) / topic_stats.get('total', 1) >= 0.9 
            and topic_stats.get('total', 0) >= 10
            for topic_stats in stats.get('topic_stats', {}).values()
        )
    },
    'daily_warrior': {
        'name': '每日战士',
        'description': '连续7天参与每日挑战',
        'icon': '⚔️',
        'condition': lambda stats: stats.get('daily_streak', 0) >= 7
    },
    'team_player': {
        'name': '团队之星',
        'description': '为团队贡献100分',
        'icon': '🌟',
        'condition': lambda stats: stats.get('team_contribution', 0) >= 100
    }
}

def check_achievements(user_id):
    """检查用户新获得的成就"""
    user_data = table.get_item(Key={'user_id': user_id}).get('Item', {})
    current_achievements = set(user_data.get('achievements', []))
    new_achievements = []
    
    for achievement_id, achievement in ACHIEVEMENTS.items():
        if achievement_id not in current_achievements:
            if achievement['condition'](user_data):
                new_achievements.append(achievement_id)
    
    if new_achievements:
        # 更新用户成就
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET achievements = list_append(if_not_exists(achievements, :empty), :new)',
            ExpressionAttributeValues={
                ':empty': [],
                ':new': new_achievements
            }
        )
    
    return new_achievements

def create_achievement_notification(achievements):
    """创建成就通知"""
    if not achievements:
        return None
    
    achievement_text = "\n".join([
        f"{ACHIEVEMENTS[ach]['icon']} *{ACHIEVEMENTS[ach]['name']}* - {ACHIEVEMENTS[ach]['description']}"
        for ach in achievements
    ])
    
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"🎉 *恭喜获得新成就！*\n\n{achievement_text}"
        }
    }
```

## 6. 学习路径推荐

### 6.1 学习路径定义
```python
LEARNING_PATHS = {
    'cloud_practitioner': {
        'name': 'AWS 云从业者',
        'description': '适合 AWS 初学者的基础路径',
        'topics': ['compute', 'storage', 'database', 'networking'],
        'estimated_time': '2-4周',
        'prerequisites': []
    },
    'solutions_architect': {
        'name': 'AWS 解决方案架构师',
        'description': '系统架构设计专业路径',
        'topics': ['compute', 'storage', 'database', 'networking', 'security'],
        'estimated_time': '6-8周',
        'prerequisites': ['cloud_practitioner']
    },
    'developer': {
        'name': 'AWS 开发者',
        'description': '专注于开发和部署的路径',
        'topics': ['compute', 'database', 'developer_tools'],
        'estimated_time': '4-6周',
        'prerequisites': ['cloud_practitioner']
    }
}

def recommend_learning_path(user_id):
    """推荐学习路径"""
    user_data = table.get_item(Key={'user_id': user_id}).get('Item', {})
    topic_stats = user_data.get('topic_stats', {})
    
    # 分析用户的强项和弱项
    strengths = []
    weaknesses = []
    
    for topic, stats in topic_stats.items():
        if stats.get('total', 0) >= 5:  # 至少答过5题
            accuracy = stats.get('correct', 0) / stats.get('total', 1)
            if accuracy >= 0.8:
                strengths.append(topic)
            elif accuracy < 0.5:
                weaknesses.append(topic)
    
    # 根据表现推荐路径
    if len(strengths) >= 3:
        return 'solutions_architect'
    elif 'compute' in strengths:
        return 'developer'
    else:
        return 'cloud_practitioner'

def create_learning_path_blocks(path_id):
    """创建学习路径展示"""
    path = LEARNING_PATHS[path_id]
    
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📚 *推荐学习路径：{path['name']}*\n\n{path['description']}\n\n⏱️ 预计时间：{path['estimated_time']}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📋 *包含主题：*\n" + "\n".join([
                    f"• {TOPIC_CATEGORIES[topic]['name']}"
                    for topic in path['topics']
                    if topic in TOPIC_CATEGORIES
                ])
            }
        }
    ]
```

## 7. 部署扩展功能

### 7.1 更新 SAM 模板
```yaml
# 添加新的 DynamoDB 表
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

# 添加定时任务生成每日挑战
DailyChallengeSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: "Generate daily challenge"
    ScheduleExpression: "cron(0 0 * * ? *)"  # 每天午夜
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

### 7.2 渐进式部署策略
```bash
# 阶段1：部署基础扩展
sam deploy --parameter-overrides EnableExtensions=basic

# 阶段2：启用高级功能
sam deploy --parameter-overrides EnableExtensions=advanced

# 阶段3：全功能部署
sam deploy --parameter-overrides EnableExtensions=full
```

通过这些扩展功能，可以将基础的问答系统发展成为一个功能丰富的学习平台，提供个性化的学习体验和社交互动功能。