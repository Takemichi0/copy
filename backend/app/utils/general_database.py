# import firebase_admin
from firebase_admin import auth, db, storage
# cred = credentials.Certificate("./././firebase_secret.json")
# firebase_admin.initialize_app(cred, {
#     'databaseURL': ''
# })

from firebase_admin import firestore
firestore_db = firestore.client()
bucket = storage.bucket()

def set_custom_claim(uid, slack_id):
    # ユーザーとslackのidを紐付ける
    custom_claims = {'slackId': slack_id}
    auth.set_custom_user_claims(uid, custom_claims)

def push_db(slack_id, channel_id, thread_ts, message):
    ref = db.reference(f'history/{slack_id}/{channel_id}/{thread_ts}')
    text_list = ref.get() or []
    text_list.append(message)
    ref.set(text_list)


def fetch_db(slack_id, channel_id, thread_ts):
    ref = db.reference(f'history/{slack_id}/{channel_id}/{thread_ts}')
    return ref.get()


def push_arxiv_data(id, summarize):
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc_ref.set({'summarize': summarize})

def fetch_arxiv_data(id):
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()['summarize']
    else:
        print(f'No document found for id: {id}')
        return None

def push_bot_token(id, summarize):
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc_ref.set({'summarize': summarize})

def upload_image(id, image) -> str:
    # 画像をアップロードしてURLを返す
    blob = bucket.blob(image)
    blob.upload_from_filename(image)
    blob.make_public()
    return blob.public_url

def upload_image_to_firestore(id, image: [str]) -> None:
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc_ref.set({'images': image}, merge=True)

def fetch_image(id):
    doc_ref = firestore_db.collection('arxiv').document(id)
    doc = doc_ref.get()
    if doc.exists:
        doc_dict = doc.to_dict()
        return doc_dict.get('images', None)
    else:
        print(f'No document found for id: {id}')
        return None


# if __name__ == "__main__":
    # push_db("slack_id", "channel_id", "thread_ts", "message21")
    # print(fetch_db("slack_id", "channel_id", "thread_ts"))
    # push_arxiv_data("2106.00001", "summarize")
    # print(fetch_arxiv_data("2106.00002"))
