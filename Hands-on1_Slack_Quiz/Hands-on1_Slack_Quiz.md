# Hands-on 1：Amazon Q + Slack インタラクティブクラウドサービス知識クイズゲーム構築

## 概要
この実験では、Amazon Q の Slack 統合を使用して "AWS クラウドサービス知識クイズ" ゲームを素早く構築する方法を学びます。ユーザーが Slack で `/awsquiz` Slash コマンドを入力すると、Amazon Q が自動的に多択問題を生成し、回答用ボタンを提供します。システムはリアルタイムでスコアを記録し、Slack Bot を通じてユーザーに直接フィードバックを提供し、即座にインタラクションが可能です。

## 目標
1. Slack における Amazon Q の問答とコンテンツ生成能力を体験する。
2. Amazon Q の出力を Lambda、DynamoDB などの AWS Serverless サービスと組み合わせて、インタラクティブアプリケーションを構築する方法を学ぶ。
3. Lambda + DynamoDB を通じてシンプルなスコア照会/ランキング機能を実装する方法を学ぶ。

## アーキテクチャ
```
ユーザー ➜ Slack Slash Command (/awsquiz) ➜ Amazon Q Chat (Slack 統合) ➜ AWS Lambda (問題ロジック & スコア計算) ➜ Amazon DynamoDB (スコア保存)
                                                                                    ↘ Slack Message (結果とスコアを返す)
```

## 前提条件
- 管理者権限を持つ AWS アカウントで、AWS Region **us-east-1** で Amazon Q (Preview) が有効化されている。
- カスタムアプリケーションをインストール可能な Slack Workspace と、対応する管理者権限。
- **AWS CLI**、**SAM CLI**、**Node.js 18+** または **Python 3.10+** がインストール・設定済み。

## 手順
1. **Amazon Q Slack 統合を有効化**  
   Amazon Q コンソール > Integrations で **Slack** を選択し、ウィザードに従って OAuth インストールを完了し、**Signing Secret** と **Bot Token** を記録します。

2. **Slash コマンド `/awsquiz` を作成**  
   Slack App 設定で Slash Command を追加し、Request URL を後でデプロイする API Gateway エンドポイントに設定します。例：`https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/quiz`。

3. **Serverless プロジェクトを初期化**  
   ```bash
   sam init --runtime python3.10 --name awsquiz
   cd awsquiz
   ```

4. **Lambda ハンドラーを作成** (`app.py`)：
   - Slash コマンド payload を解析。
   - Amazon Q Chat API（`BedrockRuntime.invoke_model`）を呼び出して問題と選択肢を生成。
   - Slack Block Kit を使用してボタン付きメッセージを構築して応答。
   - インタラクティブコールバックを処理し、スコアを計算して DynamoDB に書き込み、その後 Slack API を呼び出してリアルタイムスコアをユーザーにフィードバック。

5. **DynamoDB テーブルを設定**  
   `template.yaml` で `QuizScores` テーブルを宣言し、主キーを `user_id` に設定。読み取り/書き込み容量モードは On-Demand を選択してコストを削減。

6. **インフラストラクチャをデプロイ**  
   ```bash
   sam build && sam deploy --guided
   ```

7. **テストと検証**  
   - Slack で `/awsquiz` を入力し、問題に答えてスコアを確認。
   - 問題に答えて Slack がリアルタイムスコアフィードバックメッセージを受信しているか確認。

8. **拡張アイデア**  
   - トピック分類を導入（EC2、S3、Serverless など）。  
   - "毎日チャレンジ" 機能を追加。  
   - `/leaderboard` Slash コマンドを実装：このコマンドが Lambda をトリガーし、DynamoDB `QuizScores` テーブルからスコア最高のトップ 5 ユーザーを照会し、結果をテキストメッセージとしてフォーマットして Slack チャンネルに送信。
   - ランキングを会社内イントラネットポータルに組み込み。

9. **リソースのクリーンアップ**  
    ```bash
    sam delete
    ```
    > 注意: DynamoDB テーブルが `template.yaml` で定義されている場合、`sam delete` が自動的に削除します。テーブルを手動で作成した場合は、追加で `aws dynamodb delete-table --table-name QuizScores` を実行する必要があります。

## 費用予測
- Amazon Q Slack 統合：Preview 段階では無料（正式リリース後の価格設定にご注意ください）。  
- Lambda と API Gateway：< 1 USD/月（低呼び出し量）。  
- DynamoDB On-Demand：≈ 0.6 USD/100万書き込み/読み取りリクエスト。  

## 参考資料
- Amazon Q 公式ドキュメント：<https://docs.aws.amazon.com/ja_jp/amazonq/>  
- Slack App 開発者ガイド：<https://api.slack.com/docs>  
- AWS Serverless Application Model：<https://docs.aws.amazon.com/serverless-application-model/>