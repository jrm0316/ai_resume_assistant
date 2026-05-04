import os
import json
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from services.vector_store import search

load_dotenv()

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# CONFIG RAG
TOP_K_CONTEXT = 1  # usa só o melhor chunk


# =========================================================
# 🔵 FUNÇÃO AUXILIAR - LIMPAR JSON DO LLM
# =========================================================
def extract_json(text: str):
    try:
        # remove ```json ... ```
        text = re.sub(r"```json|```", "", text).strip()

        # pega só o JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        json_str = text[start:end]

        return json.loads(json_str)

    except Exception:
        return {
            "erro": "Falha ao gerar JSON",
            "raw": text
        }

# =========================================================
# 🔵 RAG CHAT
# =========================================================
def chat_with_resume(question: str):
    # 🔍 busca com score
    results = vectorstore.similarity_search_with_score(question, k=3)

    # 🔥 filtro por qualidade
    MAX_SCORE = 1.2
    filtered_results = [
        (doc, score) for doc, score in results if score <= MAX_SCORE
    ]

    # 🔥 pega só os melhores
    top_docs = filtered_results[:2]

    # 🧠 monta contexto
    context = "\n".join([doc.page_content for doc, _ in top_docs])

    # 🧠 prompt melhorado
    prompt = f"""
Você é um assistente que responde perguntas com base no contexto abaixo.

Contexto:
{context}

Pergunta:
{question}

Responda de forma clara e objetiva.
Se não encontrar resposta no contexto, diga:
"Não encontrei informação relevante no documento."
"""

    # 🤖 chamada do modelo (ajusta conforme o seu)
    answer = llm.invoke(prompt)

    # 📦 retorno estruturado
    return {
        "answer": answer,
        "sources": [
            {
                "content": doc.page_content,
                "score": float(score)
            }
            for doc, score in top_docs
        ]
    }

# =========================================================
# 🔵 ANALISADOR DE CURRÍCULO
# =========================================================
def analyze_resume(text: str):
    text_lower = text.lower()

    pontos_fortes = []
    pontos_fracos = []
    sugestoes = []

    # 🔥 habilidades detectadas
    if "python" in text_lower:
        pontos_fortes.append("Experiência com Python")

    if "fastapi" in text_lower:
        pontos_fortes.append("Desenvolvimento de APIs com FastAPI")

    if "postgres" in text_lower or "sql" in text_lower:
        pontos_fortes.append("Experiência com banco de dados")

    if "rag" in text_lower or "ia" in text_lower:
        pontos_fortes.append("Experiência com Inteligência Artificial")

    # 🔴 faltas importantes
    if "docker" not in text_lower:
        pontos_fracos.append("Ausência de Docker")
        sugestoes.append("Adicionar Docker ao currículo")

    if "teste" not in text_lower:
        pontos_fracos.append("Falta de testes automatizados")
        sugestoes.append("Criar testes automatizados com pytest")

    if "aws" not in text_lower and "gcp" not in text_lower:
        pontos_fracos.append("Sem experiência com cloud")
        sugestoes.append("Adicionar experiência com AWS ou GCP")

    if "git" not in text_lower:
        pontos_fracos.append("Pouca evidência de uso de Git")
        sugestoes.append("Mencionar uso de Git e versionamento")

    # 🔥 nível (simples mas eficaz)
    if "anos" in text_lower:
        if "1 ano" in text_lower:
            nivel = "Júnior"
        elif "2 anos" in text_lower or "3 anos" in text_lower:
            nivel = "Pleno"
        else:
            nivel = "Sênior"
    else:
        nivel = "Pleno"

    return {
        "nivel": nivel,
        "pontos_fortes": pontos_fortes,
        "pontos_fracos": pontos_fracos,
        "sugestoes": sugestoes
    }
# =========================================================
# 🔵 COMPARAR CURRÍCULO COM VAGA
# =========================================================
def compare_with_job(resume: str, job: str):
    # 🔥 pesos (pode evoluir depois)
    weights = {
        "python": 30,
        "fastapi": 25,
        "docker": 20,
        "testes": 15,
        "aws": 10
    }

    resume_lower = resume.lower()
    job_lower = job.lower()

    match_score = 0

    pontos_fortes = []
    faltando_obrigatorio = []
    faltando_desejavel = []

    explicacao = []

    for skill, weight in weights.items():
        if skill in job_lower:
            if skill in resume_lower:
                match_score += weight
                pontos_fortes.append(skill)
                explicacao.append(f"{skill} (+{weight}%)")
            else:
                # 🔥 regra simples: obrigatório vs desejável
                if skill in ["python", "fastapi", "docker"]:
                    faltando_obrigatorio.append(skill)
                else:
                    faltando_desejavel.append(skill)

    # 🔥 limitar em 100
    match_score = min(match_score, 100)

    resumo = (
        f"Match baseado em pesos. Pontos fortes: {', '.join(pontos_fortes)}. "
        f"Faltando: {', '.join(faltando_obrigatorio + faltando_desejavel)}."
    )

    return {
        "match": match_score,
        "faltando_obrigatorio": faltando_obrigatorio,
        "faltando_desejavel": faltando_desejavel,
        "pontos_fortes": pontos_fortes,
        "explicacao": explicacao,
        "resumo": resumo
    }