from firebase_admin import firestore
from typing import Optional


from ..models.oauth_state import OAuthState


firestore_db = firestore.client()


def create_oauth_state(state: OAuthState):
    doc_ref = firestore_db.collection("oauth_state").document(state.text)
    doc_ref.set(state.model_dump())


def find_oauth_state(state: str) -> Optional[OAuthState]:
    doc_ref = firestore_db.collection("oauth_state").document(state)
    doc = doc_ref.get()
    if doc.exists:
        return OAuthState(**doc.to_dict())
    else:
        return None


def delete_oauth_state(state: str):
    doc_ref = firestore_db.collection("oauth_state").document(state)
    doc_ref.delete()
