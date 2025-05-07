from pydantic import BaseModel, HttpUrl


class ArxivURL(BaseModel):
    url: str  # arxivのURLをバリデーションするための型


class Question(BaseModel):
    arxiv_id: str
    question_text: str

class AuthReceive(BaseModel):
    code: str
    state: str
