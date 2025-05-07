from pydantic import BaseModel

class ProcessArxivResponse(BaseModel):
    message: str
    status: str

class AskQuestionResponse(BaseModel):
    answer: str
    status: str # 不要かも
