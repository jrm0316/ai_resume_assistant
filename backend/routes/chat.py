from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import chat_with_resume
from services.ai_service import compare_documents

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    history: list = []

@router.post("/chat")
def chat(req: ChatRequest):
    result = compare_documents(
        req.question,
        req.history
    )
    return result #response