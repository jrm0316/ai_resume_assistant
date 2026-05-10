from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import generate_questions, evaluate_answer

router = APIRouter()

class ResumeRequest(BaseModel):
    resume: str

class AnswerRequest(BaseModel):
    question: str
    answer: str

@router.post("/interview/questions")
def questions(req: ResumeRequest):
    return generate_questions(req.resume)

@router.post("/interview/evaluate")
def evaluate(req: AnswerRequest):
    return evaluate_answer(req.question, req.answer)