from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import chat_with_resume

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

@router.post("/chat")
def chat(req: ChatRequest):
    return chat_with_resume(req.question)