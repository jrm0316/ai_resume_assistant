from fastapi import APIRouter
from pydantic import BaseModel

from services.ai_service import compare_documents

router = APIRouter()

class CompareDocsRequest(BaseModel):
    question: str

@router.post("/compare-docs")
def compare_docs(req: CompareDocsRequest):

    return compare_documents(req.question)