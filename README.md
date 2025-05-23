Here is the English translation of the main README for the Takemichi0/copy repository:

---

## What's this?

This tool automatically answers questions about the content of a provided PDF.  
Use case: When you want to quickly find specific information or data in long academic papers. Since it supports PDF uploads, it can also be used with instruction manuals or terms of service, etc.

## Related Links

- [Notion](https://www.notion.so/Arxiv-Interpreter-79c7f39d96614a569ab9588363840225)
- [Asana](https://app.asana.com/0/1205566635091585/1205566639320124)

## Infrastructure / Tech Stack

Google services are managed with the transX Google account.

- Frontend (/frontend)  
  Next.js, deployed to Vercel. (Firebase Auth)  
  Todo: Considering migration to Conoha or another provider since Vercel cannot be used for commercial purposes.

- Backend  
  Python (FastAPI), deployed to GCP (Cloud Run). (Uses Qdrant / Firebase as database)  
  Access restriction via Firebase Auth.

  [Architecture Diagram](https://www.notion.so/Arxiv-Interpreter-79c7f39d96614a569ab9588363840225)

## Environment Setup

Prepare a Docker environment in advance. (Installing the Docker app is recommended)

Build and start the Docker container (only needed the first time):  
`docker-compose up --build`

Start the Docker container:  
`docker-compose up`

The backend runs at `http://localhost:8000`  
The frontend runs at `http://localhost:3000`

Swagger:  
`http://localhost:8000/docs#/`

## How to Develop Locally

1. Create a new [Slack bot](https://api.slack.com/apps), then go to the portal page for the created app: `https://api.slack.com/apps/{app_id}`
2. Install the app to the transX workspace.
3. Overwrite the four or so app ids found at the bottom of Basic Information into the .env file.
4. In event subscriptions, add your local ngrok URL (for example, `http://....ngrok-free.tech/slack/events`). The last segment ("events") may differ depending on your environment.
5. Under event subscriptions, add `app_mention` and `message.channels` to "Subscribe to bot events".
6. Under OAuth & Permissions, add these Bot Token Scopes: `app_mentions:read`, `channels:history`, `chat:write`, `groups:history`, `im:history`, `mpim:history`.
7. The app manifest should look like the example below. If there are any discrepancies, correct the App manifest (example is for arxivista):

```json
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

## About API keys (environment variables)

Create a `.env` file in the backend root directory and write the following (refer to `.env.sample`):

```
OpenAI_API_KEY=""
```

The OpenAI API key is listed in a spreadsheet.  
Create `firebase_secret.json` in the same directory as `.env` (see Asana for details).  
Also create a `.env.local` file in the frontend root directory.

### How to Send PUT Requests

The API key is obtained in the settings.py file, so you can send requests as follows (see Swagger for details):

Example:
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

Write test code in the `tests` directory.  
Run tests with:  
`docker-compose exec backend pytest`

## Development Rules

- The main branch is up to date.
- Develop by creating branches for tasks assigned in Asana.
- Branch names can be anything, but `feature/short-description-of-task` is recommended.
- Pull requests must be reviewed and approved by at least one person before merging.
- Follow `.editorconfig` for code formatting.
- Use "Squash and merge" when merging.

---

Let me know if you need a translation for the frontend/README.md as well!
