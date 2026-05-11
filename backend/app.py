import streamlit as st
import requests
import time

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Career Assistant",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* =========================================================
🔥 GLOBAL
========================================================= */

html, body, [class*="css"] {
    background-color: #0e1117;
    color: #ffffff;
    font-family: 'Segoe UI', sans-serif;
}

/* =========================================================
🔥 MAIN CONTAINER
========================================================= */

.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: 1200px;
}

/* =========================================================
🔥 HEADER
========================================================= */

header {
    visibility: hidden;
}

/* =========================================================
🔥 SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

/* =========================================================
🔥 CHAT INPUT
========================================================= */

.stChatInputContainer {
    background-color: #161b22;
    border-radius: 12px;
    border: 1px solid #30363d;
    padding: 8px;
}

/* 🔥 input interno */
.stChatInputContainer textarea {
    background-color: #ffffff !important;
    color: #ffffff !important;
    border: none !important;
    font-size: 16px !important;
}

/* 🔥 placeholder */
.stChatInputContainer textarea::placeholder {
    color: #8b949e !important;
}

/* =========================================================
🔥 CHAT MESSAGES
========================================================= */

[data-testid="chat-message-container"] {
    background-color: #161b22;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 10px;
    border: 1px solid #30363d;
}

/* =========================================================
🔥 BUTTONS
========================================================= */

.stButton > button {
    background-color: #238636;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 16px;
    font-weight: 600;
}

.stButton > button:hover {
    background-color: #2ea043;
}

/* =========================================================
🔥 TEXT AREA
========================================================= */

textarea {
    background-color: #0d1117 !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #30363d !important;
}

/* =========================================================
🔥 METRICS
========================================================= */

[data-testid="metric-container"] {
    background-color: #161b22;
    border: 1px solid #30363d;
    padding: 15px;
    border-radius: 12px;
}

/* =========================================================
🔥 EXPANDERS
========================================================= */

.streamlit-expanderHeader {
    background-color: #161b22;
    border-radius: 10px;
}

/* =========================================================
🔥 SCROLLBAR
========================================================= */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #30363d;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "questions_count" not in st.session_state:
    st.session_state.questions_count = 0

if "uploaded_count" not in st.session_state:
    st.session_state.uploaded_count = 0

if "last_match" not in st.session_state:
    st.session_state.last_match = 0

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =========================================================
# API
# =========================================================

API_URL = "http://localhost:9000"

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🟢 System Status")

    st.success("LLM Online")
    st.success("RAG Active")
    st.success("FAISS Loaded")
    st.success("Embeddings Ready")
    st.success("API Connected")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("## 🔥 Detected Skills")

    detected_skills = [
        "Python",
        "FastAPI",
        "RAG",
        "LLMs",
        "PostgreSQL",
        "Docker"
    ]

    for skill in detected_skills:

        st.markdown(f"""
        <div style="
            background-color:#dff0e4;
            padding:10px;
            border-radius:10px;
            margin-bottom:8px;
            font-size:15px;
        ">
        {skill}
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# DASHBOARD
# =========================================================

col1, col2, col3 = st.columns(
    [1, 1, 1],
    gap="small"
)

with col1:
    st.metric(
        "📄 Arquivos",
        st.session_state.uploaded_count
    )

with col2:
    st.metric(
        "💬 Perguntas",
        st.session_state.questions_count
    )

with col3:
    st.metric(
        "🔥 Último Match",
        f"{st.session_state.last_match}%"
    )

# =========================================================
# TITLE
# =========================================================

st.title("🚀 AI Career Assistant")

st.caption(
    "Sistema inteligente de análise de currículos com IA, RAG e LLMs"
)

# =========================================================
# 🔥 DOCUMENTOS CARREGADOS
# =========================================================

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

if st.session_state.uploaded_files:

    st.markdown("### 📂 Documentos carregados")

    cols = st.columns(len(st.session_state.uploaded_files))

    for i, file in enumerate(st.session_state.uploaded_files):

        with cols[i]:
            st.success(file)

# =========================================================
# UPLOAD FILES
# =========================================================

uploaded_files = st.file_uploader(
    "📤 Envie currículos e vagas",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if st.button("Enviar arquivos"):

    if uploaded_files:

        files = []

        for file in uploaded_files:

            files.append(
                (
                    "files",
                    (
                        file.name,
                        file.getvalue(),
                        file.type
                    )
                )
            )

        res = requests.post(
            f"{API_URL}/upload",
            files=files
        )

        if res.status_code == 200:
            for file in uploaded_files:
                st.session_state.uploaded_files.append(file.name)

            st.session_state.uploaded_count += len(uploaded_files)

            st.success(
                f"{len(uploaded_files)} documento(s) enviado(s)!"
            )

        else:

            st.error("Erro ao enviar arquivos")

# =========================================================
# TABS
# =========================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat",
    "📄 CV",
    "🎯 Match",
    "🧠 Entrevista",
    "📊 Match Score"
])

# =========================================================
# CHAT
# =========================================================

with tab1:

    for msg in st.session_state.chat_history:

        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("Digite uma pergunta...")

    if question:

        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        st.session_state.questions_count += 1

        res = requests.post(
            f"{API_URL}/chat",
            json={
                "question": question,
                "history": st.session_state.chat_history[-5:]
            }
        )

        if res.status_code == 200:

            data = res.json()

            answer = data["answer"]

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })

            with st.chat_message("assistant"):

                # 🔥 loading
                with st.spinner("🤖 Pensando..."):

                    message_placeholder = st.empty()

                    full_response = ""

                    # 🔥 typing effect
                    for chunk in answer.split():

                        full_response += chunk + " "

                        message_placeholder.markdown(
                            full_response + "▌"
                        )

                        time.sleep(0.03)

                    # 🔥 resposta final
                    message_placeholder.markdown(full_response)

                # confiança
                confidence = data.get("confidence", 0)

                normalized = max(
                    min((confidence + 15) / 15, 1),
                    0
                )

                st.progress(normalized)

                st.caption(
                    f"Confiança: {round(confidence, 2)}"
                )

                if data.get("sources"):

                    st.markdown("### 📚 Fontes")

                    shown = set()

                    for src in data["sources"]:

                        unique_key = (
                            src["source"],
                            src["page"]
                        )

                        if unique_key in shown:
                            continue

                        shown.add(unique_key)

                        with st.expander(
                            f"📄 {src['source']} - Página {src['page']}"
                        ):

                            st.write(src["snippet"])

                            st.caption(
                                f"Relevância: {src['relevance']}"
                            )

        else:

            st.error(f"Erro na API: {res.status_code}")

            st.text(res.text)

# =========================================================
# ANALYZE CV
# =========================================================

with tab2:

    st.header("📄 Analisar Currículo")

    resume = st.text_area(
        "Cole seu currículo",
        key="cv_analyze"
    )

    if st.button("Analisar"):

        if resume:

            res = requests.post(
                f"{API_URL}/analyze",
                json={"resume": resume}
            )

            if res.status_code == 200:

                data = res.json()

                st.subheader("Nível")
                st.write(data.get("nivel"))

                st.subheader("Pontos Fortes")

                for item in data.get("pontos_fortes", []):
                    st.write(f"✅ {item}")

                st.subheader("Pontos Fracos")

                for item in data.get("pontos_fracos", []):
                    st.write(f"⚠️ {item}")

                st.subheader("Sugestões")

                for item in data.get("sugestoes", []):
                    st.write(f"💡 {item}")

            else:

                st.error(f"Erro na API: {res.status_code}")

# =========================================================
# MATCH
# =========================================================

with tab3:

    st.header("🎯 Comparar com vaga")

    resume = st.text_area(
        "Currículo",
        key="cv_match"
    )

    job = st.text_area(
        "Descrição da vaga",
        key="job_match"
    )

    if st.button("Comparar"):

        if resume and job:

            res = requests.post(
                f"{API_URL}/match",
                json={
                    "resume": resume,
                    "job": job
                }
            )

            if res.status_code == 200:

                data = res.json()

                st.subheader("Match")

                st.metric(
                    "Compatibilidade",
                    f"{data.get('match')}%"
                )

                st.subheader("Pontos Fortes")

                for item in data.get("pontos_fortes", []):
                    st.write(f"✅ {item}")

                st.subheader("Faltando")

                for item in data.get("faltando", []):
                    st.write(f"❌ {item}")

                st.subheader("Análise")

                st.write(data.get("analise"))

            else:

                st.error(f"Erro na API: {res.status_code}")

# =========================================================
# INTERVIEW
# =========================================================

with tab4:

    st.header("🧠 Simulador de Entrevista")

    resume = st.text_area("Cole seu currículo")

    if st.button("Gerar perguntas"):

        res = requests.post(
            f"{API_URL}/interview/questions",
            json={"resume": resume}
        )

        if res.status_code == 200:

            data = res.json()

            questions = data.get("questions", [])

            st.session_state["questions"] = questions

        else:

            st.error(f"Erro na API: {res.status_code}")

    if "questions" in st.session_state:

        for i, q in enumerate(
            st.session_state["questions"]
        ):

            st.subheader(f"Pergunta {i+1}")

            st.write(q)

            answer = st.text_area(
                f"Resposta {i}",
                key=f"ans_{i}"
            )

            if st.button(f"Avaliar {i}"):

                res = requests.post(
                    f"{API_URL}/interview/evaluate",
                    json={
                        "question": q,
                        "answer": answer
                    }
                )

                result = res.json()

                st.write(
                    f"Nota: {result.get('nota')}"
                )

                st.write(
                    "Feedback:",
                    result.get("feedback")
                )

# =========================================================
# MATCH SCORE
# =========================================================

with tab5:

    st.header("🔥 Match Score")

    resume_text = st.text_area(
        "Currículo",
        height=250,
        key="match_resume"
    )

    job_text = st.text_area(
        "Vaga",
        height=250,
        key="match_job"
    )

    if st.button("Calcular Match"):

        res = requests.post(
            f"{API_URL}/match-score",
            json={
                "resume": resume_text,
                "job": job_text
            }
        )

        if res.status_code == 200:

            data = res.json()

            st.session_state.last_match = data["match"]

            st.metric(
                "Match",
                f"{data['match']}%"
            )

            st.progress(data["match"] / 100)

            st.subheader("✅ Pontos Fortes")

            for item in data["strengths"]:
                st.success(f"✅ {item}")

            st.subheader("⚠️ Faltando")

            for item in data["missing"]:
                st.warning(f"⚠️ {item}")

            st.subheader("🧠 Análise")

            st.info(data["analysis"])

        else:

            st.error("Erro ao calcular match")