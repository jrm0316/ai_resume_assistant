from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import analyze_resume

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    return analyze_resume(req.text)