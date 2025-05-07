from .repository.auth_token import upsert_auth_token
from .repository.oauth_state import create_oauth_state, find_oauth_state, delete_oauth_state

from fastapi import Depends, HTTPException, status, APIRouter

from .models import request_models
from .models.oauth_state import OAuthState
from slack_sdk import WebClient

from . import settings


oauth_router = APIRouter()

# 環境変数から client_secret を保存する
client_secret = settings.SLACK_CLIENT_SECRET
# 環境変数から client_id を保存する
client_id = settings.SLACK_CLIENT_ID


# OAuth フローを開始するルート
@oauth_router.get("/begin_auth")
def pre_install():
    state = OAuthState()
    create_oauth_state(state)
    return f'<a href="https://slack.com/oauth/v2/authorize?client_id={client_id}&scope=channels:history,groups:history,im:history,mpim:history,chat:write,app_mentions:read&user_scope=&state={state.text}"><img alt="Add to Slack" height="40" width="139" src="https://platform.slack-edge.com/img/add_to_slack.png" srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x" /></a>'


@oauth_router.get("/finish_auth")
def post_install(auth_request: request_models.AuthReceive=Depends()):
    # リクエストパラメータから認可 code と state を取得する
    # Retrieve the auth code and state from the request params
    auth_code = auth_request.code
    received_state = auth_request.state

    # このリクエストにはトークンは不要なので空文字でもよい
    client = WebClient(token="")

    # state パラメータが最初に送信した時と同じであることを確認する
    state = find_oauth_state(received_state)
    if state is None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    delete_oauth_state(received_state)

    if state.is_expired:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if state.match(received_state):
        # Slack の認可トークンをリクエストする
        response = client.oauth_v2_access(
            client_id=client_id,
            client_secret=client_secret,
            code=auth_code
        )
    else:
        return "Invalid State"

    upsert_auth_token(settings.SLACK_BOT_ID, response['team']['id'], response['access_token'])
    # ユーザに認可が成功したことを知らせる
    return "Auth complete!"
