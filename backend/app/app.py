import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import settings
from .utils import firebase_init
from .slack import slack_api_router
from .oauth import oauth_router


firebase_init.is_initialized()

app = FastAPI()

if settings.ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn="https://1eb39d8f6e7261d275bb0e4235786c24@o4506015945129984.ingest.sentry.io/4506015946440704",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://arxivista.transx.tech",
    "https://arxiv-questions.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth_router)
app.include_router(slack_api_router)

