from firebase_admin import firestore
from typing import Optional

firestore_db = firestore.client()


def upsert_auth_token(bot_id: str, workspace_id: str, bot_token: str) -> None:
    if bot_token is None:
        return

    doc_ref = firestore_db.document(f"oauth_token/{bot_id}-{workspace_id}")
    doc_ref.set({"bot_token": bot_token}, merge=True)


def find_auth_token(bot_id: str, workspace_id: str) -> Optional[str]:
    doc_ref = firestore_db.document(f"oauth_token/{bot_id}-{workspace_id}")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()['bot_token']
    else:
        print(f'Not found for token: {workspace_id}')
        return None
