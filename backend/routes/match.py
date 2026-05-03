from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import compare_with_job

router = APIRouter()

class MatchRequest(BaseModel):
    resume: str
    job: str

@router.post("/match")
def match(req: MatchRequest):
    return compare_with_job(req.resume, req.job)
