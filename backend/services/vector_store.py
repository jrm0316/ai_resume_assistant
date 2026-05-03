import os
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# onde o índice será salvo
DB_PATH = "db"

# embeddings (modelo leve e bom)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================================================
# 🔵 CRIAR ÍNDICE
# =========================================================
def create_index(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=80,
        chunk_overlap=10,
        separators=["\n\n", "\n", ".", " "]
    )

    documents = splitter.create_documents([text])

    db = FAISS.from_documents(documents, embeddings)
    db.save_local(DB_PATH)

    return {"status": "Index criado com sucesso"}


# =========================================================
# 🔵 CARREGAR ÍNDICE
# =========================================================
def load_index():
    if not os.path.exists(DB_PATH):
        raise Exception(" Índice não encontrado. Faça upload primeiro.")

    return FAISS.load_local(
        DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


# =========================================================
# 🔵 BUSCA (COM SCORE)
# =========================================================
def search(query, k=5):
    db = load_index()

    results = db.similarity_search_with_score(query, k=k)

    print("\n===== DEBUG SEARCH =====")
    print("TIPO:", type(results))
    print("RESULTS:", results)

    MAX_SCORE = 0.8

    fixed_results = []

    for item in results:
        if isinstance(item, tuple):
            doc, score = item
            score = float(score)

            # filtra por relevância
            if score <= MAX_SCORE:
                fixed_results.append((doc, score))
        else:
            print(" ERRO: veio string ->", type(item))
            fixed_results.append((item, 0.0))

    # fallback inteligente (isso evita resposta vazia)
    if not fixed_results:
        print(" Nenhum resultado passou no filtro. Usando resultados originais.")
        return [(doc, float(score)) for doc, score in results]

    return fixed_results