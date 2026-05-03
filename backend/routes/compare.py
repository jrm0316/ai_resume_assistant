from fastapi import APIRouter
from pydantic import BaseModel
from services.ai_service import compare_with_job

router = APIRouter()

class CompareRequest(BaseModel):
    resume: str
    job: str

@router.post("/compare")
def compare(req: CompareRequest):
    return compare_with_job(req.resume, req.job)