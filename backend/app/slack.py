from sys import stderr
from asyncio import Lock
from expiringdict import ExpiringDict
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

# 英語での対応への分岐
slack_app = App(
    signing_secret=settings.SLACK_SIGNING_SECRET,
    authorize=authorize_callback
)


app_handler = AsyncSlackRequestHandler(slack_app)


"""

英語での処理 (/events エンドポイント)

"""
@slack_app.event("app_mention")
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
        adding_blocks_callback=lambda block: say(blocks=block, thread_ts=timestamp, text="画像を追加しました"),
        adding_message_callback=lambda text: say(text=text, thread_ts=timestamp),
        updating_message_callback=lambda text, ts: client.chat_update(
            channel=channel_id,
            ts=ts,
            text=text,
        )
    )

    try:
        generate_slack_reply(thread_class, reply_callback)
    except Exception as e:
        print(f"Failed to generate slack reply: {e}", file=stderr)
        await say(text="Error. Please try again later.", thread_ts=timestamp)


@slack_app.event("message")
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
        adding_blocks_callback=lambda block: say(blocks=block, thread_ts=thread_ts, text="画像を追加しました"),
        adding_message_callback=lambda text : say(text=text, thread_ts=thread_ts),
        updating_message_callback=lambda text, ts: client.chat_update(
            channel=channel_id,
            ts=ts,
            text=text,
        )
    )

    thread_class = messageClass.SlackThread(messages=msgs_class_list)
    try:
        generate_slack_reply(thread_class, reply_callback)
    except Exception as e:
        print(f"Failed to generate slack reply: {e}", file=stderr)
        await say(text="Error. Please try again later.", thread_ts=thread_ts)
# 重複した Event 受信の防止で過去の Event ID を保存する
# メモリ使用量を考えて一定時間で破棄する
processed_event_ids = ExpiringDict(max_len=1000, max_age_seconds=60 * 10)

lock = Lock()

@slack_api_router.post("/events")
async def endpoint(req: Request):
    event_id = (await req.json()).get("event_id")

    async with lock:
        if event_id in processed_event_ids:
            return
        processed_event_ids[event_id] = True

    return await app_handler.handle(req)
