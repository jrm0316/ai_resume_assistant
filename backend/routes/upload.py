from typing import List

from fastapi import APIRouter, UploadFile, File
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from services.ai_service import update_vectorstore

router = APIRouter()

@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(
        ...,
        description="Upload multiple files"
    )
):

    all_documents = []

    for file in files:

        content = ""

        # =========================
        # PDF
        # =========================
        if file.filename.endswith(".pdf"):

            reader = PdfReader(file.file)

            for page_number, page in enumerate(reader.pages):

                text = page.extract_text()

                if text:

                    all_documents.append(
                        Document(
                            page_content=text,
                            metadata={
                                "source": file.filename,
                                "page": page_number + 1
                            }
                        )
                    )

        # =========================
        # TXT
        # =========================
        elif file.filename.endswith(".txt"):

            text = (await file.read()).decode("utf-8")

            all_documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": file.filename,
                        "page": 1
                    }
                )
            )

        else:
            return {
                "erro": f"Formato não suportado: {file.filename}"
            }

    # =========================
    # CHUNKING
    # =========================

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    final_chunks = splitter.split_documents(all_documents)

    # =========================
    # UPDATE VECTORSTORE
    # =========================

    update_vectorstore(final_chunks)

    return {
        "message": f"{len(files)} arquivos processados com sucesso",
        "chunks": len(final_chunks)
    }