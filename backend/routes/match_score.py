from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import compare_with_job

router = APIRouter()


class MatchRequest(BaseModel):
    resume: str
    job: str


@router.post("/match-score")
def match_score(req: MatchRequest):

    result = compare_with_job(
        req.resume,
        req.job
    )

    return result