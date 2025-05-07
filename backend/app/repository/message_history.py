from firebase_admin import firestore
from typing import Optional

from ..models.message import SlackMessage, SlackThread

firestore_db = firestore.client()


def upsert_message_history(thread: SlackThread):
    if len(thread.messages) == 0:
        return

    doc_ref = firestore_db.document(
        f"message_history/{thread.workspace_id}/{thread.channel_id}/{thread.thread_ts.as_firestore_path}")
    doc_ref.set({"messages": thread.messages_to_dict()}, merge=True)


def find_message_history(slack_id: str, channel_id: str, thread_ts: str) -> Optional[SlackMessage]:
    doc_ref = firestore_db.collection(
        f"message_history/{slack_id}/{channel_id}").document(thread_ts)
    doc = doc_ref.get()
    if doc.exists:
        return SlackMessage(**doc.to_dict())
    else:
        print(f'No document found for id: {thread_ts}')
        return None
