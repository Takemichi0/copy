## What's this?

提供されたPDFの内容に関する質問に自動的に答えることができるツールを作成する  
利用シナリオ: 学術論文の長い文書に対して、特定の情報やデータを素早く取得したい場合。PDFアップロード可のため取扱説明書や利用規約にも応用可能。  

## 関連リンク
- [Notion](https://www.notion.so/Arxiv-Interpreter-79c7f39d96614a569ab9588363840225)
- [Asana](https://app.asana.com/0/1205566635091585/1205566639320124)

## インフラ / 技術スタック  
GoogleのサービスはtransXのGoogleアカウントが権限を有している。  

- フロントエンド(/frontend)  
  Next.js, deploy to Vercel.  (Firebase Auth)
  Todo; vercelは商用利用不可のためconohaなどに乗り換えを検討.  

- サーバサイド  
  Python(fastAPI), deploy to GCP(Cloud Run) (DBはQdrant / Firebaseを使用)
  FirebaseのAuthでアクセス制限.  

  [アーキテクチャ図](https://www.notion.so/Arxiv-Interpreter-79c7f39d96614a569ab9588363840225)
  

## 環境構築
事前にDockerの環境を用意する。 (アプリを入れると良いかと思います)

Dockerコンテナをビルド / 起動 (初回のみ)  
`docker-compose up --build`

Dockerコンテナを起動  
`docker-compose up`

サーバーサイドは `http://localhost:8000` で起動  
フロントエンドは `http://localhost:3000` で起動 

Swagger  
`http://localhost:8000/docs#/`

## Local環境での開発の仕方
1. [slack bot](https://api.slack.com/apps)を新規作成する / その後作成したアプリのポータル画面へ行き.. `https://api.slack.com/apps/{app_id}`
2. Install appでtransxのワークスーペースに追加する  
3. Basic informaiton下部にあるapp idなどを.envに上書き(4つ程度ある)
4. event subscrioptionsでlocalで立ち上げたngrokのURLを追加する `http:// ....ngrok-free.tech/slack/events` など(最後のeventsは環境に合わせて、jap or events)  
5. event subscrioptions下部のSubscribe to bot eventsにapp_mentionとmessage.channelsを追加。
6. Oauth & Permissions でBot Token Scopesにapp_mentions:read / channels:history / chat:write / groups:history / im:history / mpim:history を追加
7. 最終的に以下のようなapp manifestが完成すれば良い（不一致部分はApp manifestを修正して欲しい) (arxivistaの例)
```
{
    "display_information": {
        "name": "Arxivista"
    },
    "features": {
        "bot_user": {
            "display_name": "Arxivista",
            "always_online": true
        }
    },
    "oauth_config": {
        "redirect_urls": [
            "https://api.arxivista.transx.tech/finish_auth"
        ],
        "scopes": {
            "bot": [
                "channels:history",
                "groups:history",
                "im:history",
                "mpim:history",
                "chat:write",
                "app_mentions:read"
            ]
        }
    },
    "settings": {
        "event_subscriptions": {
            "request_url": "https://api.arxivista.transx.tech/slack/events",
            "bot_events": [
                "app_mention",
                "message.channels"
            ]
        },
        "interactivity": {
            "is_enabled": true,
            "request_url": "https://api.arxivista.transx.tech"
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": false,
        "token_rotation_enabled": false
    }
}
```   


## API key(環境変数)について
バックエンドのrootディレクトリに `.env` ファイルを作成し、以下のように記述する。(.env.sampleを参考に)
```
OpenAI_API_KEY=""
```
OpenAIのAPIキーはスプレッドシートに記載されている。  
firebase_secret.jsonを.envと同じ階層に作成(asana参照)  
フロントエンドのrootディレクトリ `.env.local` ファイルも作成。  

### PUTリクエストの送り方
settings.pyファイルにてAPIキーを取得しているため、以下の方法でリクエスト可能  (Swagger参照)  
ex) 
```
curl -X 'PUT' \
  'http://localhost:8000/process_pdf/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://arxiv.org/abs/2310.03063"
}'
```
```
curl -X 'PUT' \
  'http://localhost:8000/ask_question/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "arxiv_id": "2310.03063",
  "question_text": "What is ..."
}'
```

## pytest
testsディレクトリにテストコードを書く
`docker-compose exec backend pytest`

## 開発ルール
mainブランチが最新。
asanaに割り当てられたタスクをブランチを切って開発  
ブランチ名はなんでも構いませんが、 `feature/タスク概要` が良いかも  
PRは1人以上のレビューを受けてApproveされてからマージ
プロジェクト内のコードは.editorconfig に従うこと
marge方法は`Squash and merge`を使用すること
