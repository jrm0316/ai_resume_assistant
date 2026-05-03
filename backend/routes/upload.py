from fastapi import APIRouter, UploadFile, File
from services.vector_store import create_index
import io

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()

    filename = file.filename.lower()

    # 🔹 TXT
    if filename.endswith(".txt"):
        try:
            text = content.decode("utf-8")
        except:
            text = content.decode("latin-1")

    # 🔹 PDF
    elif filename.endswith(".pdf"):
        from pypdf import PdfReader

        pdf = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""

    # 🔹 DOCX
    elif filename.endswith(".docx"):
        from docx import Document

        doc = Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])

    else:
        return {"error": "Formato não suportado"}

    # 🔹 cria index
    create_index(text)

    return {"message": "Arquivo processado com sucesso"}