from fastapi import APIRouter, Request
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp as App
from slack_bolt.authorization import AuthorizeResult
from .repository.auth_token import find_auth_token
from .message_processing import generate_slack_reply
from .models import message as messageClass
from .models.reply import ReplyCallback
from . import settings

slack_app = None

# 優先度低(env入れる)
slack_api_router = APIRouter(
    prefix="/slack",
)

async def authorize_callback(enterprise_id: str, team_id: str):
    token = find_auth_token(settings.SLACK_BOT_ID, team_id)
    if token is None:
        raise Exception("Invalid workspace")

    return AuthorizeResult(
        enterprise_id=enterprise_id,
        team_id=team_id,
        bot_token=token,
        bot_id=settings.SLACK_BOT_ID,
    )

# 日本語での対応への分岐
slack_app_jap = App(
    signing_secret=settings.SLACK_SIGNING_SECRET,
    authorize=authorize_callback
)


app_handler_jap = AsyncSlackRequestHandler(slack_app_jap)


"""

日本語での処理 (/jap エンドポイント)

"""

@slack_app_jap.event("app_mention")
async def start_new_thread(body, say, logger, client):
    """
    メンションされたら発火
    """
    # メッセージの情報を取得
    logger.info(body)
    event = body.get("event")

    channel_id = event.get("channel")
    timestamp = event.get("ts")
    text = event.get("text")

    # SlackThreadクラスを作成、回答を取得
    msg_class = messageClass.SlackMessage(
        workspace_id=event.get("team"),
        slack_id=event.get("user"),
        channel_id=channel_id,
        thread_ts=messageClass.SlackThreadTimestamp(raw=timestamp),
        text=text,
    )
    thread_class = messageClass.SlackThread(messages=[msg_class])

    reply_callback = ReplyCallback(
        adding_message_callback=lambda text, block: say(text=text, thread_ts=timestamp, blocks=block),
        updating_message_callback=lambda text, block, ts: client.chat_update(
            channel=channel_id,
            ts=ts,
            text=text,
            blocks=block
        )
    )

    generate_slack_reply(thread_class, reply_callback)


@slack_app_jap.event("message")
async def handle_message(message, say, logger, client):
    """
    channelまたはthreadに新規メッセージが送られたら発火。
    """
    logger.info(message)
    thread_ts = message.get("thread_ts")
    channel_id = message.get("channel")

    # チャンネルへの投稿の場合は処理をしない
    if not thread_ts:
        return

    # ボットの返信には反応しないように
    if "bot_id" in message or message.get("subtype") == "bot_message":
        return

    # 該当スレッドの過去msgを全て取得
    thread_msgs = await client.conversations_replies(
        channel=channel_id,
        ts=thread_ts,
    )

    # スレッドの大元のメッセージでメンションされていない場合は処理しない
    bot_id = await client.auth_test()
    bot_id = bot_id.get("user_id")
    parent_msg = thread_msgs.get("messages")[0].get("text")
    if bot_id not in parent_msg:
        print("bot_id not in parent_msg")
        return

    # SlackThreadクラスを作成
    msgs_class_list = []
    for message in thread_msgs.get("messages"):
        msgs_class_list.append(
            messageClass.SlackMessage(
                workspace_id=message.get("team"),
                slack_id=message.get("user"),
                channel_id=channel_id,
                thread_ts=messageClass.SlackThreadTimestamp(raw=thread_ts),
                text=message.get("text"),
            )
        )

    reply_callback = ReplyCallback(
        adding_message_callback=lambda text: say(text=text, thread_ts=thread_ts),
        updating_message_callback=lambda text, ts: client.chat_update(
            channel=channel_id,
            ts=ts,
            text=text,
        )
    )

    thread_class = messageClass.SlackThread(messages=msgs_class_list)
    generate_slack_reply(thread_class, reply_callback)


@slack_api_router.post("/jap")
async def endpoint(req: Request):
    return await app_handler_jap.handle(req)
