import os
import json
import re
from dotenv import load_dotenv
from services.vector_store import search

from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import CrossEncoder

load_dotenv()

# =========================================================
# 🤖 LLM
# =========================================================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# =========================================================
# 🧠 EMBEDDINGS + VECTOR STORE
# =========================================================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

VECTORSTORE_PATH = "storage/faiss_index"

# =========================================================
# 🔥 RERANKER (CrossEncoder)
# =========================================================
# reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# =========================================================
# 🔧 AUXILIAR - LIMPAR JSON
# =========================================================
def extract_json(text: str):
    try:
        text = re.sub(r"```json|```", "", text).strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        return json.loads(text[start:end])
    except Exception:
        return {
            "erro": "Falha ao gerar JSON estruturado",
            "raw": text
        }
# =========================================================
# 🔧 AUXILIAR - PEGAR FRASE RELEVANTE (🔥 OPÇÃO 2)
# =========================================================
def extract_relevant_snippet(text: str, question: str):
    import re

    sentences = re.split(r"[.!?]\s+", text)

    stopwords = {"o", "a", "os", "as", "de", "da", "do", "e", "é", "que"}
    question_words = [
        word for word in question.lower().split()
        if word not in stopwords
    ]

    best_sentence = ""
    best_score = 0

    for sentence in sentences:
        score = sum(
            1 for word in question_words
            if word in sentence.lower()
        )

        if score > best_score:
            best_score = score
            best_sentence = sentence

    return best_sentence.strip() if best_sentence else text[:150]

# =========================================================
# 🔧 AUXILIAR - PEGAR FRASE BASEADA NA RESPOSTA (🔥 MELHOR)
# =========================================================
def extract_snippet_by_answer(text: str, answer: str):
    import re

    sentences = re.split(r"[.!?]\s+", text)

    best_sentence = ""
    best_score = 0

    answer_words = answer.lower().split()

    for sentence in sentences:
        score = sum(
            1 for word in answer_words
            if word in sentence.lower()
        )

        if score > best_score:
            best_score = score
            best_sentence = sentence

    return best_sentence.strip() if best_sentence else answer
# =========================================================
# 🔵 RAG CHAT (🔥 versão avançada)
# =========================================================
def chat_with_resume(
    question: str,
    history=[]
):
    global vectorstore

    try:
        # 🔍 BUSCA NO VECTORSTORE (em memória)
        results = vectorstore.similarity_search_with_score(
            question,
            k=5
        )

        # =========================================================
        # 🔥 RERANK
        # =========================================================

        #pairs = []

        #for doc, score in results:
            #pairs.append([question, doc.page_content])

        #rerank_scores = reranker.predict(pairs)
        '''
        reranked_docs = sorted(
            zip(results, rerank_scores),
            key=lambda x: x[1],
            reverse=True
        )

        results = [item[0] for item in reranked_docs[:5]]'''

        if not results:
            return {
                "answer": "Nenhum documento encontrado.",
                "confidence": 0,
                "sources": []
            }

        # 🔥 RERANKING
        #pairs = [(question, doc.page_content) for doc, _ in results]
        #scores = reranker.predict(pairs)

        reranked = sorted(
            zip(results, scores),
            key=lambda x: x[1],
            reverse=True
        )

        # 🚨 PROTEÇÃO
        if not reranked:
            return {
                "answer": "Não encontrei informação relevante.",
                "confidence": 0,
                "sources": []
            }

        # 🔝 TOP DOCS
        top_k = 5
        top_docs = [
            item[0][0]
            for item in reranked[:top_k]
        ]

        top_scores = [
            item[1]
            for item in reranked[:top_k]
        ]
        # 🚨 PROTEÇÃO
        if len(top_scores) == 0:
            return {
                "answer": "Não encontrei informação relevante.",
                "confidence": 0,
                "sources": []
            }

        best_score = float(top_scores[0])

        # 🚨 FILTRO (ajustado para CrossEncoder)
        if best_score < -4:
            return {
                "answer": "Não encontrei informação relevante no documento.",
                "confidence": 0,
                "sources": []
            }

        # 🧠 CONTEXTO
        context = "\n".join([
            doc.page_content
            for doc in top_docs
        ])

        # =========================================================
        # 🔥 CONTEXTO DA CONVERSA
        # =========================================================

        conversation_context = ""

        for item in history:

            role = item.get("role", "")

            content = item.get("content", "")

            if role == "user":
                conversation_context += f"Usuário: {content}\n"

            elif role == "assistant":
                conversation_context += f"Assistente: {content}\n"

        # 🧠 PROMPT MELHORADO
        prompt = f"""
        Você é um assistente especialista em análise de documentos.

Use o histórico da conversa para entender o contexto.

Regras:
- Responda SOMENTE com base nos documentos
- Seja direto e objetivo
- Não invente informações
- Compare os documentos quando necessário
- Considere perguntas anteriores
- Se não souber diga:
"Não encontrei informação relevante no documento."

Histórico da conversa:
{conversation_context}

Contexto:
{context}

Pergunta atual:
{question}
        """

        # 🤖 LLM
        response = llm.invoke(prompt)
        answer = response.content if response else ""

        # 🚨 PROTEÇÃO
        if not answer:
            answer = "Não consegui gerar uma resposta."

        # 🔥 NORMALIZAÇÃO DE CONFIANÇA
        confidence = round((best_score + 10) / 20, 2)

        # 📦 RESPOSTA FINAL
        return {
            "answer": answer,
            "confidence": confidence,
        "sources": [
            {
                "source": doc.metadata.get(
                    "source",
                    "desconhecido"
                ),

                "page": doc.metadata.get(
                    "page",
                    "?"
                ),

                "snippet": extract_snippet_by_answer(
                    doc.page_content,
                    answer
                )[:200],

                "relevance": (
                    "Alta"
                    if float(score) > 1
                    else "Média"
                )
            }
            for doc, score in zip(top_docs, top_scores)
        ]    
        }
    except Exception as e:
        # 🚨 DEBUG (MUITO IMPORTANTE)
        print("ERRO NO CHAT:", str(e))

        return {
            "answer": "Erro ao processar a pergunta.",
            "confidence": 0,
            "sources": [],
            "error": str(e)
        }
# =========================================================
# 🔵 ANALYZE V2
# =========================================================
def analyze_resume(text: str):
    prompt = f"""
Você é um especialista em recrutamento e análise de currículos na área de tecnologia.

Analise o currículo abaixo e retorne um JSON com:

- nivel: (Júnior, Pleno ou Sênior)
- pontos_fortes: lista
- pontos_fracos: lista
- sugestoes: lista

Regras:
- Seja objetivo e técnico
- Não invente experiências que não estão no texto
- Baseie-se apenas no conteúdo fornecido

Currículo:
{text}
"""

    response = llm.invoke(prompt)
    content = response.content

    return extract_json(content)

def extract_skills(text: str):

    skills = [
        "python",
        "fastapi",
        "docker",
        "kubernetes",
        "postgresql",
        "mysql",
        "mongodb",
        "rag",
        "llms",
        "langchain",
        "apis rest",
        "redis",
        "git",
        "aws",
        "azure",
        "gcp",
        "tensorflow",
        "pytorch",
        "ci/cd"
    ]

    found = []

    text_lower = text.lower()

    for skill in skills:

        if skill in text_lower:
            found.append(skill)

    return found
# =========================================================
# 🔵 COMPARE V2
# =========================================================
def compare_with_job(resume: str, job: str):

    # =========================
    # EXTRAÇÃO DE SKILLS
    # =========================

    resume_skills = extract_skills(resume)

    job_skills = extract_skills(job)

    # =========================
    # MATCH
    # =========================

    matched = [
        skill for skill in job_skills
        if skill in resume_skills
    ]

    missing = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    # =========================
    # SCORE REAL
    # =========================

    if len(job_skills) == 0:
        match_score = 0
    else:
        match_score = int(
            (len(matched) / len(job_skills)) * 100
        )

    # =========================
    # LLM ANALYSIS
    # =========================

    prompt = f"""
Você é um recrutador técnico.

Faça uma análise objetiva do candidato.

Skills encontradas:
{matched}

Skills faltando:
{missing}

Explique:
- nível do candidato
- aderência à vaga
- principais gaps
- próximos passos para melhorar
"""

    response = llm.invoke(prompt)

    analysis = response.content

    return {
        "match": match_score,
        "strengths": matched,
        "missing": missing,
        "analysis": analysis
    }
# =========================================================
# 🔥 COMPARE DOCUMENTS (MULTI-DOC ANALYSIS)
# =========================================================
def compare_documents(
    question: str,
    history=[]
):

    # =========================
    # BUSCA
    # =========================

    results = vectorstore.similarity_search_with_score(
        question,
        k=5
    )
    # =========================================================
    # 🔥 RERANK
    # =========================================================

    #pairs = []

    #for doc, score in results:
    #    pairs.append([question, doc.page_content])

    #rerank_scores = reranker.predict(pairs)
    '''
    reranked_docs = sorted(
        zip(results, rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )
    
    results = [item[0] for item in reranked_docs[:8]]
    '''
    # =========================================================
    # 🔥 BOOST PARA CURRÍCULO
    # =========================================================

    boost_words = [
        "candidato",
        "currículo",
        "curriculo",
        "ele",
        "experiência",
        "habilidades",
        "skills"
    ]

    question_lower = question.lower()

    boost_resume = any(
        word in question_lower
        for word in boost_words
    )

    if not results:
        return {
            "answer": "Nenhum documento encontrado.",
            "confidence": 0,
            "sources": []
        }

    # =========================
    # RERANK
    # =========================

    #pairs = [
     #   (question, doc.page_content)
     #   for doc, _ in results
    #]

    #rerank_scores = reranker.predict(pairs)

    reranked_data = []

    for (doc, vector_score), rerank_score in zip(results, rerank_scores):

        final_score = float(rerank_score)

        source = doc.metadata.get("source", "").lower()

        # boost currículo
        if boost_resume and "curriculo" in source:
            final_score += 5

        reranked_data.append(
            ((doc, vector_score), final_score)
        )

    reranked = sorted(
        reranked_data,
        key=lambda x: x[1],
        reverse=True
    )

    # =========================
    # TOP DOCS
    # =========================

    # =========================================================
    # 🔥 GARANTE MÚLTIPLOS DOCUMENTOS
    # =========================================================

    top_results = []
    seen_sources = set()

    for item in reranked:

        (doc, vector_score), rerank_score = item

        source = doc.metadata.get("source")

        # evita repetir sempre o mesmo arquivo
        if source not in seen_sources:

            seen_sources.add(source)

            top_results.append(item)

        # pega no máximo 4 documentos
        if len(top_results) >= 4:
            break

    unique_results = []
    seen = set()

    for item in top_results:

        (doc, vector_score), rerank_score = item

        key = (
            doc.metadata.get("source"),
            doc.page_content[:100]
        )

        if key not in seen:
            seen.add(key)
            unique_results.append(item)

    top_results = unique_results

    best_score = float(top_results[0][1])

    # 🚨 reduzimos agressividade

    # =========================
    # CONTEXTO
    # =========================

    context = ""

    for item in top_results:

        (doc, vector_score), rerank_score = item

        source = doc.metadata.get("source", "Desconhecido")
        page = doc.metadata.get("page", 1)

        context += f"""
Arquivo: {source}
Página: {page}

Conteúdo:
{doc.page_content}

-------------------
"""

    # =========================
    # PROMPT
    # =========================

    prompt = f"""
Você é um especialista em análise de currículos e vagas.

Responda de forma:
- objetiva
- curta
- técnica
- sem repetir informações

Use SOMENTE o contexto fornecido.

Pergunta:
{question}

Contexto:
{context}

Regras:
- Não invente informações
- Não repita tecnologias
- Se uma skill aparece nos dois documentos, diga apenas uma vez
- Se faltar informação, diga claramente
- Responda em no máximo 10 linhas
"""

    # =========================
    # LLM
    # =========================

    response = llm.invoke(prompt)

    answer = response.content

    # =========================
    # SOURCES
    # =========================

    sources = []

    for item in top_results:

        (doc, vector_score), rerank_score = item

        sources.append({
            "source": doc.metadata.get("source", "Desconhecido"),
            "page": doc.metadata.get("page", 1),
            "snippet": doc.page_content[:300],
            "relevance": "Alta" if rerank_score > 0.3 else "Média"
        })

    # =========================
    # RETURN
    # =========================

    return {
        "answer": answer,
        "confidence": round((best_score + 10) / 20, 2),
        "sources": sources
    }

# =========================================================
# SAVE VECTORSTORE
# =========================================================

VECTORSTORE_PATH = "storage/faiss_index"

# =========================================================
# LOAD VECTORSTORE
# =========================================================

if os.path.exists(VECTORSTORE_PATH):

    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

else:

    vectorstore = None

def update_vectorstore(documents):

    global vectorstore

    if vectorstore is None:

        vectorstore = FAISS.from_documents(
            documents,
            embeddings
        )

    else:

        vectorstore.add_documents(documents)

    vectorstore.save_local(VECTORSTORE_PATH)

# =========================================================
# 🔥 SKILL EXTRACTION
# =========================================================

TECH_SKILLS = [
    "python",
    "fastapi",
    "docker",
    "kubernetes",
    "rag",
    "llm",
    "llms",
    "postgresql",
    "mysql",
    "sql",
    "aws",
    "azure",
    "gcp",
    "redis",
    "mongodb",
    "api",
    "apis",
    "rest",
    "machine learning",
    "langchain",
    "faiss",
    "streamlit",
    "pandas"
]

def extract_skills(text: str):

    text_lower = text.lower()

    found = []

    for skill in TECH_SKILLS:

        if skill in text_lower:
            found.append(skill)

    return list(set(found))

# =========================================================
# 🔥 REAL MATCH SCORE
# =========================================================

def calculate_match(resume_text: str, job_text: str):

    resume_skills = extract_skills(resume_text)

    job_skills = extract_skills(job_text)

    matched = [
        skill
        for skill in job_skills
        if skill in resume_skills
    ]

    missing = [
        skill
        for skill in job_skills
        if skill not in resume_skills
    ]

    if len(job_skills) == 0:
        score = 0
    else:
        score = int(
            (len(matched) / len(job_skills)) * 100
        )

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }

# =========================================================
# 🔥 INTERVIEW SIMULATOR
# =========================================================

def generate_questions(resume_text: str):

    prompt = f"""
Você é um entrevistador técnico.

Com base no currículo abaixo,
gere 5 perguntas técnicas para entrevista.

Currículo:
{resume_text}

As perguntas devem avaliar:
- Python
- APIs
- FastAPI
- Banco de dados
- IA/RAG/LLMs

Responda apenas com as perguntas.
"""

    response = llm.invoke(prompt)

    questions = response.content.split("\n")

    questions = [
        q.strip("- ").strip()
        for q in questions
        if q.strip()
    ]

    return {
        "questions": questions
    }


# =========================================================
# 🔥 EVALUATE ANSWER
# =========================================================

def evaluate_answer(question: str, answer: str):

    prompt = f"""
Você é um avaliador técnico.

Avalie a resposta abaixo.

Pergunta:
{question}

Resposta do candidato:
{answer}

Analise:
- clareza
- conhecimento técnico
- profundidade
- objetividade

Dê:
- nota de 0 a 10
- pontos fortes
- pontos fracos
- feedback final

Responda de forma objetiva.
"""

    response = llm.invoke(prompt)

    return {
        "evaluation": response.content
    }
