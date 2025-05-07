from firebase_admin import firestore
from typing import Optional

from ..models.arxiv import VectorizationStatus


firestore_db = firestore.client()


def find_arxiv_vectorization_status(id: str) -> VectorizationStatus:
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc = doc_ref.get()
    if doc.exists:
        return VectorizationStatus(doc.to_dict()['vectorization_status'])
    else:
        return VectorizationStatus.NOT_STARTED


def update_arxiv_vectorization_status(id, vectorization_status: VectorizationStatus) -> None:
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc_ref.set({'vectorization_status': vectorization_status.value}, merge=True)
