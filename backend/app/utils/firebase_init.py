import base64

from .. import settings

import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": base64.b64decode(settings.FIREBASE_PRIVATE_KEY).decode().replace(r'\n', '\n'),
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "client_id": settings.FIREBASE_CLIENT_ID,
    "auth_uri": settings.FIREBASE_AUTH_URI,
    "token_uri": settings.FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_URL,
    "client_x509_cert_url": settings.FIREBASE_CLIENT_URL,
    "universe_domain": "googleapis.com",

})

firebase_admin.initialize_app(cred, {
        'databaseURL': settings.FIREBASE_DATABASE_URL,
        'storageBucket': settings.FIREBASE_STORAGE_BUCKET
})

def is_initialized():
    return "OK"
